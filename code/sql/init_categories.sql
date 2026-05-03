-- 初始化分类表和默认数据
-- 创建 categories 表
CREATE TABLE IF NOT EXISTS `categories` (
  `id` char(36) primary key,
  `name` varchar(100) NOT NULL,
  `parent_id` char(36) NULL,
  `sort_order` int DEFAULT 0,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX `idx_parent_id` (`parent_id`),
  FOREIGN KEY (`parent_id`) REFERENCES `categories`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 添加 knowledge 表的 category_id 外键列（如果不存在）
-- 注意：此脚本需要在数据库迁移时执行
-- ALTER TABLE `knowledge` ADD COLUMN `category_id` char(36) NULL AFTER `category`;
-- ALTER TABLE `knowledge` ADD INDEX `idx_category_id` (`category_id`);
-- ALTER TABLE `knowledge` ADD CONSTRAINT `fk_knowledge_category` FOREIGN KEY (`category_id`) REFERENCES `categories`(`id`) ON DELETE SET NULL;

-- 插入初始4个一级分类
INSERT INTO `categories` (`id`, `name`, `parent_id`, `sort_order`) VALUES
('cat-law', '法律法规', NULL, 1),
('cat-tech', '技术标准', NULL, 2),
('cat-case', '执法案例', NULL, 3),
('cat-policy', '政策文件', NULL, 4);

-- 为现有的 knowledge 记录根据 category 字符串映射到 category_id
-- UPDATE `knowledge` SET `category_id` = CASE `category`
--   WHEN 'law' THEN 'cat-law'
--   WHEN 'tech' THEN 'cat-tech'
--   WHEN 'case' THEN 'cat-case'
--   WHEN 'policy' THEN 'cat-policy'
-- END WHERE `category_id` IS NULL;