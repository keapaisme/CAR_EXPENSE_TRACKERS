# app.py
import streamlit as st
import pandas as pd
from datetime import datetime
import os
import json

# ===== 匯入 Google 相關套件 =====
try:
    from google.oauth2.service_account import Credentials
    import gspread

    GOOGLE_ENABLED = True
except ImportError:
    GOOGLE_ENABLED = False
    st.error("缺少必要套件：請安裝 gspread, google-auth")
    st.stop()


# ===== 自動判斷憑證來源 =====
def get_google_credentials():
    if os.path.exists("credentials.json"):
        return Credentials.from_service_account_file("credentials.json")
    try:
        creds_json = st.secrets["GOOGLE_CREDS"]
        creds_dict = json.loads(creds_json)
        return Credentials.from_service_account_info(creds_dict)
    except Exception as e:
        raise FileNotFoundError(
            "找不到 Google 憑證！\n"
            "• 本機：確保 credentials.json 與 app.py 同目錄\n"
            "• 線上：設定 Streamlit Secrets (GOOGLE_CREDS)"
        )


# ===== 設定 Google Sheets =====
try:
    SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = get_google_credentials().with_scopes(SCOPE)
    gc = gspread.authorize(creds)

    # 🔑 請替換成你的 Spreadsheet ID
    SPREADSHEET_ID = "1-j6aUXNyIq9I53HTECW39-aGSLa8t_V13lGFSSki_Rg"
    # 🔧 請確認工作表名稱（中文版預設是「工作表1」）
    SHEET = gc.open_by_key(SPREADSHEET_ID).worksheet("draft_sheet")

except Exception as e:
    st.error(f"❌ Google Sheets 連線失敗：{e}")
    st.stop()


# ===== 函式：讀取支出資料 =====
def load_data():
    try:
        records = SHEET.get_all_records()
        df = pd.DataFrame(records)
        if df.empty:
            df = pd.DataFrame(columns=["日期", "分類", "金額", "備註"])
        else:
            df["日期"] = pd.to_datetime(df["日期"], errors="coerce").dt.date
            df["金額"] = pd.to_numeric(df["金額"], errors="coerce").fillna(0).astype(int)
        return df
    except Exception as e:
        st.error(f"讀取資料失敗：{e}")
        return pd.DataFrame(columns=["日期", "分類", "金額", "備註"])


# ===== 函式：讀取分類 =====
def load_categories():
    try:
        cat_sheet = gc.open_by_key(SPREADSHEET_ID).worksheet("categories")
        records = cat_sheet.get_all_records()
        df = pd.DataFrame(records)
        if df.empty:
            return ["餐飲", "交通", "娛樂", "購物", "醫療", "其他"]
        else:
            return df["分類名稱"].dropna().tolist()
    except Exception as e:
        st.warning(f"讀取分類失敗，使用預設分類：{e}")
        return ["餐飲", "交通", "娛樂", "購物", "醫療", "其他"]


# ===== 函式：儲存分類 =====
def save_categories(category_list):
    try:
        cat_sheet = gc.open_by_key(SPREADSHEET_ID).worksheet("categories")
        cat_sheet.clear()
        cat_sheet.append_row(["分類名稱"])
        for cat in category_list:
            if cat.strip():
                cat_sheet.append_row([cat.strip()])
    except Exception as e:
        st.error(f"儲存分類失敗：{e}")


# ===== Streamlit UI 開始 =====
st.set_page_config(page_title="個人支出記錄系統", layout="centered")
st.title("💰 個人支出記錄系統")

# 環境提示
if not os.path.exists("credentials.json"):
    st.caption("🌐 線上版本")
else:
    st.caption("💻 本機測試版")

# ===== 新增支出表單 =====
with st.form("新增支出"):
    st.subheader("新增支出")
    col1, col2 = st.columns(2)
    with col1:
        date_input = st.date_input("日期", value=datetime.today())
        amount = st.number_input("金額", min_value=0, step=10)
    with col2:
        categories = load_categories()  # ✅ 安全呼叫（函式已定義）
        category = st.selectbox("分類", categories)
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

# ===== 管理分類 =====
st.subheader("🏷️ 管理分類")
categories = load_categories()

col1, col2 = st.columns([3, 1])
with col1:
    new_category = st.text_input("新增分類", placeholder="例如：房租、保險...", label_visibility="collapsed")
