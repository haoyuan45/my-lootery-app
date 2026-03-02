import streamlit as st
from PIL import Image, ImageOps
import pytesseract
import pandas as pd
import re
from datetime import datetime

# 頁面設定
st.set_page_config(page_title="運彩專業分析助手", layout="wide")

# 初始化歷史紀錄 (儲存在 Session 中)
if 'history' not in st.session_state:
    st.session_state.history = []

st.title("📋 運彩精準辨識系統")
st.write("自動辨識「大小分」與「讓分」並建立歷史紀錄表格。")

uploaded_file = st.file_uploader("📸 上傳截圖", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    w, h = img.size
    
    # 顯示原始圖
    st.image(img, caption="原始截圖", use_container_width=True)
    
    with st.spinner('進行深度掃描中...'):
        # 1. 預處理圖片以增加辨識率
        gray = ImageOps.grayscale(img)
        
        # 2. 辨識全圖文字
        custom_config = r'--oem 3 --psm 6'
        raw_text = pytesseract.image_to_string(gray, lang='chi_tra+eng', config=custom_config)
        
        # 3. 邏輯提取：尋找大小分(如 54.5)與賠率(如 1.70)
        # 尋找 讓分/大小數字 (通常含一位小數)
        lines = raw_text.split('\n')
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # 簡易邏輯：抓取截圖中符合格式的行
        detected_data = {
            "日期": current_date,
            "項目": "未偵測",
            "讓分/大小值": "N/A",
            "賠率": "N/A"
        }
        
        # 嘗試從文字中過濾出關鍵字
        for line in lines:
            if "大小" in line or "讓分" in line:
                detected_data["項目"] = "大小分" if "大小" in line else "讓分"
            
            # 尋找小數點數字 (如 54.5 或 3.5)
            vals = re.findall(r'\d+\.\d', line)
            if vals:
                detected_data["讓分/大小值"] = vals[0]
            
            # 尋找賠率 (如 1.70, 1.68)
            odds = re.findall(r'[1-2]\.\d{2}', line)
            if odds:
                detected_data["賠率"] = odds[0]

    # 4. 手動確認與修正區 (確保 100% 正確)
    st.subheader("📝 辨識結果確認")
    col1, col2, col3, col4 = st.columns(4)
    
    final_date = col1.text_input("日期", value=current_date)
    final_type = col2.selectbox("類型", ["大小分", "讓分", "獨贏"], index=0)
    final_val = col3.text_input("讓分/大小數字", value=detected_data["讓分/大小值"])
    final_odds = col4.text_input("賠率", value=detected_data["賠率"])
    
    if st.button("➕ 加入歷史紀錄表格"):
        new_entry = {
            "日期": final_date,
            "項目類型": final_type,
            "分盤數字": final_val,
            "賠率": final_odds
        }
        st.session_state.history.append(new_entry)
        st.success("已成功存入歷史紀錄！")

# 5. 顯示歷史紀錄表格
st.divider()
st.subheader("📜 歷史辨識紀錄表格")

if st.session_state.history:
    history_df = pd.DataFrame(st.session_state.history)
    st.table(history_df)
    
    # 下載按鈕
    csv = history_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 下載完整紀錄 (CSV)", csv, "lottery_history.csv", "text/csv")
    
    if st.button("🗑️ 清空所有紀錄"):
        st.session_state.history = []
        st.rerun()
else:
    st.info("目前尚無紀錄，請上傳截圖並點擊「加入歷史紀錄」。")
