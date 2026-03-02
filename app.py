import streamlit as st
from PIL import Image
import easyocr
import numpy as np
import re
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="運彩精準辨識版", layout="wide")

# 日期與星期
now = datetime.now()
week_list = ["一", "二", "三", "四", "五", "六", "日"]
full_date = f"{now.strftime('%Y-%m-%d')} (週{week_list[now.weekday()]})"
st.title(f"📊 運彩精準辨識系統 - {full_date}")

if 'history' not in st.session_state:
    st.session_state.history = []

@st.cache_resource
def load_reader():
    # 這裡必須載入 ch_tra (繁體中文) 來辨識「大、小、讓」
    return easyocr.Reader(['ch_tra', 'en'], gpu=False)

reader = load_reader()

def get_clean_num(text):
    """只提取數字、小數點及正負號"""
    res = re.sub(r'[^0-9.+-]', '', text)
    try:
        return float(res) if res else None
    except:
        return None

# 側邊欄紀錄
with st.sidebar:
    st.header("📜 歷史紀錄")
    if st.session_state.history:
        if st.button("清空紀錄"):
            st.session_state.history = []
            st.rerun()
        st.dataframe(pd.DataFrame(st.session_state.history), hide_index=True)

uploaded_files = st.file_uploader("📸 上傳截圖", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if uploaded_files and reader:
    st.subheader("📍 辨識結果表格")
    current_batch = []

    for i, file in enumerate(uploaded_files):
        img = Image.open(file)
        img_np = np.array(img)
        
        with st.spinner(f'深度掃描圖 {i+1}...'):
            # 取得原始結果 (包含文字與位置)
            results = reader.readtext(img_np)
            
            # 初始化該圖資料
            data = {"大小門檻": "-", "大小賠率": "-", "讓分門檻": "-", "讓分賠率": "-"}
            
            # 第一輪：找出所有帶有數字的區塊及其中心座標
            nums = []
            for (bbox, text, prob) in results:
                val = get_clean_num(text)
                if val is not None:
                    y_mid = (bbox[0][1] + bbox[2][1]) / 2
                    x_mid = (bbox[0][0] + bbox[1][0]) / 2
                    nums.append({"val": val, "x": x_mid, "y": y_mid, "text": text})

            # 第二輪：根據關鍵字定位
            for (bbox, text, prob) in results:
                y_key = (bbox[0][1] + bbox[2][1]) / 2
                x_key = (bbox[0][0] + bbox[1][0]) / 2
                
                # 尋找「大」或「小」附近的數字
                if "大" in text or "小" in text:
                    # 找同一行(y相近)且在右邊最靠近的兩個數字
                    row_nums = [n for n in nums if abs(n['y'] - y_key) < 30 and n['x'] > x_key]
                    row_nums.sort(key=lambda x: x['x'])
                    if len(row_nums) >= 1: data["大小門檻"] = row_nums[0]['val']
                    if len(row_nums) >= 2: data["大小賠率"] = row_nums[1]['val']
                
                # 尋找「讓」附近的數字
                if "讓" in text:
                    row_nums = [n for n in nums if abs(n['y'] - y_key) < 30 and n['x'] > x_key]
                    row_nums.sort(key=lambda x: x['x'])
                    if len(row_nums) >= 1: data["讓分門檻"] = row_nums[0]['val']
                    if len(row_nums) >= 2: data["讓分賠率"] = row_nums[1]['val']

            row = {
                "時間": now.strftime("%H:%M"),
                "週別": f"週{day_of_week}",
                "編號": f"圖{i+1}",
                "大小-盤口": data["大小門檻"],
                "大小-賠率": data["大小賠率"],
                "讓分-盤口": data["讓分門檻"],
                "讓分-賠率": data["讓分賠率"]
            }
            current_batch.append(row)
            st.session_state.history.append(row)

    if current_batch:
        st.table(pd.DataFrame(current_batch))
        st.divider()
        st.write("🖼️ 辨識對照圖：")
        cols = st.columns(len(uploaded_files))
        for idx, file in enumerate(uploaded_files):
            cols[idx].image(file, caption=f"圖 {idx+1}", use_container_width=True)

else:
    st.info("💡 請上傳清晰的截圖，我會自動尋找「大/小」與「讓分」欄位旁的數字。")
