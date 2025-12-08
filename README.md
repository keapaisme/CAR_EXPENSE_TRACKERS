簡介：這個專案是運用AI在2小時內完成，我先給QWEN下面說明，然後按照提示一步步完成
 "我想用PYTHON寫一個資料庫程式，
  功能要求：可增刪修。
  資料庫用 google SHEET, 
  介面用streamlit.
  請一步一步教用建立資料庫程式。
  可否列三個主題供我選擇後開始 "

這個專案目的：
想測試是否能利用AI工具完成一個專案，其落地程度？難易度？所花費的時間？利用實作了解並記錄一個由AI指導從無到有的過程

這個程式具備：
  資料庫整合（Google Sheets）
  前端介面（Streamlit）
  雲端部署（Streamlit Cloud）
  行動裝置相容
  完整 CRUD 功能

以下也是QWEN代為制作的MarkDown:
# 💰 個人支出記錄系統

> 用 Python + Streamlit + Google Sheets 打造的輕量級記帳工具，支援**新增、編輯、刪除、統計**，並可**在手機與電腦上隨時存取**！

[![Demo](https://img.shields.io/badge/線上Demo-Streamlit-blue?logo=streamlit)](https://expense-tracker-34hwuzxtutel4zlasvgcdu.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## 🌟 功能特色

- ✅ **跨平台使用**：桌面 / 手機瀏覽器皆可操作（已測試 iPhone 11/12, Redmi KC40）
- ✅ **即時同步**：所有資料儲存於 Google Sheets，永不遺失
- ✅ **直覺介面**：表格編輯 + 日期選擇器 + 金額輸入
- ✅ **財務統計**：總支出 + 分類圖表（未來可擴充）
- ✅ **完全免費**：使用 Streamlit Cloud 免費部署

## 🖥️ 線上 Demo

👉 [點此開啟線上版本](https://expense-tracker-34hwuzxtutel4zlasvgcdu.streamlit.app/)

> 💡 首次載入可能需要 5-10 秒（Streamlit Cloud 冷啟動）

## 📸 介面預覽

| 桌面版                                             | 手機版（iPhone） |
|-------------------------------------------------|------------------|
| ![Desktop](https://photos.app.goo.gl/PSpwe7t1u6VGz1m9A) | ![Mobile](https://photos.app.goo.gl/xYVnb32V9EGQZeXJ6) |

## 🛠️ 本機開發

### 前置需求
- Python 3.9+
- Google Cloud Service Account（[教學](https://docs.gspread.org/en/latest/oauth2.html)）

### 安裝步驟
```bash
# 1. 克隆專案
git clone https://github.com/your-username/expense-tracker.git
cd expense-tracker

# 2. 建立虛擬環境（可選但推薦）
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 3. 安裝套件
pip install -r requirements.txt

# 4. 放入你的 Google 憑證
# 將 credentials.json 放到專案根目錄

# 5. 執行
streamlit run app.py