import streamlit as st
from PIL import Image, ImageOps
import pytesseract
import pandas as pd
import re
from datetime import datetime

# 頁面基本設定
st.set_page_config(page_title="第一節運彩助手", layout="wide")

# 初始化歷史紀錄儲存空間
if 'lottery_history' not in st.session_state:
    st.session_state.lottery_history = []

st.title("🏀 第一節數據自動轉表格")
st.write("上傳截圖後，我會自動抓取「第一節」的大小分與讓分，並加入歷史紀錄。")

uploaded_file = st.file_uploader("📸 上傳第一節截圖", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="原始截圖", use_container_width=True)
    
    with st.spinner('正在過濾第一節數據...'):
        # 1. 圖片處理與辨識
        gray = ImageOps.grayscale(img)
        # 增加辨識繁體中文與數字
        text = pytesseract.image_to_string(gray, lang='chi_tra+eng', config='--psm 6')
        
        # 2. 定義提取邏輯
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        rows_to_add = []
        
        # 將文字拆成行來分析
        lines = text.split('\n')
        for line in lines:
            # 只找包含「第1節」或「第一節」的行
            if "1節" in line or "一節" in line:
                # 提取分盤數字 (例如 54.5, 3.5, -3.5)
                val_match = re.search(r'[-+]?\d+\.\d', line)
                # 提取賠率 (1.xx)
                odds_match = re.search(r'[1-2]\.\d{2}', line)
                
                if val_match and odds_match:
                    item_type = "第一節大小" if "大小" in line else "第一節讓分"
                    rows_to_add.append({
                        "日期": current_time,
                        "項目": item_type,
                        "分盤": val_match.group(),
                        "賠率": odds_match.group()
                    })

    # 3. 顯示本次辨識結果並確認
    if rows_to_add:
        st.subheader("📋 本次偵測到的第一節數據")
        temp_df = pd.DataFrame(rows_to_add)
        st.table(temp_df)
        
        if st.button("確認無誤，存入歷史表格"):
            st.session_state.lottery_history.extend(rows_to_add)
            st.success("已存入下方歷史紀錄！")
            st.rerun()
    else:
        st.warning("未能自動辨識出第一節數據，請手動輸入。")
        with st.expander("手動新增數據"):
            col1, col2, col3 = st.columns(3)
            m_type = col1.selectbox("項目", ["第一節大小", "第一節讓分"])
            m_val = col2.text_input("分盤數字", value="54.5")
            m_odds = col3.text_input("賠率", value="1.70")
            if st.button("手動加入"):
                st.session_state.lottery_history.append({
                    "日期": current_time, "項目": m_type, "分盤": m_val, "賠率": m_odds
                })
                st.rerun()

# 4. 顯示永久歷史紀錄表格
st.divider()
st.subheader("📜 歷史紀錄表格 (總表)")

if st.session_state.lottery_history:
    df_history = pd.DataFrame(st.session_state.lottery_history)
    st.dataframe(df_history, use_container_width=True) # 使用互動式表格
    
    # 下載功能
    csv = df_history.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 下載完整歷史紀錄 (Excel/CSV)", csv, "history.csv", "text/csv")
    
    if st.button("🗑️ 清空紀錄"):
        st.session_state.lottery_history = []
        st.rerun()
else:
    st.info("目前尚無紀錄。")
