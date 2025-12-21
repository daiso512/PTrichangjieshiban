import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ==========================================
# 0. 多语言词典配置
# ==========================================
TRANSLATIONS = {
    "CN": {
        "title": "🏭 CAR2 PT组日常通知看板",
        "sidebar_title": "🔧 设置与登录",
        "lang_select": "选择语言 / 言語切替",
        "login_header": "管理员登录",
        "password_label": "请输入密码",
        "login_btn": "登录",
        "logout_btn": "退出登录",
        "login_success": "已以管理员身份登录",
        "login_fail": "密码错误",
        "tab_view": "👀 公告看板 (View)",
        "tab_admin": "⚙️ 管理后台 (Admin)",
        "urgent_none": "",
        "search_label": "🔍 搜索历史记录",
        "export_btn": "📥 下载报表 (Excel/CSV)",
        "admin_col_add": "➕ 发布通知 (Create)",
        "admin_col_edit": "✏️ 修改 (Update)",
        "admin_col_del": "🗑️ 删除 (Delete)",
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
        "btn_delete": "删除记录",
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
        "login_header": "管理者ログイン",
        "password_label": "パスワード",
        "login_btn": "ログイン",
        "logout_btn": "ログアウト",
        "login_success": "管理者としてログイン中",
        "login_fail": "パスワードエラー",
        "tab_view": "👀 掲示板 (View)",
        "tab_admin": "⚙️ 管理パネル (Admin)",
        "urgent_none": "",
        "search_label": "🔍 検索",
        "export_btn": "📥 レポート出力",
        "admin_col_add": "➕ 新規 (Create)",
        "admin_col_edit": "✏️ 編集 (Update)",
        "admin_col_del": "🗑️ 削除 (Delete)",
        "form_date": "日付",
        "form_person": "担当者",
        "form_cat": "区分",
        "form_attr": "レベル",
        "form_content": "連絡事項",
        "form_imgs": "画像アップロード (複数可)",
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
# 1. 基础配置与数据库
# ==========================================
DB_FILE = 'notifications_v2.db' 

def init_db():
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

def get_connection():
    return sqlite3.connect(DB_FILE)

def get_images_by_id(notif_id):
    conn = get_connection()
    imgs = conn.execute("SELECT img_data FROM images WHERE notif_id=?", (notif_id,)).fetchall()
    conn.close()
    return imgs

# ==========================================
# 主程序
# ==========================================
def main():
    st.set_page_config(page_title="CAR2 PT Board", layout="wide", page_icon="🏭")
    
    # CSS 隐藏 Deploy, Footer, 以及调整 Expander 样式
    hide_streamlit_style = """
        <style>
        .stDeployButton {display:none;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        /* 调整Expander头部字体，使其更清晰 */
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

    # --- 侧边栏 ---
    with st.sidebar:
        lang_code = st.radio("Language / 言語", ["中文", "日本語"], horizontal=True)
        L = TRANSLATIONS["CN"] if lang_code == "中文" else TRANSLATIONS["JP"]
        
        st.markdown("---")
        st.header(L["sidebar_title"])

        if 'is_admin' not in st.session_state:
            st.session_state.is_admin = False

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

    # --- 标题 ---
    st.title(L["title"])

    # --- 滚动通知栏 ---
    conn = get_connection()
    today = datetime.now().strftime('%Y-%m-%d')
    today_news = pd.read_sql_query(
        f"SELECT content, person, attribute FROM notifications WHERE date='{today}'", conn
    )
    conn.close()

    if not today_news.empty:
        ticker_items = []
        for _, row in today_news.iterrows():
            icon = "🚨" if row['attribute'] in ['紧急', '緊急'] else "ℹ️"
            ticker_items.append(f"{icon} {row['content']} ({row['person']})")
        
        ticker_text = " &nbsp;&nbsp;&nbsp;&nbsp; || &nbsp;&nbsp;&nbsp;&nbsp; ".join(ticker_items)
        st.markdown(f"""
            <div style="background-color: #fff3cd; padding: 10px; border-radius: 5px; border: 1px solid #ffeeba; color: #856404; margin-bottom: 20px;">
                <marquee direction="left" scrollamount="6">{ticker_text}</marquee>
            </div>
        """, unsafe_allow_html=True)

    if st.session_state.is_admin:
        tab1, tab2 = st.tabs([L["tab_view"], L["tab_admin"]])
    else:
        tab1 = st.container()
        tab2 = None

    # ==========================
    # TAB 1: 看板 (View) - 卡片式 + 预览40字
    # ==========================
    with tab1:
        conn = get_connection()
        df = pd.read_sql_query("SELECT * FROM notifications ORDER BY date DESC, id DESC", conn)
        conn.close()

        col_search, col_space = st.columns([1, 2])
        with col_search:
            search_term = st.text_input(L["search_label"])

        if not df.empty:
            if search_term:
                mask = (
                    df['content'].str.contains(search_term, case=False) | 
                    df['person'].str.contains(search_term, case=False)
                )
                df = df[mask]
            
            st.markdown(f"**Total: {len(df)} Records**")
            
            for index, row in df.iterrows():
                # 1. 图标处理
                attr_icon = "⚪" 
                if row['attribute'] in ['紧急', '緊急']:
                    attr_icon = "🔴"
                elif row['attribute'] in ['重要']:
                    attr_icon = "🟡"
                
                # 2. 内容预览处理 (核心修改点)
                # 移除换行符，防止标题格式乱掉
                content_preview = str(row['content']).replace('\n', ' ')
                # 截取前40个字符
                if len(content_preview) > 40:
                    content_preview = content_preview[:40] + "..."
                
                # 3. 拼接标题: 【日期】 级别 | 责任人 : 内容摘要
                label_text = f"【{row['date']}】 {attr_icon}{row['attribute']} ｜ 👤{row['person']} ： {content_preview}"
                
                # 4. 创建折叠区
                with st.expander(label_text):
                    # 内部显示完整信息
                    st.caption(f"ID: {row['id']} | {L['form_cat']}: {row['category']}")
                    st.info(row['content']) # 完整内容
                    
                    # 图片展示
                    imgs = get_images_by_id(row['id'])
                    if imgs:
                        st.markdown(f"**📷 {len(imgs)} {L['lbl_img_attached']}:**")
                        cols = st.columns(min(len(imgs), 4)) 
                        for i, img_data in enumerate(imgs):
                            with cols[i % 4]:
                                st.image(img_data[0], use_column_width=True)
                    else:
                        st.caption(L["lbl_no_img"])
        else:
            st.info("No Data")

        if not df.empty:
            st.download_button(
                label=L["export_btn"],
                data=df.to_csv(index=False).encode('utf-8-sig'),
                file_name=f'CAR2_Report_{datetime.now().date()}.csv',
                mime='text/csv'
            )

    # ==========================
    # TAB 2: 管理后台 (Admin)
    # ==========================
    if st.session_state.is_admin and tab2:
        with tab2:
            col_add, col_edit, col_del = st.columns([3, 1.5, 1.5], gap="medium")
            
            # --- A: 发布 (Create) ---
            with col_add:
                st.markdown(f"#### {L['admin_col_add']}")
                with st.form("add_form", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        f_date = st.date_input(L["form_date"], datetime.now())
                        f_cat = st.selectbox(L["form_cat"], L["opt_cat"])
                    with c2:
                        f_person = st.text_input(L["form_person"])
                        f_attr = st.selectbox(L["form_attr"], L["opt_attr"])
                    
                    f_content = st.text_area(L["form_content"], height=150)
                    f_imgs = st.file_uploader(L["form_imgs"], accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])
                    
                    if st.form_submit_button(L["btn_publish"]):
                        if f_content and f_person:
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
                            st.toast(L["msg_pub_success"], icon="✅")
                            st.rerun()
                        else:
                            st.error("Missing content or person")

            # --- B: 修改 (Update) ---
            with col_edit:
                st.markdown(f"#### {L['admin_col_edit']}")
                edit_id = st.number_input(L["form_id_load"], min_value=1, step=1, key="edit_id_input")
                
                if 'edit_data' not in st.session_state:
                    st.session_state.edit_data = None

                if st.button(L["btn_load"], key="btn_load_data"):
                    conn = get_connection()
                    row = conn.execute("SELECT * FROM notifications WHERE id=?", (edit_id,)).fetchone()
                    conn.close()
                    if row:
                        st.session_state.edit_data = {
                            "id": row[0],
                            "date": datetime.strptime(row[1], '%Y-%m-%d').date(),
                            "content": row[2],
                            "attr": row[3],
                            "cat": row[4],
                            "person": row[5]
                        }
                    else:
                        st.error(L["msg_id_not_found"])
                        st.session_state.edit_data = None

                if st.session_state.edit_data:
                    with st.form("edit_form"):
                        st.caption(f"ID: {st.session_state.edit_data['id']}")
                        e_date = st.date_input(L["form_date"], st.session_state.edit_data["date"])
                        e_person = st.text_input(L["form_person"], st.session_state.edit_data["person"])
                        
                        try: cat_idx = L["opt_cat"].index(st.session_state.edit_data["cat"])
                        except: cat_idx = 0
                        try: attr_idx = L["opt_attr"].index(st.session_state.edit_data["attr"])
                        except: attr_idx = 0
                            
                        e_cat = st.selectbox(L["form_cat"], L["opt_cat"], index=cat_idx)
                        e_attr = st.selectbox(L["form_attr"], L["opt_attr"], index=attr_idx)
                        e_content = st.text_area(L["form_content"], st.session_state.edit_data["content"], height=100)
                        
                        st.caption("注：暂不支持在此处修改图片，请删除后重新发布")

                        if st.form_submit_button(L["btn_update"]):
                            conn = get_connection()
                            conn.execute('''
                                UPDATE notifications 
                                SET date=?, content=?, attribute=?, category=?, person=?
                                WHERE id=?
                            ''', (e_date, e_content, e_attr, e_cat, e_person, st.session_state.edit_data["id"]))
                            conn.commit()
                            conn.close()
                            st.success(L["msg_update_success"])
                            st.session_state.edit_data = None
                            st.rerun()

            # --- C: 删除 (Delete) ---
            with col_del:
                st.markdown(f"#### {L['admin_col_del']}")
                with st.form("del_form", clear_on_submit=True):
                    del_id = st.number_input(f"ID", min_value=1, step=1, key="del_id_input")
                    if st.form_submit_button(L["btn_delete"]):
                        conn = get_connection()
                        exists = conn.execute("SELECT 1 FROM notifications WHERE id=?", (del_id,)).fetchone()
                        if exists:
                            conn.execute("DELETE FROM notifications WHERE id=?", (del_id,))
                            conn.commit()
                            conn.close()
                            st.success(f"ID {del_id}: {L['msg_del_success']}")
                            st.rerun()
                        else:
                            conn.close()
                            st.error(L["msg_id_not_found"])

if __name__ == '__main__':
    main()