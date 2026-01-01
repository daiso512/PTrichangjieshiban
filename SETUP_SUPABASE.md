# 🚀 Supabase 配置快速指南

## 📝 第一步：获取 Supabase 凭据

### 1. 访问 Supabase Dashboard
打开浏览器，访问：https://app.supabase.com

### 2. 登录并选择项目
- 如果没有项目，点击 "New Project" 创建一个
- 项目名称可以随意，例如：`car2-notifications`

### 3. 获取 API 凭据
在项目页面：
1. 点击左侧菜单的 **Settings**（设置图标）
2. 选择 **API** 
3. 复制以下两个值：

**Project URL**（项目 URL）：
```
https://xxxxxxxxxxxxx.supabase.co
```

**anon public**（匿名公钥）：
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ...（很长的字符串）
```

---

## 📝 第二步：配置 secrets.toml

打开 `.streamlit/secrets.toml`，填入刚才复制的值：

```toml
[supabase]
url = "https://xxxxxxxxxxxxx.supabase.co"  # 粘贴您的 Project URL
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # 粘贴您的 anon key

[admin]
password = "123456"
```

**⚠️ 重要**：
- URL 和 Key 必须用引号包围
- 确保没有多余的空格
- 保存文件后不要提交到 Git（已被 .gitignore 保护）

---

## 📝 第三步：创建数据库表

### 1. 打开 SQL Editor
在 Supabase Dashboard：
1. 点击左侧菜单的 **SQL Editor**
2. 点击 **New Query**

### 2. 执行建表脚本
复制 `create_tables.sql` 的全部内容，粘贴到 SQL Editor 中，点击 **Run**。

或者直接复制以下脚本：

```sql
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
```

### 3. 验证表创建
执行后，在左侧 **Table Editor** 中应该能看到：
- ✅ `notifications` 表
- ✅ `images` 表

---

## 📝 第四步：重启应用

### 1. 停止当前应用
在运行 Streamlit 的终端窗口按 `Ctrl + C`

### 2. 重新启动
```bash
streamlit run app.py
```

### 3. 验证连接
打开浏览器，应该能看到：
- ☁️ Cloud Mode (Supabase) - 显示在左上角

---

## 📝 第五步：测试发布功能

### 1. 登录管理员
- 在左侧边栏点击 "管理员登录"
- 输入密码：`123456`
- 点击 "登录"

### 2. 发布测试通知
切换到 "⚙️ 管理后台 (Admin)" 标签：
- 日期：选择今天
- 责任人：测试用户
- 分类：日常通知
- 级别：普通
- 内容：这是一条测试消息
- 点击 **发布通知**

### 3. 查看结果
切换到 "👀 公告看板 (View)" 标签，应该看到刚才发布的通知。

---

## ✅ 验证成功标志

如果配置成功，您应该看到：
- ✅ 发布后显示 "发布成功！" 消息
- ✅ 在看板中看到新通知
- ✅ 在 Supabase Dashboard 的 Table Editor 中能看到新记录

---

## ⚠️ 常见错误

### 错误 1：`KeyError: 'url'`
**原因**：secrets.toml 格式错误
**解决**：确保格式完全正确，URL 和 Key 有引号

### 错误 2：连接失败
**原因**：URL 或 Key 不正确
**解决**：重新从 Supabase Dashboard 复制凭据

### 错误 3：插入失败
**原因**：表未创建
**解决**：重新执行 create_tables.sql 脚本

---

## 📞 需要帮助？

如果遇到问题，请提供：
1. 终端显示的错误消息
2. secrets.toml 的内容（**隐藏 Key 的后半部分**）
3. Supabase Dashboard 中是否能看到表

当前 secrets.toml 文件位置：
```
d:\VSCODE\yanshi4\.streamlit\secrets.toml
```

SQL 脚本文件位置：
```
d:\VSCODE\yanshi4\create_tables.sql
```
