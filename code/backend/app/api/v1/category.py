from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List, Union

from app.database import get_db
from app.models.user import User
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryItem, CategoryResponse
from core.rbac import get_current_user

router = APIRouter(prefix="/categories", tags=["分类管理"])


def build_tree(categories: List[Category], parent_id: Optional[Union[str, int]] = None) -> List[dict]:
    """将平铺的分类列表构建为树形结构"""
    tree = []
    for cat in categories:
        cat_parent = cat.parent_id
        if (parent_id is None and cat_parent is None) or (
            cat_parent is not None and str(cat_parent) == str(parent_id)
        ):
            node = {
                "id": cat.id,
                "name": cat.name,
                "parent_id": cat.parent_id,
                "level": cat.level,
                "description": cat.description,
                "sort_order": cat.sort_order,
                "children": build_tree(categories, cat.id)
            }
            tree.append(node)
    # 按 sort_order 排序
    tree.sort(key=lambda x: x.get("sort_order", 0))
    return tree


@router.get("", response_model=List[dict])
def list_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取分类树形列表"""
    categories = db.query(Category).order_by(Category.sort_order).all()
    return build_tree(categories)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个分类"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category


@router.post("", response_model=CategoryResponse)
def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建分类"""
    # 如果有父分类，验证父分类存在并计算层级
    parent_id = category_data.parent_id
    if parent_id is not None:
        parent = db.query(Category).filter(Category.id == parent_id).first()
        if not parent:
            raise HTTPException(status_code=400, detail="父分类不存在")
        level = parent.level + 1
    else:
        parent_id = None
        level = category_data.level

    category = Category(
        name=category_data.name,
        parent_id=parent_id,
        level=level,
        description=category_data.description,
        sort_order=category_data.sort_order
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新分类"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")

    if category_data.name is not None:
        category.name = category_data.name
    if category_data.parent_id is not None:
        # 防止将自己设为父分类
        if category_data.parent_id == category_id:
            raise HTTPException(status_code=400, detail="不能将自己设为父分类")
        # 验证父分类存在
        parent = db.query(Category).filter(Category.id == category_data.parent_id).first()
        if not parent:
            raise HTTPException(status_code=400, detail="父分类不存在")
        category.parent_id = category_data.parent_id
        category.level = parent.level + 1
    if category_data.level is not None:
        category.level = category_data.level
    if category_data.description is not None:
        category.description = category_data.description
    if category_data.sort_order is not None:
        category.sort_order = category_data.sort_order

    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除分类"""
    # 只有管理员可以删除分类
    if current_user.is_superuser != 1:
        raise HTTPException(status_code=403, detail="只有管理员可以删除分类")

    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")

    # 检查是否有子分类
    children = db.query(Category).filter(Category.parent_id == category_id).count()
    if children > 0:
        raise HTTPException(status_code=400, detail="该分类下有子分类，请先删除子分类")

    # 检查是否有知识关联（通过 category 字符串字段）
    from app.models.knowledge import Knowledge
    knowledge_count = db.query(Knowledge).filter(Knowledge.category == str(category_id)).count()
    if knowledge_count > 0:
        raise HTTPException(status_code=400, detail=f"该分类下有 {knowledge_count} 条知识，无法删除")

    db.delete(category)
    db.commit()
    return {"message": "删除成功"}