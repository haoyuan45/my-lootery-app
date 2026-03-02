import streamlit as st
import pandas as pd
from datetime import datetime

# 網頁基本設定
st.set_page_config(page_title="運彩紀錄工具", layout="centered")

st.title("📝 運彩數據手動紀錄表")
st.write("請在下方輸入數據，點擊按鈕即可自動生成表格。")

# 1. 初始化表格儲存空間 (Session State)
if 'df_data' not in st.session_state:
    st.session_state.df_data = pd.DataFrame(columns=["時間", "項目", "分盤/讓分", "賠率"])

# 2. 輸入區域
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        input_item = st.selectbox("選擇項目", ["第一節大小", "第一節讓分", "全場大小", "全場讓分", "勝分差", "其他"])
        input_line = st.text_input("分盤數字 (例如: 54.5 或 -3.5)", placeholder="請輸入數字")
        
    with col2:
        # 取得目前時間
        current_time = datetime.now().strftime("%H:%M:%S")
        input_time = st.text_input("紀錄時間", value=current_time)
        input_odds = st.text_input("賠率 (例如: 1.70)", placeholder="請輸入賠率")

# 3. 功能按鈕
col_btn1, col_btn2 = st.columns([1, 1])

if col_btn1.button("➕ 加入表格", use_container_width=True):
    if input_line and input_odds:
        # 新增一筆資料
        new_row = {
            "時間": input_time,
            "項目": input_item,
            "分盤/讓分": input_line,
            "賠率": input_odds
        }
        # 更新表格
        st.session_state.df_data = pd.concat([st.session_state.df_data, pd.DataFrame([new_row])], ignore_index=True)
        st.toast("已成功加入！")
    else:
        st.error("請填寫分盤數字與賠率！")

if col_btn2.button("🗑️ 清空表格", use_container_width=True):
    st.session_state.df_data = pd.DataFrame(columns=["時間", "項目", "分盤/讓分", "賠率"])
    st.rerun()

st.divider()

# 4. 顯示表格結果
st.subheader("📋 數據總表")

if not st.session_state.df_data.empty:
    # 顯示表格
    st.dataframe(st.session_state.df_data, use_container_width=True)
    
    # 下載按鈕
    csv = st.session_state.df_data.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 下載此表格 (CSV/Excel)",
        data=csv,
        file_name=f"lottery_records_{datetime.now().strftime('%m%d')}.csv",
        mime="text/csv",
    )
else:
    st.info("目前表格內尚無資料。")

st.caption("提示：加入後可繼續輸入下一筆，表格會自動往下累積。")
