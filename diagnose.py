"""
Supabase 连接诊断脚本
用于测试数据库连接和配置是否正确
"""

import streamlit as st
from supabase import create_client
from datetime import datetime

st.set_page_config(page_title="Supabase 诊断", page_icon="🔍")

st.title("🔍 Supabase 连接诊断工具")
st.markdown("---")

# 读取配置
st.subheader("1️⃣ 配置检查")

try:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    
    st.success(f"✅ URL 已配置: `{url}`")
    st.success(f"✅ Key 已配置: `{key[:20]}...{key[-10:]}`")
    
except Exception as e:
    st.error(f"❌ 配置读取失败: {str(e)}")
    st.stop()

st.markdown("---")

# 测试连接
st.subheader("2️⃣ 连接测试")

try:
    client = create_client(url, key)
    st.success("✅ Supabase 客户端创建成功")
except Exception as e:
    st.error(f"❌ 客户端创建失败: {str(e)}")
    st.stop()

st.markdown("---")

# 测试表访问
st.subheader("3️⃣ 表结构检查")

# 测试 notifications 表
try:
    result = client.table('notifications').select('*').limit(1).execute()
    st.success("✅ `notifications` 表可访问")
    
    if result.data:
        st.info(f"表中已有 {len(result.data)} 条记录（显示前1条）")
        st.json(result.data)
    else:
        st.warning("⚠️ `notifications` 表为空，但表存在")
        
except Exception as e:
    st.error(f"❌ `notifications` 表访问失败")
    st.error(f"错误详情: {str(e)}")
    st.warning("**可能的原因**：表未创建，请在 Supabase SQL Editor 中运行 `create_tables.sql`")

# 测试 images 表
try:
    result = client.table('images').select('*').limit(1).execute()
    st.success("✅ `images` 表可访问")
except Exception as e:
    st.error(f"❌ `images` 表访问失败")
    st.error(f"错误详情: {str(e)}")

st.markdown("---")

# 测试 INSERT 权限
st.subheader("4️⃣ 插入权限测试")

if st.button("🧪 测试插入操作", type="primary"):
    test_data = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'content': f'[诊断测试] {datetime.now().strftime("%H:%M:%S")}',
        'attribute': '普通',
        'category': '测试',
        'person': '诊断工具'
    }
    
    try:
        result = client.table('notifications').insert(test_data).execute()
        
        if result.data:
            inserted_id = result.data[0]['id']
            st.success(f"✅ 插入成功！记录 ID: {inserted_id}")
            st.json(result.data[0])
            
            # 尝试删除测试数据
            if st.button("🗑️ 删除测试数据"):
                client.table('notifications').delete().eq('id', inserted_id).execute()
                st.success("✅ 测试数据已删除")
        else:
            st.error("❌ 插入失败：无返回数据")
            
    except Exception as e:
        st.error(f"❌ 插入失败")
        st.error(f"错误详情: {str(e)}")
        
        # 分析错误原因
        error_msg = str(e).lower()
        
        if 'permission' in error_msg or 'policy' in error_msg:
            st.warning("""
            **可能的原因：权限问题**
            
            解决方案：
            1. 登录 Supabase Dashboard
            2. 进入 Authentication → Policies
            3. 为 `notifications` 表添加策略，或临时禁用 RLS
            
            临时解决（仅用于开发）：
            ```sql
            ALTER TABLE notifications DISABLE ROW LEVEL SECURITY;
            ALTER TABLE images DISABLE ROW LEVEL SECURITY;
            ```
            """)
        elif 'relation' in error_msg or 'does not exist' in error_msg:
            st.warning("""
            **可能的原因：表不存在**
            
            解决方案：
            1. 登录 Supabase Dashboard
            2. 进入 SQL Editor
            3. 运行 `create_tables.sql` 中的脚本
            """)
        else:
            st.info("请检查 Supabase Dashboard 的日志以获取更多信息")

st.markdown("---")

# 总结
st.subheader("📊 诊断总结")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("配置", "✅" if url and key else "❌")

with col2:
    st.metric("连接", "✅" if client else "❌")

with col3:
    st.metric("表访问", "待测试")

st.markdown("---")

st.info("""
💡 **常见问题解决方案**

1. **表不存在** → 运行 `create_tables.sql`
2. **权限错误** → 禁用 RLS 或配置策略
3. **连接超时** → 检查网络或 Supabase 项目状态
4. **Key 错误** → 确认使用的是 `anon public` key

**下一步**：
- 如果所有测试通过，重启主应用：`streamlit run app.py`
- 如果仍有问题，提供上述错误信息以获取帮助
""")
