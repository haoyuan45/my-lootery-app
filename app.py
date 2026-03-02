import streamlit as st
from PIL import Image
import pytesseract
import pandas as pd
import re

# 網頁標題設定
st.set_page_config(page_title="運彩賠率自動轉表格", layout="centered")

st.title("📋 運彩截圖 -> 自動轉表格")
st.write("上傳截圖後，我會自動提取所有賠率數字並整理。")

# 檔案上傳器
uploaded_file = st.file_uploader("📸 請選擇你的運彩截圖", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # 顯示上傳的原始圖片
    img = Image.open(uploaded_file)
    st.image(img, caption="已上傳的截圖", use_container_width=True)
    
    with st.spinner('正在掃描圖片中的賠率...'):
        # 1. 使用 OCR 辨識圖片中的文字
        # config 設定為只辨識數字和小數點，增加準確率
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789.'
        raw_text = pytesseract.image_to_string(img, config=custom_config)
        
        # 2. 用正規表達式抓取 1.xx 或 2.xx 格式的賠率
        odds_found = re.findall(r'[1-2]\.\d{2}', raw_text)
        
        # 3. 去除重複數字並保持順序
        odds_unique = []
        for o in odds_found:
            if o not in odds_unique:
                odds_unique.append(o)

    # 4. 建立表格
    if odds_unique:
        st.success(f"✅ 成功辨識出 {len(odds_unique)} 個賠率！")
        
        # 建立資料清單
        data = []
        for i, val in enumerate(odds_unique):
            data.append({"序號": i + 1, "辨識到的賠率": val})
        
        # 轉成 DataFrame 並顯示表格
        df = pd.DataFrame(data)
        st.subheader("📊 自動整理結果")
        st.table(df) # 使用 st.table 顯示靜態表格，手機看很清楚
        
        # 下載按鈕 (選配)
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 下載此表格 (CSV)", csv, "my_odds.csv", "text/csv")
        
    else:
        st.error("❌ 找不到賠率數字。請確認截圖是否清晰，或賠率是否在 1.00 ~ 2.99 之間。")

st.divider()
st.caption("提示：如果表格抓到無關數字（如讓分數 3.50），請自行對照原圖。")
