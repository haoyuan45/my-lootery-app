import streamlit as st
from PIL import Image, ImageOps
import pytesseract
import pandas as pd
import re

st.set_page_config(page_title="運彩截圖助手", layout="wide")

st.title("📊 運彩截圖 -> 自動生成表格")

uploaded_file = st.file_uploader("📸 上傳你的運彩截圖", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="原始截圖", use_container_width=True)
    
    with st.spinner('正在從圖片提取數據...'):
        # 1. 圖片預處理（增加辨識度）
        gray = ImageOps.grayscale(img)
        
        # 2. OCR 辨識
        # 使用 psm 6 適合表格型態的文字
        custom_config = r'--oem 3 --psm 6'
        raw_text = pytesseract.image_to_string(gray, lang='eng+chi_tra', config=custom_config)
        
        # 3. 抓取所有數字（包含賠率如 1.70 和 分盤如 54.5）
        # 邏輯：找所有帶小數點的數字
        numbers = re.findall(r'\d+\.\d{1,2}', raw_text)
        
    if numbers:
        st.success(f"✅ 成功抓到 {len(numbers)} 組數據！")
        
        # 4. 整理成表格
        # 我們把抓到的數字兩兩一組排列，通常剛好會是 [分盤, 賠率]
        rows = []
        for i in range(0, len(numbers) - 1, 2):
            rows.append({
                "組別": f"項目 {i//2 + 1}",
                "數據 A (可能是分盤)": numbers[i],
                "數據 B (可能是賠率)": numbers[i+1]
            })
            
        df = pd.DataFrame(rows)
        
        st.subheader("📋 自動生成的表格")
        st.table(df) # 直接顯示表格
        
        # 提供下載
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 下載此表格 (CSV)", csv, "lottery_table.csv", "text/csv")
    else:
        st.error("❌ 抓不到數字，請確保截圖中的賠率清晰可見。")
        with st.expander("查看電腦辨識出的原始文字"):
            st.text(raw_text)

st.divider()
st.info("💡 如果表格數據位移了，通常是因為圖片中還有其他雜訊數字，你可以參考原始截圖對照。")
