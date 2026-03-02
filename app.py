import streamlit as st
from PIL import Image
import easyocr
import numpy as np
import re
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="運彩辨識紀錄版", layout="wide")
st.title("🏀 運彩第一節賠率自動列表")

# 初始化紀錄儲存器 (Session State)
if 'history' not in st.session_state:
    st.session_state.history = []

@st.cache_resource
def load_reader():
    try:
        return easyocr.Reader(['en'], gpu=False)
    except Exception as e:
        st.error(f"AI 引擎啟動失敗: {e}")
        return None

reader = load_reader()

# 側邊欄：歷史紀錄
with st.sidebar:
    st.header("📜 歷史辨識紀錄")
    if st.session_state.history:
        if st.button("清除所有紀錄"):
            st.session_state.history = []
            st.rerun()
        
        # 顯示歷史表格
        df_history = pd.DataFrame(st.session_state.history)
        st.dataframe(df_history, use_container_width=True)
    else:
        st.write("尚無紀錄")

# 主界面：上傳區
uploaded_files = st.file_uploader("📸 上傳運彩截圖", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if uploaded_files and reader:
    st.subheader("🔍 本次辨識結果")
    
    current_results = []
    
    for i, file in enumerate(uploaded_files):
        img = Image.open(file)
        img.thumbnail((800, 800))
        
        with st.spinner(f'辨識圖片 {i+1}...'):
            img_np = np.array(img)
            results = reader.readtext(img_np)
            
            detected = []
            for (_, text, _) in results:
                clean = re.sub(r'[^0-9.]', '', text)
                try:
                    val = float(clean)
                    # 篩選賠率範圍
                    if 1.1 <= val <= 5.0 and "." in clean:
                        if val not in detected:
                            detected.append(val)
                except: continue
            
            # 分配賠率：假設第一個是大小，第二個是讓分 (依辨識順序)
            odds_size = detected[0] if len(detected) > 0 else "未偵測"
            odds_spread = detected[1] if len(detected) > 1 else "未偵測"
            
            # 建立單筆紀錄
            record = {
                "時間": datetime.now().strftime("%H:%M:%S"),
                "圖片": f"圖 {i+1}",
                "第一節大小": odds_size,
                "第一節讓分": odds_spread
            }
            current_results.append(record)
            st.session_state.history.append(record)

    # 顯示本次表格
    if current_results:
        df_now = pd.DataFrame(current_results)
        st.table(df_now) # 使用 table 顯示美觀的靜態表格
        
        # 顯示圖片預覽
        cols = st.columns(len(uploaded_files))
        for idx, file in enumerate(uploaded_files):
            cols[idx].image(file, caption=f"圖 {idx+1}", use_container_width=True)
            
    st.success("✅ 辨識完成！紀錄已同步至左側清單。")

else:
    st.info("💡 請上傳截圖，我會自動幫你區分「大小」與「讓分」賠率並列表。")
