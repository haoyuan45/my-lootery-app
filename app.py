import streamlit as st
from PIL import Image
import pytesseract
import pandas as pd
import re

st.set_page_config(page_title="運彩自動整理助手", layout="wide")

st.title("📋 運彩截圖 -> 自動轉表格")
st.write("請上傳截圖，我會自動提取所有賠率數字並整理。")

uploaded_file = st.file_uploader("📸 選擇截圖", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # 讀取並顯示原始圖片
    img = Image.open(uploaded_file)
    st.image(img, caption="原始截圖", use_container_width=True)
    
    with st.spinner('正在分析圖片內容...'):
        # OCR 辨識文字 (含中文與英文數字)
        text = pytesseract.image_to_string(img, lang='chi_tra+eng')
        
        # 使用正規表達式抓取賠率 (找 1.xx 到 2.xx 的數字)
        odds_found = re.findall(r'[1-2]\.\d{2}', text)
        
        # 整理成表格格式
        table_data = []
        for i in range(0, len(odds_found)):
            table_data.append({
                "序號": i + 1,
                "偵測到的賠率": odds_found[i],
                "類型": "待確認"
            })

    if table_data:
        st.success(f"✅ 成功辨識出 {len(odds_found)} 個賠率數字！")
        
        # 轉換成 Pandas 表格
        df = pd.DataFrame(table_data)
        
        # 顯示互動式表格
        st.subheader("📊 賠率整理結果")
        st.dataframe(df, use_container_width=True)
        
        # 提供下載按鈕
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 下載此表格 (Excel/CSV)", csv, "odds.csv", "text/csv")
    else:
        st.error("❌ 找不到賠率數字，請確認截圖是否清晰。")
        with st.expander("查看辨識到的原始文字"):
            st.text(text)

st.divider()
st.info("💡 提示：如果辨識不夠準確，建議截圖時不要包含太多無關內容。")
