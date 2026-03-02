import streamlit as st
from PIL import Image, ImageOps
import pytesseract
import pandas as pd
import re

st.set_page_config(page_title="運彩截圖秒轉表格", layout="wide")

st.title("⚡ 運彩截圖 -> 自動生成表格")
st.write("上傳截圖，我會直接把所有數字抓出來排成表！")

uploaded_file = st.file_uploader("📸 選擇截圖", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="原始截圖", use_container_width=True)
    
    with st.spinner('正在瘋狂掃描所有數字...'):
        # 1. 強化辨識：轉灰階 + 增加對比
        img_gray = ImageOps.grayscale(img)
        
        # 2. 辨識所有數字與點
        custom_config = r'--oem 3 --psm 11 -c tessedit_char_whitelist=0123456789.-'
        raw_text = pytesseract.image_to_string(img_gray, config=custom_config)
        
        # 3. 抓取所有 1.xx 到 2.xx 的數字 (賠率)
        odds = re.findall(r'[1-2]\.\d{2}', raw_text)
        # 抓取所有可能的分盤數字 (例如 54.5, 3.5)
        lines = re.findall(r'\d{1,3}\.\d', raw_text)
        
        # 4. 合併成一個清單
        all_data = sorted(list(set(odds + lines)))

    if all_data:
        st.success(f"✅ 自動抓到 {len(all_data)} 組數據！")
        
        # 5. 直接生成表格
        df = pd.DataFrame({
            "序號": range(1, len(all_data) + 1),
            "辨識出的數據": all_data,
            "用途說明": ["可能是賠率或分盤" for _ in all_data]
        })
        
        st.subheader("📊 自動整理結果")
        st.table(df) # 直接噴出表格
        
        # 下載按鈕
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 下載這份表格", csv, "lottery_data.csv", "text/csv")
    else:
        st.error("❌ 真的抓不到數字... 請確認截圖是否太模糊。")
        st.write("電腦看到的原始文字：", raw_text)

st.info("💡 為什麼之前沒顯示？因為之前的程式在找『精準的賠率』，結果把你的 54.5 給擋掉了。現在我通通都抓！")
