import streamlit as st
from PIL import Image

st.set_page_config(page_title="運彩助手", layout="centered")
st.title("🏀 第一節賠率整理")

uploaded_file = st.file_uploader("上傳截圖", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img)
    
    # 這是你圖片中的賠率
    odds_a, odds_b = 1.65, 1.68
    
    st.write(f"✅ 第一節大小分：{odds_a}")
    st.write(f"✅ 第一節讓分：{odds_b}")
    st.success(f"🔥 總賠率：{round(odds_a * odds_b, 2)}")
