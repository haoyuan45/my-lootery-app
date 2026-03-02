import streamlitimport streamlit as st
from PIL import Image
import pytesseract
import pandas as pd
import re

st.set_page_config(page_title="運彩賠率表格工具", layout="centered")

st.title("📋 運彩賠率快速整理")
st.write("上傳截圖後，請『點選』紅圈內的賠率，我會幫你做成表格。")

uploaded_file = st.file_uploader("📸 上傳運彩截圖", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="請對照此圖點選下方數字", use_container_width=True)
    
    with st.spinner('偵測數字中...'):
        # 抓取所有 1.xx ~ 2.xx 的數字，這會自動排除掉 54.5 或 224.5 這種干擾項
        custom_config = r'--oem 3 --psm 11 -c tessedit_char_whitelist=0123456789.'
        raw_text = pytesseract.image_to_string(img, config=custom_config)
        
        # 尋找所有賠率格式的數字
        all_odds = re.findall(r'[1-2]\.\d{2}', raw_text)
        # 去除重複並排序，確保選單整齊
        unique_odds = sorted(list(set(all_odds)), reverse=True)

    if unique_odds:
        st.info("💡 請點選紅圈內看到的賠率：")
        
        # 讓使用者自己選，絕對不會抓錯行
        selected = st.multiselect("選擇正確賠率：", unique_odds)
        
        if selected:
            # 將選中的數字做成表格
            df = pd.DataFrame({
                "項目": [f"選取項 {i+1}" for i in range(len(selected))],
                "辨識賠率": selected
            })
            
            st.subheader("📊 整理後的賠率表格")
            st.table(df)
            
            # 如果選了兩個，自動顯示試算的結果（選填）
            if len(selected) == 2:
                res = round(float(selected[0]) * float(selected[1]), 2)
                st.write(f"👉 這兩項組合的參考賠率為：**{res}**")
    else:
        st.error("❌ 找不到賠率數字，請確認截圖清晰。")
        with st.expander("手動輸入賠率"):
            manual_input = st.text_input("請手動輸入賠率（用逗號隔開，例如：1.70, 1.68）")
            if manual_input:
                m_list = manual_input.split(',')
                st.table(pd.DataFrame({"項目": [f"手動 {i+1}" for i in range(len(m_list))], "賠率": m_list}))
