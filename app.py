import streamlit as st
from PIL import Image
import easyocr
import numpy as np
import re
import pandas as pd
from datetime import datetime

# 設定網頁
st.set_page_config(page_title="運彩辨識紀錄系統", layout="wide")

# 設定日期與星期
now = datetime.now()
week_list = ["一", "二", "三", "四", "五", "六", "日"]
date_str = now.strftime("%Y-%m-%d")
day_of_week = week_list[now.weekday()]
full_date_display = f"{date_str} (週{day_of_week})"

st.title(f"📊 運彩辨識系統 - {full_date_display}")

# 初始化紀錄儲存器
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
    st.header("📜 歷史紀錄回看")
    if st.session_state.history:
        if st.button("清空所有紀錄"):
            st.session_state.history = []
            st.rerun()
        df_hist = pd.DataFrame(st.session_state.history)
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
    else:
        st.write("目前尚無紀錄")

# 主頁面上傳
uploaded_files = st.file_uploader("📸 上傳運彩截圖 (可多張)", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if uploaded_files and reader:
    st.subheader("📍 本次辨識結果")
    
    table_data = []

    for i, file in enumerate(uploaded_files):
        img = Image.open(file)
        img.thumbnail((1000, 1000))
        img_np = np.array(img)
        
        with st.spinner(f'正在分析圖 {i+1}...'):
            results = reader.readtext(img_np)
            width, height = img.size
            
            # 建立資料存放區
            # 邏輯：利用 x 座標區分左右，y 座標區分上下
            left_nums = []  # 大小分區域 (通常在左)
            right_nums = [] # 讓分區域 (通常在右)
            
            for (bbox, text, prob) in results:
                clean = re.sub(r'[^0-9.+-]', '', text)
                if clean and "." in clean:
                    x_center = (bbox[0][0] + bbox[1][0]) / 2
                    y_center = (bbox[0][1] + bbox[2][1]) / 2
                    
                    # 以圖片中心線區分左右
                    if x_center < width / 2:
                        left_nums.append({'val': clean, 'y': y_center})
                    else:
                        right_nums.append({'val': clean, 'y': y_center})

            # 依垂直位置排序
            left_nums.sort(key=lambda x: x['y'])
            right_nums.sort(key=lambda x: x['y'])

            # 提取數值
            # 大小分：通常第一個是門檻(如 52.5)，第二個是賠率(如 1.75)
            sz_limit = left_nums[0]['val'] if len(left_nums) > 0 else "-"
            sz_odds = left_nums[1]['val'] if len(left_nums) > 1 else "-"
            
            # 讓分：通常第一個是門檻(如 -3.5)，第二個是賠率(如 1.85)
            sp_limit = right_nums[0]['val'] if len(right_nums) > 0 else "-"
            sp_odds = right_nums[1]['val'] if len(right_nums) > 1 else "-"

            # 整理成一列
            row = {
                "日期星期": full_date_display,
                "編號": f"圖{i+1}",
                "大小分-門檻": sz_limit,
                "大小分-賠率": sz_odds,
                "讓分-門檻": sp_limit,
                "讓分-賠率": sp_odds
            }
            table_data.append(row)
            st.session_state.history.append(row)

    # 顯示總表
    if table_data:
        final_df = pd.DataFrame(table_data)
        st.table(final_df) # 使用美觀的表格顯示
        
        # 下方顯示預覽圖對照
        st.divider()
        st.write("🖼️ 圖片對照預覽：")
        cols = st.columns(len(uploaded_files))
        for idx, file in enumerate(uploaded_files):
            cols[idx].image(file, caption=f"圖 {idx+1}", use_container_width=True)

    st.success("✅ 辨識完畢！資料已同步至左側紀錄。")
