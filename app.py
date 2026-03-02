import streamlit as st
from PIL import Image
import easyocr
import numpy as np

st.set_page_config(page_title="運彩自動辨識", layout="centered")
st.title("🏀 第一節賠率自動抓取")

# 初始化辨識器 (只需要執行一次)
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en']) # 辨識數字與英文

reader = load_reader()

uploaded_file = st.file_uploader("請上傳運彩截圖", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="正在辨識中...", use_container_width=True)
    
    # 轉換圖片格式給 EasyOCR 使用
    img_np = np.array(img)
    results = reader.readtext(img_np)
    
    # 這裡儲存所有抓到的數字
    all_numbers = []
    for (bbox, text, prob) in results:
        # 篩選看起來像賠率的數字 (例如 1.xx)
        try:
            val = float(text)
            if 1.0 < val < 5.0: # 通常賠率在這個區間
                all_numbers.append(val)
        except:
            continue

    st.divider()
    
    if len(all_numbers) >= 2:
        # 假設抓到的前兩個數字就是你要的
        odds_a = all_numbers[0]
        odds_b = all_numbers[1]
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("偵測賠率 1", f"{odds_a}")
        with col2:
            st.metric("偵測賠率 2", f"{odds_b}")
            
        total_odds = round(odds_a * odds_b, 2)
        st.success(f"🔥 自動計算二串一總賠率：{total_odds}")
        st.write(f"💰 投注 100 元預計回收：{int(100 * total_odds)} 元")
    else:
        st.warning("無法自動偵測到足夠的賠率數字，請確保截圖清晰且包含紅圈內的數值。")
        st.write("偵測到的文字內容：", [res[1] for res in results])