with col2:
    if st.button("➕ 新增"):
        if new_category.strip() and new_category.strip() not in categories:
            categories.append(new_category.strip())
            save_categories(categories)
            st.rerun()
        elif new_category.strip() in categories:
            st.warning("⚠️ 分類已存在")
        else:
            st.warning("⚠️ 請輸入分類名稱")

# 顯示分類清單
if categories:
    st.write("**目前分類：**")
    for i, cat in enumerate(categories):
        col_cat, col_del = st.columns([4, 1])
        with col_cat:
            st.write(f"`{cat}`")
        with col_del:
            if st.button("🗑️", key=f"del_{i}", help=f"刪除 {cat}"):
                categories.remove(cat)
                save_categories(categories)
                st.rerun()

# ===== 查詢功能 =====
st.subheader("🔍 查詢支出")

# 載入資料與分類
df_all = load_data()
all_categories = load_categories()

if df_all.empty:
    st.info("尚無資料可供查詢。")
else:
    # 建立查詢條件
    col1, col2, col3 = st.columns(3)

    with col1:
        # 分類多選（預設全選）
        selected_cats = st.multiselect(
            "分類",
            options=all_categories,
            default=all_categories
        )

    with col2:
        # 日期範圍
        min_date = df_all["日期"].min()
        max_date = df_all["日期"].max()
        start_date = st.date_input("開始日期", value=min_date, min_value=min_date, max_value=max_date)
        end_date = st.date_input("結束日期", value=max_date, min_value=min_date, max_value=max_date)

    with col3:
        # 備註關鍵字（模糊搜尋）
        keyword = st.text_input("備註關鍵字", placeholder="例如：超市、Uber...")

    # 按下查詢按鈕才執行（避免每次輸入都過濾）
    if st.button("🔎 查詢"):
        # 複製原始資料
        filtered_df = df_all.copy()

        # 1. 依分類篩選
        if selected_cats:
            filtered_df = filtered_df[filtered_df["分類"].isin(selected_cats)]
        else:
            filtered_df = pd.DataFrame(columns=df_all.columns)  # 無分類時顯示空

        # 2. 依日期區間篩選
        if not filtered_df.empty:
            filtered_df["日期"] = pd.to_datetime(filtered_df["日期"])
            mask = (filtered_df["日期"].dt.date >= start_date) & (filtered_df["日期"].dt.date <= end_date)
            filtered_df = filtered_df[mask]

        # 3. 依備註關鍵字篩選（模糊搜尋，忽略大小寫）
        if keyword and not filtered_df.empty:
            filtered_df = filtered_df[
                filtered_df["備註"].astype(str).str.contains(keyword, case=False, na=False)
            ]

        # 顯示結果
        if filtered_df.empty:
            st.warning("⚠️ 查無符合條件的記錄。")
        else:
            st.success(f"✅ 找到 {len(filtered_df)} 筆記錄")

            # 顯示表格（唯讀，因查詢結果不應直接編輯）
            st.dataframe(
                filtered_df.sort_values("日期", ascending=False),
                use_container_width=True
            )

            # 顯示小計
            total_filtered = filtered_df["金額"].sum()
            st.info(f"📌 查詢結果總支出：**${int(total_filtered):,}**")

# ===== 顯示與編輯現有資料 =====
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
                date_str = row["日期"].strftime("%Y-%m-%d") if pd.notna(row["日期"]) else ""
                amount_int = int(row["金額"]) if pd.notna(row["金額"]) else 0
                new_row = [date_str, row["分類"], amount_int, row["備註"]]
                SHEET.append_row(new_row)
            st.success("💾 所有變更已儲存！")
            st.rerun()
        except Exception as e:
            st.error(f"儲存失敗：{e}")
else:
    st.info("尚無支出記錄。")

# ===== 顯示總支出 =====
st.divider()
st.subheader("💰 總計概覽")
try:
    df_total = load_data()
    if not df_total.empty and "金額" in df_total.columns:
        df_total["金額"] = pd.to_numeric(df_total["金額"], errors="coerce")
        total = df_total["金額"].sum()
        if pd.notna(total) and total > 0:
            st.success(f"📊 總支出：**${int(total):,}**")
        else:
            st.info("尚未記錄有效支出。")
    else:
        st.info("尚無支出記錄。")
except Exception as e:
    st.warning(f"計算總支出時發生問題：{str(e)[:100]}")