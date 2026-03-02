import streamlit as st
from PIL import Image, ImageOps
import pytesseract
import re

st.set_page_config(page_title="運彩小助手", layout="centered")

st.title("🏀 運彩截圖精準辨識")
st.write("上傳截圖後，我會嘗試過濾雜訊並抓取賠率。")

uploaded_file = st.file_uploader("📸 選擇截圖", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # 1. 讀取圖片
    img = Image.open(uploaded_file)
    
    # 2. 圖像預處理：轉為灰階並增加對比（這能幫助 OCR 看得更清楚）
    gray_img = ImageOps.grayscale(img)
    
    st.image(img, caption="原始截圖", use_container_width=True)
    
    with st.spinner('正在精準辨識中...'):
        # 3. OCR 設定：只允許讀取數字和小數點
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789.'
        text = pytesseract.image_to_string(gray_img, config=custom_config)
        
        # 4. 尋找符合賠率格式的數字 (例如 1.50 到 9.99 之間)
        odds_found = re.findall(r'[1-9]\.\d{2}', text)
        
        # 去除重複抓到的數字
        odds_found = list(dict.fromkeys(odds_found))

    if len(odds_found) >= 2:
        st.success(f"✅ 成功辨識出 {len(odds_found)} 個賠率！")
        
        # 讓使用者勾選哪兩個才是對的（防止抓錯數字）
        selected_odds = st.multiselect("請選取正確的兩個賠率：", odds_found, default=odds_found[:2])
        
        if len(selected_odds) == 2:
            o1, o2 = float(selected_odds[0]), float(selected_odds[1])
            total = round(o1 * o2, 2)
            st.metric("二串一總賠率", f"{total}", delta=f"{o1} x {o2}")
        else:
            st.info("請在上方選單中勾選兩個數字來計算。")
    else:
        st.error("❌ 辨識失敗或數字不足。")
        st.write("抓到的文字內容為：", text) # 顯示抓到的東西方便除錯
        
        # 備用手動輸入
        col1, col2 = st.columns(2)
        o1 = col1.number_input("手動輸入賠率 1", value=1.75, step=0.01)
        o2 = col2.number_input("手動輸入賠率 2", value=1.75, step=0.01)
        st.warning(f"手動計算結果：{round(o1 * o2, 2)}")
