import streamlit as st
from PIL import Image
import easyocr
import numpy as np
import re

st.set_page_config(page_title="運彩多圖辨識版", layout="centered")
st.title("🏀 運彩多圖自動辨識系統")

# 初始化辨識器
@st.cache_resource
def load_reader():
    return easyocr.Reader(['ch_tra', 'en']) # 支援繁體中文與數字

reader = load_reader()

# 修改處：支援一次上傳多張
uploaded_files = st.file_uploader("請上傳一張或多張運彩截圖", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    total_combination_odds = 1.0
    st.subheader(f"共上傳 {len(uploaded_files)} 張圖片")

    for i, file in enumerate(uploaded_files):
        img = Image.open(file)
        st.image(img, caption=f"圖片 {i+1} 辨識中...", width=300)
        
        # 影像辨識
        img_np = np.array(img)
        results = reader.readtext(img_np)
        
        # 精準篩選：找尋符合 1.xx 格式的賠率數字
        detected_odds = []
        for (bbox, text, prob) in results:
            # 清理文字：只留數字和小數點
            clean_text = re.sub(r'[^0-9.]', '', text)
            try:
                val = float(clean_text)
                # 篩選合理的賠率範圍 (通常 1.2 ~ 4.5 之間較準確)
                if 1.2 <= val <= 5.0 and len(clean_text) >= 4:
                    detected_odds.append(val)
            except:
                continue
        
        # 顯示該張圖的結果
        if detected_odds:
            # 取信心水準最高或最像賠率的一個 (通常是第一個)
            best_odds = detected_odds[0]
            st.success(f"🖼️ 圖片 {i+1} 偵測到賠率：**{best_odds}**")
            total_combination_odds *= best_odds
        else:
            st.error(f"🖼️ 圖片 {i+1} 無法辨識出有效賠率，請確保數字清晰。")

    st.divider()
    
    # 最終總和計算
    if total_combination_odds > 1.0:
        final_odds = round(total_combination_odds, 2)
        st.balloons()
        st.metric("🔥 串關總賠率", f"{final_odds}")
        
        bet_amount = st.number_input("輸入下注金額", value=100, step=100)
        st.info(f"💰 預計回報：{int(bet_amount * final_odds)} 元")
