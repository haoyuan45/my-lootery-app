import streamlit as st
from PIL import Image, ImageOps, ImageEnhance
import pytesseract
import pandas as pd
import re
from datetime import datetime

# 頁面基本設定
st.set_page_config(page_title="第一節運彩助手", layout="wide")

# 初始化歷史紀錄
if 'lottery_history' not in st.session_state:
    st.session_state.lottery_history = []

st.title("📋 第一節數據自動轉表格")
st.write("上傳截圖後，我會強化辨識「第一節」數據。若辨識成功會自動填入，失敗則可手動修正。")

uploaded_file = st.file_uploader("📸 上傳第一節截圖", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="原始截圖", use_container_width=True)
    
    with st.spinner('正在強化辨識第一節數據...'):
        # --- 圖片預處理強化 ---
        # 轉灰階 -> 提高對比度 -> 銳利化
        gray = ImageOps.grayscale(img)
        enhancer = ImageEnhance.Contrast(gray)
        gray = enhancer.enhance(2.0) 
        
        # 辨識文字
        text = pytesseract.image_to_string(gray, lang='chi_tra+eng', config='--psm 6')
        
        # 提取邏輯
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # 預設值（給手動輸入框用）
        auto_val = ""
        auto_odds = ""
        auto_type = "第一節大小"

        lines = text.split('\n')
        for line in lines:
            # 只要包含「1節」或「一節」
            if "1" in line or "一" in line:
                # 抓取分盤 (例如 54.5 或 -3.5)
                v_match = re.search(r'[-+]?\d+\.\d', line)
                # 抓取賠率 (1.xx)
                o_match = re.search(r'[1-2]\.\d{2}', line)
                
                if v_match: auto_val = v_match.group()
                if o_match: auto_odds = o_match.group()
                if "讓" in line: auto_type = "第一節讓分"

    # --- 手動確認/輸入區 ---
    st.subheader("📝 數據確認 (自動辨識結果已預填)")
    c1, c2, c3, c4 = st.columns(4)
    
    f_date = c1.text_input("日期", value=current_time)
    f_type = c2.selectbox("項目", ["第一節大小", "第一節讓分", "第一節勝分差"], 
                         index=0 if auto_type == "第一節大小" else 1)
    f_val = c3.text_input("分盤數字 (如 54.5)", value=auto_val)
    f_odds = c4.text_input("賠率 (如 1.70)", value=auto_odds)
    
    if st.button("➕ 加入歷史紀錄表格"):
        if f_val and f_odds:
            st.session_state.lottery_history.append({
                "日期": f_date, "項目": f_type, "分盤": f_val, "賠率": f_odds
            })
            st.success("已存入表格！")
            st.rerun()
        else:
            st.error("請確保分盤與賠率欄位有數字喔！")

# --- 歷史紀錄表格 ---
st.divider()
st.subheader("📜 歷史紀錄表格 (總表)")

if st.session_state.lottery_history:
    df_history = pd.DataFrame(st.session_state.lottery_history)
    st.table(df_history) # 使用 table 顯示更像傳統表格
    
    csv = df_history.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 下載完整紀錄 (CSV/Excel)", csv, "history.csv", "text/csv")
    
    if st.button("🗑️ 清空紀錄"):
        st.session_state.lottery_history = []
        st.rerun()
else:
    st.info("目前尚無紀錄。")
