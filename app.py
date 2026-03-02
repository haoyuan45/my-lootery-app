import streamlit as st
from PIL import Image
import pytesseract
import re

st.set_page_config(page_title="運彩小助手", layout="centered")

st.title("🏀 運彩截圖自動辨識")
st.write("請上傳運彩官網或 App 的截圖，我會幫你抓出賠率！")

uploaded_file = st.file_uploader("📸 選擇截圖", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # 顯示上傳的圖片
    img = Image.open(uploaded_file)
    st.image(img, caption="已上傳的截圖", use_container_width=True)
    
    with st.spinner('正在辨識數字中...'):
        # 使用 OCR 辨識文字
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(img, config=custom_config)
        
        # 使用正則表達式尋找像 1.65, 1.75 這樣的數字
        # 這邊會抓出所有小數點兩位的數字
        odds_found = re.findall(r'\d\.\d{2}', text)
        
    if len(odds_found) >= 2:
        # 假設前兩個抓到的數字就是你要的
        odds_a = float(odds_found[0])
        odds_b = float(odds_found[1])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("辨識賠率 A", f"{odds_a}")
        with col2:
            st.metric("辨識賠率 B", f"{odds_b}")
            
        total_odds = round(odds_a * odds_b, 2)
        st.success(f"🔥 自動計算二串一總賠率：{total_odds}")
        st.info("💡 提示：如果辨識不準，請確保截圖清晰且背景單純。")
    else:
        st.warning("無法從圖片中辨識出足夠的賠率數字，請手動輸入或重新截圖。")
        # 備用手動輸入
        odds_a = st.number_input("手動輸入賠率 A", value=1.75)
        odds_b = st.number_input("手動輸入賠率 B", value=1.75)
        st.write(f"計算結果：{round(odds_a * odds_b, 2)}")
