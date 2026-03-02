import streamlit as st
from PIL import Image
import pytesseract
import pandas as pd
import re

st.set_page_config(page_title="運彩精準整理", layout="centered")

st.title("📋 紅圈賠率自動轉表格")
st.write("請上傳截圖，我會只抓取紅圈區域的賠率並整理。")

uploaded_file = st.file_uploader("📸 上傳截圖", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    w, h = img.size
    st.image(img, caption="原始截圖", use_container_width=True)
    
    # 根據你的紅圈位置設定裁切比例 (左, 上, 右, 下)
    # 區域 1：上方紅圈 (第一節大小)
    box1 = (w * 0.5, h * 0.15, w * 0.95, h * 0.25) 
    # 區域 2：下方紅圈 (第一節讓分)
    box2 = (w * 0.1, h * 0.65, w * 0.5, h * 0.75)

    with st.spinner('掃描紅圈區域...'):
        # 提取區域並辨識
        def get_odds(box):
            crop = img.crop(box)
            # 轉灰階增加準確度
            text = pytesseract.image_to_string(crop, config=r'--psm 6 -c tessedit_char_whitelist=0123456789.')
            match = re.search(r'[1-2]\.\d{2}', text)
            return match.group(0) if match else "辨識失敗"

        odds1 = get_
