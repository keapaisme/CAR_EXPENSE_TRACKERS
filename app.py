# app.py
import streamlit as st
import pandas as pd
from datetime import datetime
import os
import json

# ===== 預先匯入可能用到的模組（避免在函式內重複 import）=====
try:
    from google.oauth2.service_account import Credentials
    import gspread

    GOOGLE_ENABLED = True
except ImportError:
    GOOGLE_ENABLED = False


# ===== 安全取得 Google 憑證（不觸發本機 secrets 錯誤）=====
def get_google_credentials():
    """優先使用本機 credentials.json；若不存在，則使用 Streamlit Secrets"""
    # 本機開發：使用 credentials.json
    if os.path.exists("credentials.json"):
        return Credentials.from_service_account_file("credentials.json")

    # 線上部署：使用 Streamlit Secrets
    try:
        creds_json = st.secrets["GOOGLE_CREDS"]
        creds_dict = json.loads(creds_json)
        return Credentials.from_service_account_info(creds_dict)
    except KeyError:
        raise FileNotFoundError("缺少 GOOGLE_CREDS Secrets（線上環境）")
    except Exception as e:
        raise Exception(f"載入憑證失敗: {e}")


# ===== 設定 Google Sheets =====
if GOOGLE_ENABLED:
    try:
        SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = get_google_credentials().with_scopes(SCOPE)
        gc = gspread.authorize(creds)

        # 🔑 請替換成你的 Google Sheet ID
        SPREADSHEET_ID = "1-j6aUXNyIq9I53HTECW39-aGSLa8t_V13lGFSSki_Rg"
        # 🔧 請替換成你的工作表名稱（預設中文版是「工作表1」，英文版是「Sheet1」）
        SHEET = gc.open_by_key(SPREADSHEET_ID).worksheet("draft_sheet")

    except Exception as e:
        st.error(f"❌ Google Sheets 連線失敗：{e}")
        st.stop()
else:
    st.error("缺少必要套件：請安裝 gspread, google-auth")
    st.stop()

# ===== Streamlit 頁面設定 =====
st.set_page_config(page_title="個人支出記錄系統", layout="centered")
st.title("💰 個人支出記錄系統")

# 環境提示（可選）
if not os.path.exists("credentials.json"):
    st.caption("🌐 線上版本")
else:
    st.caption("💻 本機測試版")


# ===== 讀取資料並轉換日期格式 =====
def load_data():
    try:
        records = SHEET.get_all_records()
        df = pd.DataFrame(records)
        if df.empty:
            df = pd.DataFrame(columns=["日期", "分類", "金額", "備註"])
        else:
            # 🔑 關鍵：把「日期」欄位從字串轉為 datetime
            df["日期"] = pd.to_datetime(df["日期"], errors="coerce").dt.date
            # 將金額轉為數字（避免文字）
            df["金額"] = pd.to_numeric(df["金額"], errors="coerce").fillna(0).astype(int)
        return df
    except Exception as e:
        st.error(f"讀取資料失敗：{e}")
        return pd.DataFrame(columns=["日期", "分類", "金額", "備註"])


# ===== 新增支出 =====
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
        if amount <= 0:
            st.warning("⚠️ 請輸入大於 0 的金額")
        else:
            new_row = [
                date_input.strftime("%Y-%m-%d"),
                category,
                amount,
                note
            ]
            SHEET.append_row(new_row)
            st.success("✅ 支出已新增！")
            st.rerun()

# ===== 顯示與編輯資料 =====
st.subheader("現有記錄")
df = load_data()

if not df.empty:
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        column_config={
            "日期": st.column_config.DateColumn(format="YYYY-MM-DD"),
            "金額": st.column_config.NumberColumn(format="$%d")
        },
        key="expense_editor"
    )

    if st.button("儲存所有變更"):
        try:
            SHEET.clear()
            SHEET.append_row(["日期", "分類", "金額", "備註"])

            for _, row in edited_df.iterrows():
                # 🔑 關鍵：把 date 轉回字串格式
                date_str = row["日期"].strftime("%Y-%m-%d") if pd.notna(row["日期"]) else ""
                amount_int = int(row["金額"]) if pd.notna(row["金額"]) else 0

                new_row = [
                    date_str,
                    row["分類"],
                    amount_int,
                    row["備註"]
                ]
                SHEET.append_row(new_row)

            st.success("💾 所有變更已儲存！")
            st.rerun()
        except Exception as e:
            st.error(f"儲存失敗：{e}")
else:
    st.info("尚無支出記錄。")

# ===== 顯示總支出 =====
if not df.empty:
    total = df["金額"].sum()
    st.success(f"📊 總支出：**${total:,}**")