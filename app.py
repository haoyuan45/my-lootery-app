import streamlit as st
import pandas as pd
from datetime import datetime

# 設定網頁標題與佈局
st.set_page_config(page_title="運彩紀錄工具", layout="wide")

st.title("📋 運彩投注歷史紀錄表")
st.write("手動輸入賠率資訊，系統會自動幫你整理成歷史表格。")

# --- 核心功能：初始化儲存空間 ---
# 使用 session_state 確保在同一次使用中，資料可以持續累計
if 'history_data' not in st.session_state:
    st.session_state.history_data = []

# --- 第一部分：資料輸入區 ---
with st.expander("➕ 新增一筆紀錄", expanded=True):
    # 自動抓取現在的時間
    current_dt = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
    
    with col1:
        date_input = st.text_input("日期時間", value=current_dt)
    with col2:
        item_input = st.text_input("項目 (例如：第一節大小)", placeholder="請輸入項目")
    with col3:
        line_input = st.text_input("分盤/讓分", placeholder="54.5")
    with col
