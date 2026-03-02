import streamlit as st
from PIL import Image
import easyocr
import numpy as np
import re
import pandas as pd
from datetime import datetime

# 設定網頁標題與寬度
st.set_page_config(page_title="運彩辨識進階版", layout="wide")

# 顯示今天的日期
today_str = datetime.now().strftime("%Y-%m-%d")
st.title(f"🏀 運彩自動辨識系統 ({today_str})")

# 初始化紀錄儲存器
if 'history' not in st.session_state:
    st.session_state.history = []

@st.cache_resource
def load_reader():
    try:
        # 繁體中文與英文辨識
        return easyocr.Reader(['ch_tra', 'en'], gpu=False)
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
        df_history = pd.DataFrame(st.session_state.history)
        st.dataframe(df_history, use_container_width=True)
    else:
        st.write("尚無紀錄")

# 主界面
uploaded_files = st.file_uploader("📸 上傳運彩截圖", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if uploaded_files and reader:
    st.subheader("🔍 本次辨識明細")
    
    for i, file in enumerate(uploaded_files):
        img = Image.open(file)
        img.thumbnail((1000, 1000))
        
        # 建立左右佈局：左邊放圖，右邊放辨識結果
        col_img, col_info = st.columns([1, 1])
        
        with col_img:
            st.image(img, caption=f"原始圖 {i+1}", use_container_width=True)
            
        with col_info:
            with st.spinner(f'正在深度辨識圖 {i+1}...'):
                img_np = np.array(img)
                # 取得包含位置資訊的原始辨識結果
                raw_results = reader.readtext(img_np)
                
                # 儲存所有找到的數字與其垂直位置(y軸)
                all_numbers = []
                for (bbox, text, prob) in raw_results:
                    # 提取數字、小數點與正負號
                    clean = re.sub(r'[^0-9.+-]', '', text)
                    if clean and len(clean) >= 1:
                        y_center = (bbox[0][1] + bbox[2][1]) / 2
                        try:
                            val = float(clean)
                            all_numbers.append({'val': clean, 'y': y_center, 'text': text})
                        except: continue

                # 排序：依圖片從上到下的位置排序
                all_numbers.sort(key=lambda x: x['y'])

                # 邏輯分配：通常一行會有「門檻值」和「賠率」
                # 門檻值通常帶有 .5 或 +-，賠率通常在 1.5~2.5 之間
                size_line = "未偵測"
                spread_line = "未偵測"
                
                # 簡單分組：前兩個數字歸為第一組（通常是大小），後兩個歸為第二組（讓分）
                if len(all_numbers) >= 2:
                    size_line = f"門檻:{all_numbers[0]['val']} / 賠率:{all_numbers[1]['val']}"
                if len(all_numbers) >= 4:
                    spread_line = f"門檻:{all_numbers[2]['val']} / 賠率:{all_numbers[3]['val']}"
                
                # 顯示當前結果
                st.markdown(f"### 📋 圖 {i+1} 結果")
                st.info(f"📏 **第一節大小分**：{size_line}")
                st.success(f"⚖️ **第一節讓分**：{spread_line}")
                
                # 存入歷史紀錄
                record = {
                    "日期": today_str,
                    "圖片": f"圖 {i+1}",
                    "大小分(門檻/賠率)": size_line,
                    "讓分(門檻/賠率)": spread_line
                }
                st.session_state.history.append(record)

    st.success("✅ 所有圖片辨識完畢，紀錄已存入左側表格。")

else:
    st.info(f"📅 今天是 {today_str}，請上傳截圖開始辨識。")
