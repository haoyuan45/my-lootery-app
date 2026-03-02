import streamlit as st
from PIL import Image, ImageOps, ImageEnhance
import pytesseract
import pandas as pd
import re
from datetime import datetime

st.set_page_config(page_title="第一節運彩助手", layout="wide")

# 初始化歷史紀錄與辨識快取
if 'lottery_history' not in st.session_state:
    st.session_state.lottery_history = []
if 'ocr_cache' not in st.session_state:
    st.session_state.ocr_cache = {"第一節大小": {"val": "", "odds": ""}, "第一節讓分": {"val": "", "odds": ""}}

st.title("📋 第一節數據連動表格")
st.write("上傳截圖後，切換項目時「分盤」與「賠率」會自動跟著跳轉。")

uploaded_file = st.file_uploader("📸 上傳第一節截圖", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="原始截圖", use_container_width=True)
    
    with st.spinner('正在深度掃描所有第一節數據...'):
        # 圖片強化處理
        gray = ImageOps.grayscale(img)
        gray = ImageEnhance.Contrast(gray).enhance(2.0)
        text = pytesseract.image_to_string(gray, lang='chi_tra+eng', config='--psm 6')
        
        # 重置快取
        st.session_state.ocr_cache = {"第一節大小": {"val": "", "odds": ""}, "第一節讓分": {"val": "", "odds": ""}}
        
        lines = text.split('\n')
        for line in lines:
            if "1" in line or "一" in line:
                v_match = re.search(r'[-+]?\d+\.\d', line)
                o_match = re.search(r'[1-2]\.\d{2}', line)
                
                if "大小" in line and v_match and o_match:
                    st.session_state.ocr_cache["第一節大小"] = {"val": v_match.group(), "odds": o_match.group()}
                elif "讓" in line and v_match and o_match:
                    st.session_state.ocr_cache["第一節讓分"] = {"val": v_match.group(), "odds": o_match.group()}

# --- 數據確認與聯動區 ---
st.subheader("📝 數據確認 (切換項目會自動帶入對應數字)")
c1, c2, c3, c4 = st.columns(4)

current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
f_date = c1.text_input("日期", value=current_time)

# 1. 項目切換
f_type = c2.selectbox("項目", ["第一節大小", "第一節讓分"])

# 2. 根據項目自動取得快取中的數字
default_val = st.session_state.ocr_cache[f_type]["val"]
default_odds = st.session_state.ocr_cache[f_type]["odds"]

# 3. 顯示輸入框 (使用者仍可手動微調)
f_val = c3.text_input("分盤數字", value=default_val, key=f"val_{f_type}")
f_odds = c4.text_input("賠率", value=default_odds, key=f"odds_{f_type}")

if st.button("➕ 加入歷史紀錄表格"):
    if f_val and f_odds:
        st.session_state.lottery_history.append({
            "日期": f_date, "項目": f_type, "分盤": f_val, "賠率": f_odds
        })
        st.success(f"已加入 {f_type} 紀錄！")
        st.rerun()
    else:
        st.error("該項目未偵測到數字，請手動輸入後再加入。")

# --- 歷史紀錄總表 ---
st.divider()
st.subheader("📜 歷史紀錄表格 (總表)")

if st.session_state.lottery_history:
    df_history = pd.DataFrame(st.session_state.lottery_history)
    st.table(df_history)
    
    csv = df_history.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 下載完整紀錄 (CSV)", csv, "history.csv", "text/csv")
    
    if st.button("🗑️ 清空紀錄"):
        st.session_state.lottery_history = []
        st.rerun()
