-- 为 qa_session 表添加 category 字段
-- 2026-04-26

ALTER TABLE qa_session
ADD COLUMN IF NOT EXISTS category VARCHAR(50) DEFAULT 'qa' AFTER title;

-- 为 category 列添加索引
ALTER TABLE qa_session
ADD INDEX idx_category (category);

-- 更新现有会话的 category 为 'qa'
UPDATE qa_session SET category = 'qa' WHERE category IS NULL OR category = '';
