import streamlit as st
from PIL import Image
import pytesseract
import re

st.set_page_config(page_title="運彩賠率計算器", layout="centered")

st.title("🏀 運彩賠率自動抓取")
st.write("上傳截圖後，請從清單中選出紅圈內的賠率。")

uploaded_file = st.file_uploader("📸 選擇截圖", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="原始截圖", use_container_width=True)
    
    with st.spinner('搜尋圖片中的數字...'):
        # 1. 抓取所有數字
        custom_config = r'--oem 3 --psm 11 -c tessedit_char_whitelist=0123456789.'
        raw_text = pytesseract.image_to_string(img, config=custom_config)
        
        # 2. 過濾出符合 1.XX 格式的數字 (例如 1.50 到 2.50)
        potential_odds = re.findall(r'[1-2]\.\d{2}', raw_text)
        # 去除重複
        potential_odds = sorted(list(set(potential_odds)))

    if potential_odds:
        st.info(f"🔍 偵測到以下可能賠率，請選出你要的那兩個：")
        
        # 3. 讓使用者自己點選（這最準！）
        selected = st.multiselect("點選紅圈內的賠率：", potential_odds)
        
        if len(selected) == 2:
            o1, o2 = float(selected[0]), float(selected[1])
            total = round(o1 * o2, 2)
            st.success(f"🔥 二串一計算結果：{o1} x {o2} = {total}")
            st.balloons()
        elif len(selected) > 2:
            st.warning("請只選擇兩個數字。")
        else:
            st.write("請選擇兩個賠率來計算總賠率。")
    else:
        st.error("❌ 找不到任何賠率數字。")

    # 4. 萬一辨識不到，保留手動輸入區
    with st.expander("手動輸入 (辨識失敗時用)"):
        col1, col2 = st.columns(2)
        m1 = col1.number_input("賠率 1", value=1.75, step=0.01)
        m2 = col2.number_input("賠率 2", value=1.70, step=0.01)
        st.write(f"手動總賠率：{round(m1 * m2, 2)}")
