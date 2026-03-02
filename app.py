import streamlit as st
from PIL import Image
import easyocr
import numpy as np
import re

st.set_page_config(page_title="運彩辨識高手", layout="centered")
st.title("🏀 運彩多圖自動辨識")

# 強化載入邏輯
@st.cache_resource
def load_reader():
    try:
        # gpu=False 是雲端運行的必備設定
        return easyocr.Reader(['en'], gpu=False)
    except Exception as e:
        st.error(f"AI 引擎初始化失敗: {e}")
        return None

reader = load_reader()

uploaded_files = st.file_uploader("📸 上傳截圖", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if uploaded_files and reader:
    total_odds = 1.0
    for i, file in enumerate(uploaded_files):
        img = Image.open(file)
        # 縮小圖片尺寸，節省雲端記憶體防止崩潰
        img.thumbnail((800, 800)) 
        st.image(img, caption=f"圖片 {i+1}", width=300)
        
        with st.spinner('AI 辨識中...'):
            img_np = np.array(img)
            results = reader.readtext(img_np)
            
            detected = []
            for (_, text, _) in results:
                clean = re.sub(r'[^0-9.]', '', text)
                try:
                    val = float(clean)
                    if 1.1 <= val <= 10.0 and "." in clean:
                        detected.append(val)
                except: continue
            
            if detected:
                # 運彩賠率通常在後半段出現，取最後一個偵測到的數字往往最準
                res = detected[-1] 
                st.success(f"✅ 圖片 {i+1} 賠率: {res}")
                total_odds *= res
            else:
                st.warning(f"❌ 圖片 {i+1} 抓不到數字")

    if total_odds > 1.0:
        st.divider()
        final = round(total_odds, 2)
        st.metric("🔥 總賠率", f"{final}")
        amt = st.number_input("下注金額", value=100)
        st.info(f"💰 預計回報: {int(amt * final)} 元")
