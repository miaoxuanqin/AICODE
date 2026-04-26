-- ========================================
-- 问答助手数据库表
-- 创建时间：2026-04-25
-- ========================================

-- 问答记录表
CREATE TABLE IF NOT EXISTS `qa_records` (
    `id` VARCHAR(36) PRIMARY KEY COMMENT '问答记录ID',
    `user_id` VARCHAR(36) NOT NULL COMMENT '用户ID',
    `question` TEXT NOT NULL COMMENT '用户问题',
    `answer` TEXT NOT NULL COMMENT '回答内容',
    `search_results` JSON COMMENT '检索到的知识列表',
    `rating` VARCHAR(10) COMMENT '评价：up/down/null',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='问答记录表';

-- 热门问题表
CREATE TABLE IF NOT EXISTS `qa_hot_questions` (
    `id` VARCHAR(36) PRIMARY KEY COMMENT '问题ID',
    `question` VARCHAR(500) NOT NULL COMMENT '问题内容',
    `count` INT DEFAULT 1 COMMENT '问答次数',
    `last_updated` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
    INDEX `idx_count` (`count` DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='热门问题表';

-- 问答历史记录表
CREATE TABLE IF NOT EXISTS `qa_history` (
    `id` VARCHAR(36) PRIMARY KEY COMMENT '记录ID',
    `user_id` VARCHAR(36) NOT NULL COMMENT '用户ID',
    `question` VARCHAR(500) NOT NULL COMMENT '问题内容',
    `answer` TEXT COMMENT '回答内容',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='问答历史记录表';