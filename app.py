import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

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
DB_FILE = 'notifications_v2.db'

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    # 启用外键支持
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            content TEXT NOT NULL,
            attribute TEXT,
            category TEXT,
            person TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            notif_id INTEGER,
            img_data BLOB,
            filename TEXT,
            FOREIGN KEY(notif_id) REFERENCES notifications(id) ON DELETE CASCADE)''')

def get_images_by_id(notif_id):
    with get_connection() as conn:
        return conn.execute("SELECT img_data FROM images WHERE notif_id=?", (notif_id,)).fetchall()

# ==========================================
# 4. 主程序逻辑
# ==========================================
def main():
    st.set_page_config(page_title="CAR2 PT Board", layout="wide", page_icon="🏭")
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
        lang_code = st.radio("Language / 言語", ["中文", "日本語"], horizontal=True)
        L = TRANSLATIONS["CN"] if lang_code == "中文" else TRANSLATIONS["JP"]
        st.divider()
        st.header(L["sidebar_title"])

        if not st.session_state.is_admin:
            st.subheader(L["login_header"])
            pwd = st.text_input(L["password_label"], type="password")
            if st.button(L["login_btn"]):
                if pwd == "123456":
                    st.session_state.is_admin = True
                    st.rerun()
                else:
                    st.error(L["login_fail"])
        else:
            st.success(L["login_success"])
            if st.button(L["logout_btn"]):
                st.session_state.is_admin = False
                st.rerun()

    st.title(L["title"])

    # --- 滚动通知栏 ---
    with get_connection() as conn:
        today = datetime.now().strftime('%Y-%m-%d')
        today_news = pd.read_sql_query(f"SELECT content, person, attribute FROM notifications WHERE date='{today}'", conn)

    if not today_news.empty:
        ticker_items = [f"{'🚨' if row['attribute'] in ['紧急', '緊急'] else 'ℹ️'} {row['content']} ({row['person']})" for _, row in today_news.iterrows()]
        ticker_text = " &nbsp;&nbsp;&nbsp;&nbsp; || &nbsp;&nbsp;&nbsp;&nbsp; ".join(ticker_items)
        st.markdown(f'<div style="background:#fff3cd;padding:10px;border-radius:5px;color:#856404;"><marquee scrollamount="6">{ticker_text}</marquee></div>', unsafe_allow_html=True)

    # --- 稳定 Tab 结构 ---
    tab1, tab2 = st.tabs([L["tab_view"], L["tab_admin"]])

    # ==========================
    # TAB 1: 看板 (所有人可见)
    # ==========================
    with tab1:
        with get_connection() as conn:
            df = pd.read_sql_query("SELECT * FROM notifications ORDER BY date DESC, id DESC", conn)

        search_term = st.text_input(L["search_label"])
        if not df.empty:
            if search_term:
                df = df[df['content'].str.contains(search_term, case=False) | df['person'].str.contains(search_term, case=False)]
            
            st.write(f"Total: {len(df)}")
            for _, row in df.iterrows():
                icon = "🔴" if row['attribute'] in ['紧急', '緊急'] else ("🟡" if row['attribute'] == '重要' else "⚪")
                preview = str(row['content']).replace('\n', ' ')[:40] + "..."
                label = f"【{row['date']}】 {icon}{row['attribute']} 👤{row['person']} : {preview}"
                
                with st.expander(label):
                    st.caption(f"ID: {row['id']} | {L['form_cat']}: {row['category']}")
                    st.info(row['content'])
                    imgs = get_images_by_id(row['id'])
                    if imgs:
                        cols = st.columns(4)
                        for i, img in enumerate(imgs):
                            cols[i % 4].image(img[0], use_container_width=True)
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
                            with get_connection() as conn:
                                cur = conn.cursor()
                                cur.execute('INSERT INTO notifications (date, content, attribute, category, person) VALUES (?,?,?,?,?)',
                                            (f_date, f_content, f_attr, f_cat, f_person))
                                new_id = cur.lastrowid
                                if f_imgs:
                                    for img in f_imgs:
                                        cur.execute('INSERT INTO images (notif_id, img_data, filename) VALUES (?,?,?)', (new_id, img.getvalue(), img.name))
                                conn.commit()
                            st.toast(L["msg_pub_success"])
                            st.rerun()

            # B: 修改
            with col_edit:
                st.subheader(L["admin_col_edit"])
                edit_id = st.number_input(L["form_id_load"], min_value=1, step=1)
                if st.button(L["btn_load"]):
                    with get_connection() as conn:
                        row = conn.execute("SELECT * FROM notifications WHERE id=?", (edit_id,)).fetchone()
                        if row:
                            st.session_state.edit_data = {"id": row[0], "date": datetime.strptime(row[1], '%Y-%m-%d').date(), "content": row[2], "attr": row[3], "cat": row[4], "person": row[5]}
                        else: st.error(L["msg_id_not_found"])

                if st.session_state.edit_data:
                    with st.form("edit_form"):
                        e_content = st.text_area(L["form_content"], st.session_state.edit_data["content"])
                        if st.form_submit_button(L["btn_update"]):
                            with get_connection() as conn:
                                conn.execute('UPDATE notifications SET content=? WHERE id=?', (e_content, st.session_state.edit_data["id"]))
                                conn.commit()
                            st.success(L["msg_update_success"])
                            st.session_state.edit_data = None
                            st.rerun()

            # C: 删除
            with col_del:
                st.subheader(L["admin_col_del"])
                del_id = st.number_input("Delete ID", min_value=1, step=1)
                if st.button(L["btn_delete"]):
                    with get_connection() as conn:
                        conn.execute("DELETE FROM notifications WHERE id=?", (del_id,))
                        conn.commit()
                    st.success(L["msg_del_success"])
                    st.rerun()

if __name__ == '__main__':
    main()
