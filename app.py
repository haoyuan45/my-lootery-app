import streamlit as st
from PIL import Image, ImageOps
import pytesseract
import re

st.set_page_config(page_title="運彩精準辨識", layout="centered")

st.title("🏀 運彩截圖區域辨識")
st.write("上傳截圖後，我會嘗試裁切特定區域來抓取賠率。")

uploaded_file = st.file_uploader("📸 選擇截圖", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # 1. 讀取圖片
    img = Image.open(uploaded_file)
    w, h = img.size
    
    st.image(img, caption="原始截圖", use_container_width=True)
    
    # 2. 定義裁切區域 (這是關鍵！)
    # 這裡的比例需要根據您的截圖版面調整。
    # 假設賠率通常在圖片的右側中段。
    # 格式為 (左, 上, 右, 下)
    # 我們這裡先定義兩個可能的賠率區域。
    
    # 區域 A (例如：第一節大小分賠率)
    # 裁切圖片右側 60% 到 90%，上方 40% 到 55% 的區域
    crop_box_a = (w * 0.6, h * 0.4, w * 0.9, h * 0.55)
    
    # 區域 B (例如：第一節讓分賠率)
    # 裁切圖片右側 60% 到 90%，上方 55% 到 70% 的區域
    crop_box_b = (w * 0.6, h * 0.55, w * 0.9, h * 0.7)
    
    cropped_img_a = img.crop(crop_box_a)
    cropped_img_b = img.crop(crop_box_b)
    
    # 顯示裁切後的區域，方便除錯
    col1, col2 = st.columns(2)
    with col1:
        st.image(cropped_img_a, caption="裁切區域 A", use_container_width=True)
    with col2:
        st.image(cropped_img_b, caption="裁切區域 B", use_container_width=True)
        
    with st.spinner('正在精準辨識中...'):
        # 3. 圖像預處理與 OCR 設定
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789.'
        
        # 辨識區域 A
        gray_a = ImageOps.grayscale(cropped_img_a)
        text_a = pytesseract.image_to_string(gray_a, config=custom_config)
        odds_a_found = re.findall(r'[1-9]\.\d{2}', text_a)
        
        # 辨識區域 B
        gray_b = ImageOps.grayscale(cropped_img_b)
        text_b = pytesseract.image_to_string(gray_b, config=custom_config)
        odds_b_found = re.findall(r'[1-9]\.\d{2}', text_b)
        
    # 4. 顯示結果
    if odds_a_found and odds_b_found:
        o1 = float(odds_a_found[0])
        o2 = float(odds_b_found[0])
        total = round(o1 * o2, 2)
        st.success(f"✅ 成功辨識！區域 A：{o1}，區域 B：{o2}")
        st.metric("二串一總賠率", f"{total}", delta=f"{o1} x {o2}")
    else:
        st.error("❌ 裁切區域內無法辨識出足夠的賠率數字。")
        st.write("區域 A 辨識內容：", text_a)
        st.write("區域 B 辨識內容：", text_b)
        st.info("💡 提示：這通常是因為裁切位置不對，需要調整 `crop_box` 的比例。")
        
        # 備用手動輸入
        col1, col2 = st.columns(2)
        o1 = col1.number_input("手動輸入賠率 A", value=1.75, step=0.01)
        o2 = col2.number_input("手動輸入賠率 B", value=1.75, step=0.01)
        st.warning(f"手動計算結果：{round(o1 * o2, 2)}")
