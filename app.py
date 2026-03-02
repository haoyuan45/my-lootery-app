import streamlit as st
from PIL import Image
import easyocr
import numpy as np
import re
import pandas as pd
from datetime import datetime
import gc # 記憶體回收

st.set_page_config(page_title="運彩辨識穩定版", layout="wide")

# 日期與星期
now = datetime.now()
week_list = ["一", "二", "三", "四", "五", "六", "日"]
day_of_week = week_list[now.weekday()]
full_date_display = f"{now.strftime('%Y-%m-%d')} (週{day_of_week})"

st.title(f"🚀 運彩辨識系統 - {full_date_display}")

# 初始化歷史紀錄
if 'history' not in st.session_state:
    st.session_state.history = []

# 讀取器 (加上快取與防錯)
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'], gpu=False)

try:
    reader = load_reader()
except:
    st.error("伺服器壓力過大，請點擊右上角 Reboot 重整。")

# 側邊欄紀錄
with st.sidebar:
    st.header("📜 歷史紀錄")
    if st.session_state.history:
        if st.button("清空紀錄"):
            st.session_state.history = []
            st.rerun()
        st.dataframe(pd.DataFrame(st.session_state.history), hide_index=True)

uploaded_files = st.file_uploader("📸 上傳截圖", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if uploaded_files and 'reader' in locals():
    current_results = []

    for i, file in enumerate(uploaded_files):
        img = Image.open(file).convert('RGB')
        
        # 【重要】壓縮圖片大小，防止記憶體溢出
        img.thumbnail((600, 600)) 
        width, height = img.size
        img_np = np.array(img)
        
        with st.spinner(f'辨識中 {i+1}...'):
            results = reader.readtext(img_np)
            
            nums = []
            for (bbox, text, prob) in results:
                clean = re.sub(r'[^0-9.]', '', text)
                # 過濾掉太短或沒小數點的雜訊
                if clean and "." in clean and len(clean) >= 3:
                    x = (bbox[0][0] + bbox[1][0]) / 2
                    y = (bbox[0][1] + bbox[2][1]) / 2
                    nums.append({'val': clean, 'x': x, 'y': y})

            # 邏輯：左大小、右讓分
            left_p = sorted([n for n in nums if n['x'] < width/2], key=lambda n: n['y'])
            right_p = sorted([n for n in nums if n['x'] >= width/2], key=lambda n: n['y'])

            row = {
                "時間": now.strftime("%H:%M"),
                "編號": f"圖{i+1}",
                "大小-門檻": left_p[0]['val'] if len(left_p) > 0 else "-",
                "大小-賠率": left_p[1]['val'] if len(left_p) > 1 else "-",
                "讓分-門檻": right_p[0]['val'] if len(right_p) > 0 else "-",
                "讓分-賠率": right_p[1]['val'] if len(right_p) > 1 else "-"
            }
            current_results.append(row)
            st.session_state.history.append(row)
            
            # 手動清理記憶體
            del img_np
            gc.collect()

    if current_results:
        st.table(pd.DataFrame(current_results))

else:
    st.info("請上傳圖片。若持續出現 Oh no，請點擊右上角三點選單選擇 Reboot App。")
