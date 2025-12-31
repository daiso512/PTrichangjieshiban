import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import binascii
from supabase import create_client, Client

# ==========================================
# 1. 基础配置与 Session State (必须在最前)
# ==========================================
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'edit_data' not in st.session_state:
    st.session_state.edit_data = None

# ==========================================
# 2. 多语言词典配置 (完整保留)
# ==========================================
TRANSLATIONS = {
    "CN": {
        "title": "🏭 CAR2 PT组日常通知看板",
        "sidebar_title": "🔧 设置与登录",
        "lang_select": "选择语言",
        "login_header": "管理员登录",
        "password_label": "请输入密码",
        "login_btn": "登录",
        "logout_btn": "退出登录",
        "login_success": "已以管理员身份登录",
        "login_fail": "密码错误",
        "tab_view": "👀 公告看板 (View)",
        "tab_admin": "⚙️ 管理后台 (Admin)",
        "login_msg": "🔓 请在左侧登录以使用管理功能",
        "search_label": "🔍 搜索内容或责任人",
        "export_btn": "📥 下载报表 (Excel/CSV)",
        "admin_col_add": "➕ 发布通知",
        "admin_col_edit": "✏️ 修改记录",
        "admin_col_del": "🗑️ 删除记录",
        "form_date": "日期",
        "form_person": "责任人",
        "form_cat": "分类",
        "form_attr": "级别",
        "form_content": "事项内容",
        "form_imgs": "上传图片 (支持多张)",
        "form_id_load": "输入要修改的ID",
        "btn_load": "读取数据",
        "btn_publish": "发布通知",
        "btn_update": "确认修改",
        "btn_delete": "删除",
        "msg_pub_success": "发布成功！",
        "msg_update_success": "修改成功！",
        "msg_del_success": "删除成功！",
        "msg_id_not_found": "未找到该ID",
        "opt_cat": ["日常通知", "品质管理", "注意事项", "其他事项"],
        "opt_attr": ["普通", "紧急", "重要"],
        "lbl_no_img": "无图片附件",
        "lbl_img_attached": "张图片附件"
    },
    "JP": {
        "title": "🏭 CAR2 PTチーム掲示板",
        "sidebar_title": "🔧 設定 & ログイン",
        "lang_select": "言語切替",
        "login_header": "管理者ログイン",
        "password_label": "パスワード",
        "login_btn": "ログイン",
        "logout_btn": "ログアウト",
        "login_success": "管理者としてログイン中",
        "login_fail": "パスワードエラー",
        "tab_view": "👀 掲示板 (View)",
        "tab_admin": "⚙️ 管理パネル (Admin)",
        "login_msg": "🔓 管理者機能を利用するにはログインしてください",
        "search_label": "🔍 検索",
        "export_btn": "📥 レポート出力",
        "admin_col_add": "➕ 新規作成",
        "admin_col_edit": "✏️ 編集",
        "admin_col_del": "🗑️ 削除",
        "form_date": "日付",
        "form_person": "担当者",
        "form_cat": "区分",
        "form_attr": "レベル",
        "form_content": "連絡事項",
        "form_imgs": "画像アップロード",
        "form_id_load": "編集するIDを入力",
        "btn_load": "読込",
        "btn_publish": "投稿",
        "btn_update": "更新",
        "btn_delete": "削除",
        "msg_pub_success": "投稿完了！",
        "msg_update_success": "更新完了！",
        "msg_del_success": "削除完了！",
        "msg_id_not_found": "IDが見つかりません",
        "opt_cat": ["日常通知", "品質管理", "注意事項", "その他"],
        "opt_attr": ["普通", "緊急", "重要"],
        "lbl_no_img": "画像なし",
        "lbl_img_attached": "枚の画像"
    }
}

# ==========================================
# 3. 数据库操作
# ==========================================
# 选择数据库模式: 'SQLITE' (本地) 或 'SUPABASE' (云端)
DB_TYPE = 'SUPABASE' 

DB_FILE = 'notifications_v2.db' 

@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        return None

