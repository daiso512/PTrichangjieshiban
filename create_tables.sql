-- ================================================
-- Supabase 数据库表创建脚本
-- 用于 CAR2 PT 通知系统
-- ================================================
-- 使用方法：
-- 1. 登录 https://app.supabase.com
-- 2. 选择您的项目
-- 3. 进入 SQL Editor
-- 4. 复制粘贴本脚本
-- 5. 点击 Run 执行
-- ================================================

-- 创建 notifications 表
CREATE TABLE IF NOT EXISTS notifications (
    id BIGSERIAL PRIMARY KEY,
    date TEXT NOT NULL,
    content TEXT NOT NULL,
    attribute TEXT,
    category TEXT,
    person TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建 images 表
CREATE TABLE IF NOT EXISTS images (
    id BIGSERIAL PRIMARY KEY,
    notif_id BIGINT REFERENCES notifications(id) ON DELETE CASCADE,
    img_data BYTEA,
    filename TEXT
);

-- 添加索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_notifications_date ON notifications(date DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_images_notif_id ON images(notif_id);

-- 插入一条测试数据（可选）
INSERT INTO notifications (date, content, attribute, category, person) 
VALUES ('2026-01-01', '系统初始化完成', '普通', '其他事项', '系统管理员')
ON CONFLICT DO NOTHING;

-- 验证表创建成功
SELECT 'notifications 表记录数：' AS info, COUNT(*) AS count FROM notifications
UNION ALL
SELECT 'images 表记录数：' AS info, COUNT(*) AS count FROM images;
