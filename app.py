import streamlit as st
from PIL import Image
import easyocr
import numpy as np
import re

# 1. 網頁基本設定
st.set_page_config(page_title="運彩多圖辨識助手", layout="centered")
st.title("🏀 運彩多圖自動辨識系統")
st.write("上傳多張截圖，AI 會自動抓取賠率並計算串關。")

# 2. 初始化 OCR 辨識器 (加上 cache 避免重複載入)
@st.cache_resource
def load_reader():
    # gpu=False 是關鍵，因為 Streamlit Cloud 沒有顯卡
    return easyocr.Reader(['ch_tra', 'en'], gpu=False)

try:
    reader = load_reader()
except Exception as e:
    st.error(f"AI 模型載入失敗，請檢查 requirements.txt。錯誤: {e}")

# 3. 上傳檔案區 (支援多圖)
uploaded_files = st.file_uploader("📸 請上傳一張或多張運彩截圖", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    total_combination_odds = 1.0
    st.subheader(f"✅ 已上傳 {len(uploaded_files)} 張圖片")
    
    # 建立一個容器來顯示結果
    for i, file in enumerate(uploaded_files):
        with st.expander(f"查看圖片 {i+1} 辨識細節", expanded=True):
            img = Image.open(file)
            st.image(img, use_container_width=True)
            
            # 開始辨識
            with st.spinner(f'正在辨識圖片 {i+1}...'):
                img_np = np.array(img)
                results = reader.readtext(img_np)
                
                # 精準篩選賠率 (找尋 1.xx ~ 5.xx 的數字)
                detected_odds = []
                for (bbox, text, prob) in results:
                    # 只留數字和小數點
                    clean_text = re.sub(r'[^0-9.]', '', text)
                    try:
                        val = float(clean_text)
                        # 篩選合理賠率範圍，且字數通常大於 3 (例如 1.75)
                        if 1.1 <= val <= 8.0 and len(clean_text) >= 3:
                            detected_odds.append(val)
                    except:
                        continue
                
                if detected_odds:
                    # 取第一個偵測到的合理數字作為賠率
                    best_odds = detected_odds[0]
                    st.success(f"🎯 偵測到賠率：**{best_odds}**")
                    total_combination_odds *= best_odds
                else:
                    st.warning(f"⚠️ 圖片 {i+1} 沒找到明顯賠率，請確保數字清晰且沒有被遮擋。")

    # 4. 總結計算
    st.divider()
    if total_combination_odds > 1.0:
        final_odds = round(total_combination_odds, 2)
        st.balloons() # 噴彩帶慶祝
        
        # 顯示大大的結果
        col1, col2 = st.columns(2)
        col1.metric("🔥 串關總賠率", f"{final_odds}")
        
        bet_amount = st.number_input("💰 輸入下注金額", value=100, step=100)
        potential_profit = int(bet_amount * final_odds)
        
        col2.metric("💵 預計回報", f"{potential_profit} 元")
        
        st.info(f"💡 計算公式：{' x '.join(['賠率']*len(uploaded_files))} = {final_odds}")
    else:
        st.info("請上傳帶有賠率數字的截圖開始計算。")

else:
    st.info("💡 提示：你可以一次選取多張照片上傳，我會幫你自動串關。")
