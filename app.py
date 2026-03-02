import streamlit as st
from PIL import Image
import pytesseract
import re
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="運彩辨識優化版", layout="wide")

now = datetime.now()
week_list = ["一", "二", "三", "四", "五", "六", "日"]
day_of_week = week_list[now.weekday()]
full_date_display = f"{now.strftime('%Y-%m-%d')} (週{day_of_week})"

st.title(f"⚡ 運彩辨識系統 - {full_date_display}")

if 'history' not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.header("📜 歷史紀錄")
    if st.session_state.history:
        if st.button("清空紀錄"):
            st.session_state.history = []
            st.rerun()
        st.dataframe(pd.DataFrame(st.session_state.history), hide_index=True)

uploaded_files = st.file_uploader("📸 請上傳截圖", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    current_results = []

    for i, file in enumerate(uploaded_files):
        img = Image.open(file).convert('L') 
        width, height = img.size
        
        with st.spinner(f'分析圖 {i+1} 中...'):
            # 增加辨識參數，嘗試抓取更細微的文字
            custom_config = r'--oem 3 --psm 6' 
            raw_data = pytesseract.image_to_data(img, config=custom_config, output_type=pytesseract.Output.DICT)
            
            nums = []
            for j in range(len(raw_data['text'])):
                text = raw_data['text'][j].strip()
                # 只抓含有數字且有小數點的內容
                clean_text = re.sub(r'[^0-9.]', '', text)
                if clean_text and "." in clean_text:
                    try:
                        val = float(clean_text)
                        # 排除不合理的超大數字 (例如日期或賠率不會是 100 以上)
                        if 1.0 < val < 100.0:
                            x = raw_data['left'][j] + raw_data['width'][j]/2
                            y = raw_data['top'][j] + raw_data['height'][j]/2
                            nums.append({'val': clean_text, 'x': x, 'y': y})
                    except: continue

            # --- 核心邏輯修正 ---
            # 1. 先把數字分成左右兩群
            left_group = [n for n in nums if n['x'] < width * 0.5]
            right_group = [n for n in nums if n['x'] >= width * 0.5]
            
            # 2. 排序 (從上到下)
            left_group.sort(key=lambda n: n['y'])
            right_group.sort(key=lambda n: n['y'])

            # 3. 過濾掉重複或太接近的座標 (防止同一個數字被抓兩次)
            def filter_close_nums(sorted_list):
                unique = []
                for n in sorted_list:
                    if not unique or abs(n['y'] - unique[-1]['y']) > 20:
                        unique.append(n)
                return unique

            left_final = filter_close_nums(left_group)
            right_final = filter_close_nums(right_group)

            row = {
                "時間": now.strftime("%H:%M"),
                "編號": f"圖{i+1}",
                "大小-門檻": left_final[0]['val'] if len(left_final) > 0 else "-",
                "大小-賠率": left_final[1]['val'] if len(left_final) > 1 else "-",
                "讓分-門檻": right_final[0]['val'] if len(right_final) > 0 else "-",
                "讓分-賠率": right_final[1]['val'] if len(right_final) > 1 else "-"
            }
            current_results.append(row)
            st.session_state.history.append(row)

    if current_results:
        st.table(pd.DataFrame(current_results))
