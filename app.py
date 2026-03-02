import streamlit as st
from PIL import Image
import pytesseract
import pandas as pd
import re

st.set_page_config(page_title="運彩賠率自動整理", layout="wide")

st.title("📋 運彩賠率自動轉表格")
st.write("上傳截圖，我會自動提取所有賠率並整理成表格。")

uploaded_file = st.file_uploader("📸 上傳運彩截圖", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="原始截圖", use_container_width=True)
    
    with st.spinner('正在掃描資訊中...'):
        # 使用 PSM 6 適合按行讀取文字
        custom_config = r'--oem 3 --psm 6'
        raw_text = pytesseract.image_to_string(img, lang='chi_tra+eng', config=custom_config)
        
        # 尋找所有 1.xx 或 2.xx 的賠率數字
        odds_found = re.findall(r'[1-2]\.\d{2}', raw_text)
        
        # 整理成表格資料
        data = []
        # 每兩個賠率一組（通常是 大/小 或 主/客）
        for i in range(0, len(odds_found) - 1, 2):
            data.append({
                "項目": f"選項 {i//2 + 1}",
                "賠率 A": odds_found[i],
                "賠率 B": odds_found[i+1]
            })

    if data:
        st.success("✅ 已自動整理成表格：")
        df = pd.DataFrame(data)
        
        # 顯示表格
        st.table(df)
        
        # 下載功能
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 下載表格 (CSV)", csv, "odds_table.csv", "text/csv")
    else:
        st.error("❌ 找不到賠率數字，請確認截圖內容是否清晰。")
        with st.expander("查看原始辨識文字"):
            st.text(raw_text)

    st.info("💡 提示：如果表格內容有誤，可能是 OCR 抓到了讓分數（如 3.5）。你可以對照原始截圖確認。")
