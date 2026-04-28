"""
问答服务 (QA Service)
基于 RAG 架构实现智能问答，支持多轮对话 Session
"""
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

import anthropic

from app.config import get_settings
from app.database import get_db
from app.models.qa import QARecord, QAHotQuestion, QAHistory, QASession, QASessionMessage
from app.services.search_service import search_service

settings = get_settings()


class QAService:
    """问答服务"""

    def __init__(self):
        self.search_service = search_service
        self._llm_client = None

    @property
    def llm_client(self):
        """延迟初始化 LLM 客户端"""
        if self._llm_client is None:
            self._llm_client = anthropic.Anthropic(
                base_url=settings.anthropic_base_url,
                api_key=settings.anthropic_auth_token,
            )
        return self._llm_client

    # ============ Session 管理 ============

    def create_session(self, user_id: str, db: Session = None,
                       title: str = "新对话", category: str = "qa") -> Dict[str, Any]:
        """创建新会话"""
        if not db:
            return None

        try:
            session = QASession(
                id=str(uuid.uuid4()),
                user_id=user_id,
                title=title,
                category=category,
                is_active=1
            )
            db.add(session)
            db.commit()
            db.refresh(session)

            return {
                "id": session.id,
                "title": session.title,
                "category": session.category,
                "is_active": session.is_active,
                "created_at": session.created_at.isoformat() if session.created_at else "",
                "updated_at": session.updated_at.isoformat() if session.updated_at else ""
            }
        except Exception as e:
            print(f"创建会话失败: {e}")
            db.rollback()
            return None

    def get_sessions(self, user_id: str, db: Session = None) -> List[Dict[str, Any]]:
        """获取用户的所有会话"""
        if not db:
            return []

        try:
            sessions = db.query(QASession).filter(
                QASession.user_id == user_id
            ).order_by(desc(QASession.updated_at)).all()

            return [{
                "id": s.id,
                "title": s.title,
                "category": s.category,
                "is_active": s.is_active,
                "created_at": s.created_at.isoformat() if s.created_at else "",
                "updated_at": s.updated_at.isoformat() if s.updated_at else ""
            } for s in sessions]
        except Exception as e:
            print(f"获取会话列表失败: {e}")
            return []

    def get_session_detail(self, session_id: str, user_id: str, db: Session = None) -> Optional[Dict[str, Any]]:
        """获取会话详情（含消息历史）"""
        if not db:
            return None

        try:
            session = db.query(QASession).filter(
                QASession.id == session_id,
                QASession.user_id == user_id
            ).first()

            if not session:
                return None

            messages = db.query(QASessionMessage).filter(
                QASessionMessage.session_id == session_id
            ).order_by(QASessionMessage.id).all()

            return {
                "id": session.id,
                "title": session.title,
                "category": session.category,
                "is_active": session.is_active,
                "created_at": session.created_at.isoformat() if session.created_at else "",
                "updated_at": session.updated_at.isoformat() if session.updated_at else "",
                "messages": [{
                    "id": m.id,
                    "role": m.role,
                    "content": m.content,
                    "time": m.created_at.strftime("%Y-%m-%d %H:%M") if m.created_at else ""
                } for m in messages]
            }
        except Exception as e:
            print(f"获取会话详情失败: {e}")
            return None

    def delete_session(self, session_id: str, user_id: str, db: Session = None) -> bool:
        """删除会话（级联删除消息）"""
        if not db:
            return False

        try:
            session = db.query(QASession).filter(
                QASession.id == session_id,
                QASession.user_id == user_id
            ).first()

            if session:
                db.delete(session)
                db.commit()
                return True
        except Exception as e:
            print(f"删除会话失败: {e}")
            db.rollback()

        return False

    def clear_session_messages(self, session_id: str, user_id: str, db: Session = None) -> bool:
        """清除会话消息，保留会话"""
        if not db:
            return False

        try:
            # 确认会话属于该用户
            session = db.query(QASession).filter(
                QASession.id == session_id,
                QASession.user_id == user_id
            ).first()

            if not session:
                return False

            # 删除所有消息
            db.query(QASessionMessage).filter(
                QASessionMessage.session_id == session_id
            ).delete()

            # 更新会话标题为新对话
            session.title = '新对话'
            db.commit()
            return True
        except Exception as e:
            print(f"清除会话消息失败: {e}")
            db.rollback()
            return False

    def get_session_history(self, session_id: str, user_id: str, limit: int = 5, db: Session = None) -> List[Dict[str, str]]:
        """获取会话历史消息（用于 Prompt）"""
        if not db:
            return []

        try:
            messages = db.query(QASessionMessage).filter(
                QASessionMessage.session_id == session_id
            ).order_by(desc(QASessionMessage.created_at)).limit(limit * 2).all()

            # 倒序返回最近的 limit 轮对话
            result = []
            for m in reversed(messages):
                result.append({
                    "role": m.role,
                    "content": m.content
                })

            return result[-limit * 2:] if len(result) > limit * 2 else result
        except Exception as e:
            print(f"获取会话历史失败: {e}")
            return []

    # ============ 核心问答 ============

    def ask(self, question: str, user_id: Optional[str] = None,
            session_id: Optional[str] = None, db: Session = None,
            is_admin: bool = False) -> Dict[str, Any]:
        """
        处理问答（支持多轮对话）

        Args:
            question: 用户问题
            user_id: 用户ID
            session_id: 会话ID（可选，为空则不关联会话）
            db: 数据库会话
            is_admin: 是否管理员（管理员可查看所有知识）

        Returns:
            包含 answer, cards, related_questions, session_id 的字典
        """
        if not question.strip():
            return {
                "answer": "请输入问题",
                "cards": [],
                "related_questions": [],
                "session_id": session_id
            }

        user_id = user_id or "anonymous"

        # 如果有 session_id，关联或创建
        current_session_id = session_id
        current_category = "qa"  # 默认类别
        if current_session_id and db:
            # 验证 session 存在
            session = db.query(QASession).filter(
                QASession.id == current_session_id,
                QASession.user_id == user_id
            ).first()
            if not session:
                current_session_id = None
            else:
                current_category = session.category or "qa"

        # 如果没有 session，创建一个新会话
        if not current_session_id and db:
            new_session = self.create_session(user_id, db)
            if new_session:
                current_session_id = new_session["id"]

        # 获取对话历史
        history_messages = []
        if current_session_id:
            history_messages = self.get_session_history(current_session_id, user_id, limit=5, db=db)

        # 获取类目配置
        config = self.CATEGORY_CONFIG.get(current_category, self.CATEGORY_CONFIG["qa"])
        search_size = config["search_size"]

        # 1. 检索相关知识
        # 所有助手都优先使用向量搜索（语义搜索），失败则 fallback 到关键词搜索
        try:
            from app.services.embedding_service import embedding_service
            query_vector = embedding_service.encode_single(question)
            knowledge_ids = self.search_service.search_vector(
                query_vector=query_vector,
                user_id=user_id,
                limit=search_size,
                is_admin=is_admin
            )
            # 根据 ID 获取完整知识信息
            items = []
            for kid in knowledge_ids:
                doc = self.search_service.get_by_id(kid)
                if doc:
                    items.append({
                        "id": doc["id"],
                        "title": doc["title"],
                        "summary": doc.get("summary", ""),
                        "content": doc.get("content", ""),
                        "category": doc.get("category", ""),
                        "score": 0.9
                    })
            search_results = {"items": items, "total": len(items)}
        except Exception as e:
            print(f"向量搜索失败，fallback 到关键词搜索: {e}")
            search_results = self.search_service.search_keyword(
                query=question,
                user_id=user_id,
                page=1,
                page_size=search_size,
                is_admin=is_admin
            )

        # 2. 构建 Prompt（带历史和类别）
        prompt = self._build_prompt(question, search_results['items'], history_messages, current_category)

        # 3. 调用 LLM
        if search_results['total'] > 0:
            answer = self._call_llm(prompt)
        else:
            answer = "抱歉，知识库中没有找到与您问题相关的内容。请尝试换一种问法，或者联系管理员添加相关知识。"

        # 4. 生成推荐问题
        related_questions = self._generate_related_questions(search_results['items'])

        # 5. 构建知识卡片
        cards = []
        for item in search_results['items']:
            content = item.get('summary', '') or item.get('content', '')
            cards.append({
                "id": item['id'],
                "title": item['title'],
                "summary": content[:200],
                "type": item.get('category', ''),
                "category": item.get('category', ''),
                "source": item.get('source', ''),
                "confidence": min(95, int(item.get('score', 0) * 10 + 60))
            })

        # 6. 生成唯一 ID
        qa_id = str(uuid.uuid4())

        # 7. 保存记录
        if db:
            self._save_qa_record(db, qa_id, user_id, question, answer, search_results['items'])

            # 保存到会话消息（同一事务中保存，确保顺序）
            if current_session_id:
                try:
                    import time
                    ts = int(time.time() * 1000000)  # 微秒级时间戳
                    user_msg = QASessionMessage(
                        id=f"{ts}-user",
                        session_id=current_session_id,
                        role="user",
                        content=question
                    )
                    assistant_msg = QASessionMessage(
                        id=f"{ts+1}-assistant",
                        session_id=current_session_id,
                        role="assistant",
                        content=answer
                    )
                    db.add(user_msg)
                    db.add(assistant_msg)

                    # 更新会话标题为第一个问题
                    session = db.query(QASession).filter(QASession.id == current_session_id).first()
                    if session and session.title == '新对话':
                        session.title = question[:50] if len(question) <= 50 else question[:47] + '...'
                    db.commit()
                except Exception as e:
                    print(f"保存会话消息失败: {e}")
                    db.rollback()

        return {
            "id": qa_id,
            "question": question,
            "answer": answer,
            "cards": cards,
            "related_questions": related_questions,
            "session_id": current_session_id
        }

    def _save_session_message(self, db: Session, session_id: str, role: str, content: str):
        """保存会话消息"""
        try:
            msg = QASessionMessage(
                id=str(uuid.uuid4()),
                session_id=session_id,
                role=role,
                content=content
            )
            db.add(msg)
            db.commit()
        except Exception as e:
            print(f"保存会话消息失败: {e}")
            db.rollback()

    def _save_qa_record(self, db: Session, qa_id: str, user_id: str,
                        question: str, answer: str, search_items: List[Dict]):
        """保存问答记录到数据库"""
        try:
            record = QARecord(
                id=qa_id,
                user_id=user_id,
                question=question,
                answer=answer,
                search_results=[{"id": item['id'], "title": item['title']} for item in search_items]
            )
            db.add(record)

            self._update_hot_question(db, question)

            history = QAHistory(
                id=str(uuid.uuid4()),
                user_id=user_id,
                question=question,
                answer=answer
            )
            db.add(history)

            db.commit()
        except Exception as e:
            print(f"保存问答记录失败: {e}")
            db.rollback()

    def _update_hot_question(self, db: Session, question: str):
        """更新热门问题统计"""
        try:
            existing = db.query(QAHotQuestion).filter(
                QAHotQuestion.question == question
            ).first()

            if existing:
                existing.count += 1
            else:
                new_question = QAHotQuestion(
                    id=str(uuid.uuid4()),
                    question=question,
                    count=1
                )
                db.add(new_question)
        except Exception as e:
            print(f"更新热门问题失败: {e}")

    # ============ Category 专用配置 ============

    CATEGORY_CONFIG = {
        "qa": {
            "name": "知识问答助手",
            "system_prompt": "你是一个住建领域知识助手，专注于为用户提供准确、专业的政策法规和业务知识解答。",
            "search_size": 5,
        },
        "law_general": {
            "name": "执法智能助手",
            "system_prompt": "你是一个综合执法领域的智能助手，熟悉各类执法场景，能够根据相关法律法规提供专业的执法指导和建议。",
            "search_size": 5,
        },
        "supervise": {
            "name": "工程监管助手",
            "system_prompt": """你是一个工程监管领域的专家，专注于工程质量安全监督管理工作。
你熟悉以下方面的专业知识：
- 建设工程质量管理条例
- 安全生产管理条例
- 施工现场安全技术规范
- 工程质量验收标准
- 常见质量问题识别与处置（如混凝土强度不足、钢筋配置不规范、防水工程缺陷等）

当用户描述工程现场问题时，你应该：
1. 准确识别问题类型和严重程度
2. 引用相关法规、标准条款
3. 提供明确的处置建议和整改要求
4. 必要时给出预防措施建议""",
            "search_size": 8,  # 工程监管需要更多参考资料
        }
    }

    def _build_prompt(self, question: str, search_results: List[Dict],
                      history_messages: List[Dict] = None,
                      category: str = "qa") -> str:
        """构建 Prompt（支持对话历史和 category 差异化）"""
        config = self.CATEGORY_CONFIG.get(category, self.CATEGORY_CONFIG["qa"])
        system_prompt = config["system_prompt"]

        # 对话历史
        history_text = ""
        if history_messages:
            history_parts = []
            for msg in history_messages:
                role = "用户" if msg['role'] == 'user' else "助手"
                history_parts.append(f"{role}：{msg['content']}")
            history_text = "\n".join(history_parts)

        # 知识内容
        if not search_results:
            knowledge_text = "（知识库中暂无相关内容）"
        else:
            knowledge_parts = []
            for i, item in enumerate(search_results, 1):
                content = item.get('summary', '') or item.get('content', '')
                knowledge_parts.append(
                    f"【知识 {i}】\n标题：{item['title']}\n分类：{item.get('category', '通用')}\n内容：{content[:2000]}"
                )
            knowledge_text = "\n\n".join(knowledge_parts)

        if history_text:
            return f"""{system_prompt}

【对话历史】
{history_text}

【知识内容】
{knowledge_text}

【当前问题】
{question}

请根据对话历史和知识内容给出准确、专业的回答。如果知识内容不足以回答，请说明。"""
        else:
            return f"""{system_prompt}

【知识内容】
{knowledge_text}

【用户问题】
{question}

请根据知识内容给出准确、专业的回答。如果知识内容不足以回答，请说明。"""

    def _call_llm(self, prompt: str) -> str:
        """调用 LLM 生成回答"""
        try:
            message = self.llm_client.messages.create(
                model=settings.anthropic_default_haiku_model,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )

            for block in message.content:
                if hasattr(block, 'type') and block.type == 'text':
                    return block.text

            for block in message.content:
                if hasattr(block, 'text'):
                    return block.text

            return "抱歉，回答生成失败"

        except Exception as e:
            print(f"LLM 调用失败: {e}")
            return "服务暂时不可用，请稍后重试"

    def _generate_related_questions(self, search_results: List[Dict]) -> List[str]:
        """根据搜索结果生成推荐问题"""
        if not search_results:
            return []

        related = []
        for item in search_results[:3]:
            title = item.get('title', '')
            if title and title not in related:
                related.append(title)

        return related

    def rate(self, qa_id: str, rating: str, db: Session = None) -> bool:
        """评价问答结果"""
        if not db:
            return False

        try:
            record = db.query(QARecord).filter(QARecord.id == qa_id).first()
            if record:
                record.rating = rating
                db.commit()
                return True
        except Exception as e:
            print(f"评价保存失败: {e}")
            db.rollback()

        return False

    def get_stats(self, user_id: str, db: Session = None) -> Dict[str, Any]:
        """获取问答统计"""
        if not db:
            return self._get_mock_stats()

        try:
            total = db.query(func.count(QARecord.id)).filter(
                QARecord.user_id == user_id
            ).scalar() or 0

            today = date.today()
            today_count = db.query(func.count(QARecord.id)).filter(
                QARecord.user_id == user_id,
                func.date(QARecord.created_at) == today
            ).scalar() or 0

            total_ratings = db.query(func.count(QARecord.id)).filter(
                QARecord.user_id == user_id,
                QARecord.rating.isnot(None)
            ).scalar() or 0

            up_ratings = db.query(func.count(QARecord.id)).filter(
                QARecord.user_id == user_id,
                QARecord.rating == 'up'
            ).scalar() or 0

            satisfaction = int(up_ratings / total_ratings * 100) if total_ratings > 0 else 0

            return {
                "total_count": total,
                "today_count": today_count,
                "satisfaction": satisfaction
            }
        except Exception as e:
            print(f"获取统计失败: {e}")
            return self._get_mock_stats()

    def _get_mock_stats(self) -> Dict[str, Any]:
        return {
            "total_count": 0,
            "today_count": 0,
            "satisfaction": 0
        }

    def get_hot_questions(self, user_id: str = None, limit: int = 5, db: Session = None) -> List[Dict[str, Any]]:
        """获取热门问题"""
        if not db:
            return []

        try:
            questions = db.query(QAHotQuestion).order_by(
                desc(QAHotQuestion.count)
            ).limit(limit).all()

            return [{"question": q.question, "count": q.count} for q in questions]
        except Exception as e:
            print(f"获取热门问题失败: {e}")
            return []

    def get_history(self, user_id: str, limit: int = 10, db: Session = None) -> List[Dict[str, Any]]:
        """获取问答历史"""
        if not db:
            return []

        try:
            history_records = db.query(QAHistory).filter(
                QAHistory.user_id == user_id
            ).order_by(desc(QAHistory.created_at)).limit(limit).all()

            result = []
            for record in history_records:
                time_str = self._format_time(record.created_at)
                result.append({
                    "question": record.question,
                    "time": time_str
                })

            return result
        except Exception as e:
            print(f"获取历史记录失败: {e}")
            return []

    def _format_time(self, dt: datetime) -> str:
        """格式化时间"""
        if not dt:
            return ""

        now = datetime.now()
        diff = now - dt

        if diff.days == 0:
            return dt.strftime("%H:%M")
        elif diff.days == 1:
            return "昨天"
        elif diff.days < 7:
            return f"{diff.days}天前"
        else:
            return dt.strftime("%m-%d")


qa_service = QAService()
