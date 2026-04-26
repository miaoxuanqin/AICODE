-- 用户、角色、权限系统数据库初始化脚本
-- 数据库: mydatabase

-- ============ 组织表 ============
CREATE TABLE IF NOT EXISTS organizations (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    parent_id CHAR(36),
    level VARCHAR(20) NOT NULL COMMENT '1=省级, 2=市县级, 3=区县级',
    path VARCHAR(255) NOT NULL COMMENT '路径便于查询，如 海南/海口市',
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES organizations(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============ 用户表 ============
CREATE TABLE IF NOT EXISTS users (
    id CHAR(36) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    full_name VARCHAR(100),
    org_id CHAR(36),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login_at DATETIME,
    FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE SET NULL,
    INDEX idx_username (username),
    INDEX idx_org_id (org_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============ 权限表 ============
CREATE TABLE IF NOT EXISTS permissions (
    id CHAR(36) PRIMARY KEY,
    code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    module VARCHAR(50) NOT NULL COMMENT 'knowledge/portal/config/system',
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_code (code),
    INDEX idx_module (module)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============ 角色表 ============
CREATE TABLE IF NOT EXISTS roles (
    id CHAR(36) PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_system BOOLEAN DEFAULT FALSE COMMENT '系统预置角色不可删除',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============ 角色-权限关联表 ============
CREATE TABLE IF NOT EXISTS role_permissions (
    id CHAR(36) PRIMARY KEY,
    role_id CHAR(36) NOT NULL,
    permission_id CHAR(36) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE,
    UNIQUE KEY uk_role_permission (role_id, permission_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============ 用户-角色关联表 ============
CREATE TABLE IF NOT EXISTS user_roles (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    role_id CHAR(36) NOT NULL,
    org_id CHAR(36) COMMENT 'NULL表示全局',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_role_org (user_id, role_id, org_id),
    INDEX idx_user_id (user_id),
    INDEX idx_role_id (role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============ 知识访问控制表 ============
CREATE TABLE IF NOT EXISTS knowledge_access (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36),
    role_id CHAR(36),
    org_id CHAR(36),
    access_type ENUM('public', 'org', 'category', 'private') NOT NULL DEFAULT 'public',
    target_id VARCHAR(100) COMMENT '分类ID或知识ID，NULL表示全部',
    permission ENUM('read', 'write', 'admin') NOT NULL DEFAULT 'read',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE CASCADE,
    INDEX idx_access_type (access_type),
    INDEX idx_user_id (user_id),
    INDEX idx_role_id (role_id),
    INDEX idx_org_id (org_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- 初始化数据
-- ============================================

-- 插入省级组织
INSERT INTO organizations (id, name, code, parent_id, level, path) VALUES
('a0000000-0000-0000-0000-000000000001', '海南省住房和城乡建设厅', 'HAINAN_PROVINCE', NULL, '1', '海南省');

-- 插入市县组织
INSERT INTO organizations (id, name, code, parent_id, level, path) VALUES
('b0000000-0000-0000-0000-000000000001', '海口市住房和城乡建设局', 'HAIKOU_CITY', 'a0000000-0000-0000-0000-000000000001', '2', '海南省/海口市'),
('b0000000-0000-0000-0000-000000000002', '三亚市住房和城乡建设局', 'SANYA_CITY', 'a0000000-0000-0000-0000-000000000001', '2', '海南省/三亚市');

-- 插入预置权限
INSERT INTO permissions (id, code, name, module, description) VALUES
-- 系统权限
('p0000001-0000-0000-0000-000000000001', 'system:user:list', '用户列表查看', 'system', '查看用户列表'),
('p0000001-0000-0000-0000-000000000002', 'system:user:read', '用户详情查看', 'system', '查看用户详细信息'),
('p0000001-0000-0000-0000-000000000003', 'system:user:create', '用户创建', 'system', '创建新用户'),
('p0000001-0000-0000-0000-000000000004', 'system:user:update', '用户更新', 'system', '更新用户信息'),
('p0000001-0000-0000-0000-000000000005', 'system:user:delete', '用户删除', 'system', '删除/禁用用户'),
('p0000001-0000-0000-0000-000000000006', 'system:role:list', '角色列表查看', 'system', '查看角色列表'),
('p0000001-0000-0000-0000-000000000007', 'system:role:read', '角色详情查看', 'system', '查看角色详细信息'),
('p0000001-0000-0000-0000-000000000008', 'system:role:create', '角色创建', 'system', '创建新角色'),
('p0000001-0000-0000-0000-000000000009', 'system:role:update', '角色更新', 'system', '更新角色信息'),
('p0000001-0000-0000-0000-000000000010', 'system:role:delete', '角色删除', 'system', '删除角色'),
('p0000001-0000-0000-0000-000000000011', 'system:permission:list', '权限列表查看', 'system', '查看所有权限'),
-- 知识模块权限
('p0000002-0000-0000-0000-000000000001', 'knowledge:search', '知识搜索', 'knowledge', '搜索知识内容'),
('p0000002-0000-0000-0000-000000000002', 'knowledge:read', '知识查看', 'knowledge', '查看知识详情'),
('p0000002-0000-0000-0000-000000000003', 'knowledge:create', '知识创建', 'knowledge', '创建知识条目'),
('p0000002-0000-0000-0000-000000000004', 'knowledge:update', '知识更新', 'knowledge', '更新知识内容'),
('p0000002-0000-0000-0000-000000000005', 'knowledge:delete', '知识删除', 'knowledge', '删除知识条目'),
('p0000002-0000-0000-0000-000000000006', 'knowledge:approve', '知识审批', 'knowledge', '审批知识条目'),
-- 门户模块权限
('p0000003-0000-0000-0000-000000000001', 'portal:config', '门户配置', 'portal', '配置搜索门户'),
('p0000003-0000-0000-0000-000000000002', 'portal:view', '门户查看', 'portal', '查看门户配置');

-- 插入预置角色
INSERT INTO roles (id, code, name, description, is_system) VALUES
('r0000001-0000-0000-0000-000000000001', 'platform_admin', '平台管理员', '系统最高权限，拥有所有功能权限', TRUE),
('r0000001-0000-0000-0000-000000000002', 'provincial_admin', '省厅管理员', '省级知识管理权限', TRUE),
('r0000001-0000-0000-0000-000000000003', 'city_admin', '市县管理员', '市县级知识管理权限', TRUE),
('r0000001-0000-0000-0000-000000000004', 'business_user', '业务用户', '普通业务人员权限', TRUE),
('r0000001-0000-0000-0000-000000000005', 'viewer', '访客', '只读权限', TRUE);

-- 为平台管理员分配所有权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT 'r0000001-0000-0000-0000-000000000001', id FROM permissions;

-- 为省厅管理员分配知识+门户权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT 'r0000001-0000-0000-0000-000000000002', id FROM permissions
WHERE module IN ('knowledge', 'portal');

-- 为市县管理员分配知识搜索和查看权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT 'r0000001-0000-0000-0000-000000000003', id FROM permissions
WHERE code IN ('knowledge:search', 'knowledge:read', 'portal:view');

-- 为业务用户分配基础权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT 'r0000001-0000-0000-0000-000000000004', id FROM permissions
WHERE code IN ('knowledge:search', 'knowledge:read', 'portal:view');

-- 为访客分配只读权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT 'r0000001-0000-0000-0000-000000000005', id FROM permissions
WHERE code = 'knowledge:search';

-- 插入超级管理员用户 (密码: admin123)
INSERT INTO users (id, username, password_hash, email, full_name, org_id, is_superuser) VALUES
('u0000001-0000-0000-0000-000000000001', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.AKj1p.o2KsMmDi', 'admin@example.com', '系统管理员', 'a0000000-0000-0000-0000-000000000001', TRUE);

-- 将超级管理员分配给平台管理员角色
INSERT INTO user_roles (user_id, role_id) VALUES
('u0000001-0000-0000-0000-000000000001', 'r0000001-0000-0000-0000-000000000001');