def init_db():
    if DB_TYPE == 'SQLITE':
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                content TEXT NOT NULL,
                attribute TEXT,
                category TEXT,
                person TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                notif_id INTEGER,
                img_data BLOB,
                filename TEXT,
                FOREIGN KEY(notif_id) REFERENCES notifications(id) ON DELETE CASCADE
            )
        ''')
        conn.commit()
        conn.close()
    # Supabase tables are pre-created via SQL Editor

def get_connection():
    if DB_TYPE == 'SQLITE':
        return sqlite3.connect(DB_FILE)
    return None

def get_images_by_id(notif_id):
    if DB_TYPE == 'SQLITE':
        conn = get_connection()
        imgs = conn.execute("SELECT img_data FROM images WHERE notif_id=?", (notif_id,)).fetchall()
        # imgs format: [(blob,), (blob,)]
        conn.close()
        return imgs
    else:
        sb = init_supabase()
        if not sb: return []
        res = sb.table('images').select('img_data').eq('notif_id', notif_id).execute()
        # Convert hex string (bytea) back to bytes
        imgs = []
        for item in res.data:
            hex_str = item['img_data']
            # Postgres hex format: \xDEADBEEF...
            if hex_str.startswith(r'\x'):
                hex_str = hex_str[2:]
            try:
                img_bytes = binascii.unhexlify(hex_str)
                imgs.append((img_bytes,))
            except:
                pass
        return imgs

# ==========================================
# 4. 主程序逻辑
# ==========================================
def main():
    st.set_page_config(page_title="CAR2 PT Board", layout="wide", page_icon="🏭")
    
    hide_streamlit_style = """
        <style>
        .stAppDeployButton {display:none !important;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .streamlit-expanderHeader {
            font-family: 'Segoe UI', sans-serif;
            font-size: 15px !important;
            font-weight: 500;
            color: #31333F;
        }
        </style>
        """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    init_db()

    # --- 样式优化 ---
    st.markdown("""
        <style>
        .stAppDeployButton {display:none !important;}
        footer {visibility: hidden;}
        .streamlit-expanderHeader { font-size: 16px !important; font-weight: bold; }
        </style>
        """, unsafe_allow_html=True)

    # --- 侧边栏 ---
    with st.sidebar:
        # DB Mode Indicator
        if DB_TYPE == 'SUPABASE':
            st.caption("☁️ Cloud Mode (Supabase)")
        else:
            st.caption("📂 Local Mode (SQLite)")

        lang_code = st.radio("Language / 言語", ["中文", "日本語"], horizontal=True)
        L = TRANSLATIONS["CN"] if lang_code == "中文" else TRANSLATIONS["JP"]
        st.divider()
        st.header(L["sidebar_title"])

        if not st.session_state.is_admin:
            with st.expander(L["login_header"], expanded=False):
                pwd = st.text_input(L["password_label"], type="password")
                if st.button(L["login_btn"]):
                    # 从 secrets 获取密码
                    admin_pwd = st.secrets["admin"]["password"] if "admin" in st.secrets else "123456"
                    if pwd == admin_pwd:
                        st.session_state.is_admin = True
                        st.rerun()
                    else:
                        st.error(L["login_fail"])
        else:
            with st.expander(L["login_header"], expanded=True):
                st.success(L["login_success"])
                if st.button(L["logout_btn"]):
                    st.session_state.is_admin = False
                    st.rerun()

    st.title(L["title"])

    # --- 滚动通知栏 ---
    today = datetime.now().strftime('%Y-%m-%d')
    today_news = pd.DataFrame()

    if DB_TYPE == 'SQLITE':
        conn = get_connection()
        today_news = pd.read_sql_query(
            f"SELECT content, person, attribute FROM notifications WHERE date='{today}'", conn
        )
        conn.close()
    else:
        sb = init_supabase()
        if sb:
            res = sb.table('notifications').select('content, person, attribute').eq('date', today).execute()
            today_news = pd.DataFrame(res.data)
    
    if not today_news.empty:
        ticker_items = [f"{'🚨' if row['attribute'] in ['紧急', '緊急'] else 'ℹ️'} {row['content']} ({row['person']})" for _, row in today_news.iterrows()]
        ticker_text = " &nbsp;&nbsp;&nbsp;&nbsp; || &nbsp;&nbsp;&nbsp;&nbsp; ".join(ticker_items)
        st.markdown(f'<div style="background:#fff3cd;padding:10px;border-radius:5px;color:#856404;"><marquee scrollamount="6">{ticker_text}</marquee></div>', unsafe_allow_html=True)

    # --- 稳定 Tab 结构 ---
    tab1, tab2 = st.tabs([L["tab_view"], L["tab_admin"]])

    # ==========================
    # TAB 1: 看板 (View)
    # ==========================
    with tab1:
        df = pd.DataFrame()
        if DB_TYPE == 'SQLITE':
            conn = get_connection()
            df = pd.read_sql_query("SELECT * FROM notifications ORDER BY date DESC, id DESC", conn)
            conn.close()
        else:
            sb = init_supabase()
            if sb:
                # Supabase typically needs explicit order
                res = sb.table('notifications').select('*').order('date', desc=True).order('id', desc=True).execute()
                df = pd.DataFrame(res.data)

        col_search, col_space = st.columns([1, 2])
        with col_search:
            search_term = st.text_input(L["search_label"])

        if not df.empty:
            if search_term:
                df = df[df['content'].str.contains(search_term, case=False) | df['person'].str.contains(search_term, case=False)]
            
            st.markdown(f"**Total: {len(df)} Records**")
            
            for index, row in df.iterrows():
                # 1. 图标处理
                attr_icon = "⚪" 
                if row['attribute'] in ['紧急', '緊急']:
                    attr_icon = "🔴"
                elif row['attribute'] in ['重要']:
                    attr_icon = "🟡"
                
                # 2. 内容预览
                content_preview = str(row['content']).replace('\n', ' ')
                if len(content_preview) > 40:
                    content_preview = content_preview[:40] + "..."
                
                label_text = f"【{row['date']}】 {attr_icon}{row['attribute']} ｜ 👤{row['person']} ： {content_preview}"
                
                # 3. 创建折叠区
                with st.expander(label_text):
                    st.caption(f"ID: {row['id']} | {L['form_cat']}: {row['category']}")
                    st.info(row['content']) 
                    
                    imgs = get_images_by_id(row['id'])
                    if imgs:
                        cols = st.columns(min(len(imgs), 4)) 
                        for i, img_data in enumerate(imgs):
                            with cols[i % 4]:
                                st.image(img_data[0], use_container_width=True)
        else:
            st.info("No Data")

    # ==========================
    # TAB 2: 管理后台 (权限控制)
    # ==========================
    with tab2:
        if not st.session_state.is_admin:
            st.warning(L["login_msg"])
        else:
            col_add, col_edit, col_del = st.columns([3, 2, 1.5], gap="large")
            
            # A: 发布
            with col_add:
                st.subheader(L["admin_col_add"])
                with st.form("add_form", clear_on_submit=True):
                    f_date = st.date_input(L["form_date"])
                    f_person = st.text_input(L["form_person"])
                    f_cat = st.selectbox(L["form_cat"], L["opt_cat"])
                    f_attr = st.selectbox(L["form_attr"], L["opt_attr"])
                    f_content = st.text_area(L["form_content"])
                    f_imgs = st.file_uploader(L["form_imgs"], accept_multiple_files=True)
                    if st.form_submit_button(L["btn_publish"]):
                        if f_content and f_person:
                            if DB_TYPE == 'SQLITE':
                                conn = get_connection()
                                cursor = conn.cursor()
                                cursor.execute(
                                    'INSERT INTO notifications (date, content, attribute, category, person) VALUES (?, ?, ?, ?, ?)',
                                    (f_date, f_content, f_attr, f_cat, f_person)
                                )
                                new_id = cursor.lastrowid
                                if f_imgs:
                                    for img_file in f_imgs:
                                        img_bytes = img_file.getvalue()
                                        cursor.execute(
                                            'INSERT INTO images (notif_id, img_data, filename) VALUES (?, ?, ?)',
                                            (new_id, img_bytes, img_file.name)
                                        )
                                conn.commit()
                                conn.close()
                            else:
                                sb = init_supabase()
                                if sb:
                                    res = sb.table('notifications').insert({
                                        'date': str(f_date),
                                        'content': f_content,
                                        'attribute': f_attr,
                                        'category': f_cat,
                                        'person': f_person
                                    }).execute()
                                    
                                    # Get the ID of the new row. 
                                    if res.data:
                                        new_id = res.data[0]['id']
                                        if f_imgs:
                                            img_inserts = []
                                            for img_file in f_imgs:
                                                # Convert to hex string for BYTEA
                                                hex_data = r'\x' + binascii.hexlify(img_file.getvalue()).decode('ascii')
                                                img_inserts.append({
                                                    'notif_id': new_id,
                                                    'img_data': hex_data, 
                                                    'filename': img_file.name
                                                })
                                            sb.table('images').insert(img_inserts).execute()

                            st.toast(L["msg_pub_success"], icon="✅")
                            st.rerun()

            # B: 修改
            with col_edit:
                st.subheader(L["admin_col_edit"])
                edit_id = st.number_input(L["form_id_load"], min_value=1, step=1, key="edit_id_input")
                
                if 'edit_data' not in st.session_state:
                    st.session_state.edit_data = None

                if st.button(L["btn_load"], key="btn_load_data"):
                    row = None
                    if DB_TYPE == 'SQLITE':
                        conn = get_connection()
                        row_raw = conn.execute("SELECT * FROM notifications WHERE id=?", (edit_id,)).fetchone()
                        conn.close()
                        if row_raw:
                            # Map array to dict
                            row = {
                                "id": row_raw[0],
                                "date": row_raw[1],
                                "content": row_raw[2],
                                "attr": row_raw[3],
                                "cat": row_raw[4],
                                "person": row_raw[5]
                            }
                    else:
                        sb = init_supabase()
                        if sb:
                            res = sb.table('notifications').select('*').eq('id', edit_id).execute()
                            if res.data:
                                row = res.data[0] # date is likely string 'YYYY-MM-DD'
                    
                    if row:
                        date_obj = row['date']
                        if isinstance(date_obj, str):
                            date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
                            
                        st.session_state.edit_data = {
                            "id": row['id'],
                            "date": date_obj,
                            "content": row['content'],
                            "attr": row.get('attribute') or row.get('attr'), # handle name diff if any
                            "cat": row.get('category') or row.get('cat'),
                            "person": row['person']
                        }
                    else:
                        st.error(L["msg_id_not_found"])
                        st.session_state.edit_data = None

                if st.session_state.edit_data:
                    with st.form("edit_form"):
                        e_content = st.text_area(L["form_content"], st.session_state.edit_data["content"])
                        if st.form_submit_button(L["btn_update"]):
                            if DB_TYPE == 'SQLITE':
                                conn = get_connection()
                                conn.execute('''
                                    UPDATE notifications 
                                    SET date=?, content=?, attribute=?, category=?, person=?
                                    WHERE id=?
                                ''', (st.session_state.edit_data["date"], e_content, st.session_state.edit_data["attr"], st.session_state.edit_data["cat"], st.session_state.edit_data["person"], st.session_state.edit_data["id"]))
                                conn.commit()
                                conn.close()
                            else:
                                sb = init_supabase()
                                if sb:
                                    sb.table('notifications').update({
                                        'content': e_content
                                    }).eq('id', st.session_state.edit_data["id"]).execute()

                            st.success(L["msg_update_success"])
                            st.session_state.edit_data = None
                            st.rerun()

            # C: 删除
            with col_del:
                st.subheader(L["admin_col_del"])
                with st.form("del_form", clear_on_submit=True):
                    del_id = st.number_input(f"ID", min_value=1, step=1, key="del_id_input")
                    if st.form_submit_button(L["btn_delete"]):
                        if DB_TYPE == 'SQLITE':
                            conn = get_connection()
                            exists = conn.execute("SELECT 1 FROM notifications WHERE id=?", (del_id,)).fetchone()
                            if exists:
                                conn.execute("DELETE FROM notifications WHERE id=?", (del_id,))
                                conn.commit()
                                st.success(f"ID {del_id}: {L['msg_del_success']}")
                            else:
                                st.error(L["msg_id_not_found"])
                            conn.close()
                            if exists: st.rerun()
                        else:
                            sb = init_supabase()
                            if sb:
                                # Check exist
                                res = sb.table('notifications').select('id').eq('id', del_id).execute()
                                if res.data:
                                    sb.table('notifications').delete().eq('id', del_id).execute()
                                    st.success(f"ID {del_id}: {L['msg_del_success']}")
                                    st.rerun()
                                else:
                                    st.error(L["msg_id_not_found"])

if __name__ == '__main__':
    main()
