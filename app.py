import streamlit as st
from PIL import Image
import easyocr
import numpy as np
import re
import pandas as pd
from datetime import datetime

# 基礎設定
st.set_page_config(page_title="運彩辨識穩定版", layout="wide")

# 日期與星期
now = datetime.now()
week_list = ["一", "二", "三", "四", "五", "六", "日"]
day_of_week = week_list[now.weekday()]
full_date_display = f"{now.strftime('%Y-%m-%d')} (週{day_of_week})"

st.title(f"🚀 運彩辨識系統 - {full_date_display}")

if 'history' not in st.session_state:
    st.session_state.history = []

@st.cache_resource
def load_reader():
    # 只載入英文辨識數字，最節省記憶體，不會掛掉
    return easyocr.Reader(['en'], gpu=False)

reader = load_reader()

# 側邊欄
with st.sidebar:
    st.header("📜 歷史紀錄")
    if st.session_state.history:
        if st.button("清空紀錄"):
            st.session_state.history = []
            st.rerun()
        st.dataframe(pd.DataFrame(st.session_state.history), hide_index=True)

uploaded_files = st.file_uploader("📸 上傳截圖", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if uploaded_files and reader:
    st.subheader("📍 辨識結果")
    current_results = []

    for i, file in enumerate(uploaded_files):
        img = Image.open(file)
        width, height = img.size
        img_np = np.array(img)
        
        with st.spinner(f'正在分析圖 {i+1}...'):
            results = reader.readtext(img_np)
            
            # 存儲所有數字及其座標
            all_nums = []
            for (bbox, text, prob) in results:
                clean = re.sub(r'[^0-9.]', '', text)
                if clean and "." in clean:
                    x = (bbox[0][0] + bbox[1][0]) / 2
                    y = (bbox[0][1] + bbox[2][1]) / 2
                    all_nums.append({'val': clean, 'x': x, 'y': y})

            # 排序邏輯：將數字分成「左半部」與「右半部」
            # 左半部通常是大小分，右半部是讓分
            left_part = sorted([n for n in all_nums if n['x'] < width * 0.5], key=lambda n: n['y'])
            right_part = sorted([n for n in all_nums if n['x'] >= width * 0.5], key=lambda n: n['y'])

            # 抓取數值 (取每區垂直位置最中間的兩個)
            sz_l, sz_o, sp_l, sp_o = "-", "-", "-", "-"
            
            if len(left_part) >= 2:
                sz_l, sz_o = left_part[0]['val'], left_part[1]['val']
            elif len(left_part) == 1:
                sz_o = left_part[0]['val']

            if len(right_part) >= 2:
                sp_l, sp_o = right_part[0]['val'], right_part[1]['val']
            elif len(right_part) == 1:
                sp_o = right_part[0]['val']

            row = {
                "日期星期": full_date_display,
                "編號": f"圖{i+1}",
                "大小-盤口": sz_l,
                "大小-賠率": sz_o,
                "讓分-盤口": sp_l,
                "讓分-賠率": sp_o
            }
            current_results.append(row)
            st.session_state.history.append(row)

    if current_results:
        st.table(pd.DataFrame(current_results))
        st.divider()
        st.write("🖼️ 對照預覽：")
        cols = st.columns(len(uploaded_files))
        for idx, file in enumerate(uploaded_files):
            cols[idx].image(file, caption=f"圖 {idx+1}", use_container_width=True)
else:
    st.info("💡 提示：請確保圖片清晰。若數字不對，請嘗試將截圖裁切成只剩賠率表格。")
