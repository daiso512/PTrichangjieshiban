-- ================================================
-- 修复 RLS 策略问题 - 允许应用写入数据
-- ================================================
-- 在 Supabase Dashboard 的 SQL Editor 中运行此脚本
-- ================================================

-- 方案 1：禁用 RLS（推荐用于开发环境）
-- 这将允许所有操作，适合开发和测试
ALTER TABLE notifications DISABLE ROW LEVEL SECURITY;
ALTER TABLE images DISABLE ROW LEVEL SECURITY;

-- ================================================
-- 方案 2：启用 RLS 并添加允许策略（推荐用于生产环境）
-- 如果您希望保持 RLS 安全性，可以使用以下策略
-- ================================================

-- 取消下面的注释以启用方案 2

-- -- 启用 RLS
-- ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE images ENABLE ROW LEVEL SECURITY;

-- -- 允许所有人读取
-- CREATE POLICY "Allow public read access" ON notifications
--     FOR SELECT
--     USING (true);

-- CREATE POLICY "Allow public read access" ON images
--     FOR SELECT
--     USING (true);

-- -- 允许所有人插入、更新、删除（仅用于开发）
-- CREATE POLICY "Allow public insert" ON notifications
--     FOR INSERT
--     WITH CHECK (true);

-- CREATE POLICY "Allow public update" ON notifications
--     FOR UPDATE
--     USING (true);

-- CREATE POLICY "Allow public delete" ON notifications
--     FOR DELETE
--     USING (true);

-- CREATE POLICY "Allow public insert" ON images
--     FOR INSERT
--     WITH CHECK (true);

-- CREATE POLICY "Allow public update" ON images
--     FOR UPDATE
--     USING (true);

-- CREATE POLICY "Allow public delete" ON images
--     FOR DELETE
--     USING (true);

-- ================================================
-- 验证策略
-- ================================================

-- 查看当前策略
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies
WHERE tablename IN ('notifications', 'images');

-- 查看 RLS 状态
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE tablename IN ('notifications', 'images');
