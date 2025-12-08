# app.py
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# ===== 設定 Google Sheets =====
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS = Credentials.from_service_account_file("credentials.json", scopes=SCOPE)
GC = gspread.authorize(CREDS)

# 請替換成你的 Spreadsheet ID
SPREADSHEET_ID = "1-j6aUXNyIq9I53HTECW39-aGSLa8t_V13lGFSSki_Rg"
SHEET = GC.open_by_key(SPREADSHEET_ID).sheet1  # 第一個工作表

# ===== Streamlit 頁面設定 =====
st.set_page_config(page_title="個人支出記錄系統", layout="centered")
st.title("💰 個人支出記錄系統")


# ===== 讀取現有資料 =====
def load_data():
    try:
        records = SHEET.get_all_records()
        df = pd.DataFrame(records)
        if df.empty:
            df = pd.DataFrame(columns=["日期", "分類", "金額", "備註"])
        return df
    except Exception as e:
        st.error(f"讀取資料失敗：{e}")
        return pd.DataFrame(columns=["日期", "分類", "金額", "備註"])


# ===== 功能：新增支出 =====
with st.form("新增支出"):
    st.subheader("新增支出")
    col1, col2 = st.columns(2)
    with col1:
        date_input = st.date_input("日期", value=datetime.today())
        amount = st.number_input("金額", min_value=0, step=10)
    with col2:
        category = st.selectbox("分類", ["餐飲", "交通", "娛樂", "購物", "醫療", "其他"])
        note = st.text_input("備註")
    submitted = st.form_submit_button("新增")

    if submitted:
        new_row = [
            date_input.strftime("%Y-%m-%d"),
            category,
            amount,
            note
        ]
        SHEET.append_row(new_row)
        st.success("✅ 支出已新增！")

# ===== 顯示與編輯現有資料 =====
st.subheader("現有記錄")
df = load_data()

if not df.empty:
    # 用 st.data_editor 允許編輯（Streamlit 1.17+）
    edited_df = st.data_editor(df, num_rows="dynamic", key="editor")

    # 比較變更並同步到 Google Sheets
    if st.button("儲存所有變更"):
        # 清空現有資料（保留標題）
        SHEET.clear()
        SHEET.append_row(["日期", "分類", "金額", "備註"])  # 恢復標題

        # 寫入所有編輯後的資料
        for _, row in edited_df.iterrows():
            SHEET.append_row(row.tolist())
        st.success("💾 所有變更已儲存！")
else:
    st.info("尚無支出記錄。")