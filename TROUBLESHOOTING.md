# 🚨 发布信息失败 - 快速修复指南

## ❌ 问题原因

您的应用无法发布信息，因为 Supabase 数据库配置缺失。

## ✅ 解决方案

### 方案 1：使用 Supabase（云端数据库）- 推荐用于部署

#### 步骤 1：获取 Supabase 凭据

1. 访问 [Supabase Dashboard](https://app.supabase.com)
2. 登录您的账户
3. 选择您的项目
4. 进入 **Settings** → **API**
5. 复制以下信息：
   - **Project URL**（类似：`https://xxxxx.supabase.co`）
   - **anon/public key**（以 `eyJhbGci...` 开头的长字符串）

#### 步骤 2：配置 secrets.toml

打开 `.streamlit/secrets.toml`，填入真实值：

```toml
[supabase]
url = "https://your-project-id.supabase.co"  # 替换为您的实际 URL
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # 替换为您的实际 Key

[admin]
password = "123456"
```

#### 步骤 3：创建数据库表

在 Supabase Dashboard 的 **SQL Editor** 中执行：

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

#### 步骤 4：重启应用

```bash
# 停止当前应用（Ctrl+C）
# 重新启动
streamlit run app.py
```

---

### 方案 2：使用本地 SQLite（快速测试）- 仅限开发环境

#### 修改 app.py

找到第 102 行，修改为：

```python
# 修改前
DB_TYPE = 'SUPABASE'

# 修改后
DB_TYPE = 'SQLITE'
```

#### 重启应用

应用会自动创建本地 `notifications_v2.db` 文件，无需 Supabase 配置。

**⚠️ 注意**：
- SQLite 模式仅适用于本地开发
- 数据存储在本地文件中
- 部署到 Streamlit Cloud 时必须使用 Supabase

---

## 🔍 验证修复

修复后，测试发布功能：

1. 重启 Streamlit 应用
2. 登录管理员账户（密码：123456）
3. 在 "➕ 发布通知" 栏填写测试数据
4. 点击 "发布通知"
5. 检查是否显示成功消息

**预期结果**：
- ✅ 显示 "发布成功！" 消息
- ✅ 在看板中看到新发布的通知

---

## 🆘 仍然失败？

如果仍然无法发布，检查：

### 检查点 1：Streamlit 控制台错误

查看运行 Streamlit 的终端窗口，是否有错误信息：
- `KeyError: 'url'` → secrets.toml 配置不正确
- `Connection refused` → Supabase URL 错误或网络问题
- `Permission denied` → API Key 权限不足

### 检查点 2：secrets.toml 格式

确保文件格式正确（TOML 格式）：
```toml
[supabase]
url = "https://xxx.supabase.co"  # 必须有引号
key = "eyJxxx..."                # 必须有引号
```

### 检查点 3：数据库表是否存在

如果使用 Supabase，确认在 Dashboard 的 Table Editor 中能看到 `notifications` 表。

---

## 📞 需要帮助？

提供以下信息以获得更精准的帮助：
1. 您选择哪个方案？（Supabase 或 SQLite）
2. 终端显示的错误消息（如有）
3. 是本地开发还是部署到 Streamlit Cloud？
