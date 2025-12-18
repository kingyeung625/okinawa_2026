import streamlit as st
import json
import folium
from streamlit_folium import st_folium
import google.generativeai as genai

# 1. 頁面基礎配置
st.set_page_config(page_title="沖繩 2025 團體導遊", layout="wide", page_icon="🌺")

# 2. 初始化 Gemini API (從 Secrets 讀取，安全第一)
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("❌ 未在 Secrets 中找到 GEMINI_API_KEY")
    model = None

# 3. 注入 CSS 提升視覺效果
st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; }
    .spot-card {
        background-color: white;
        padding: 25px;
        border-radius: 20px;
        border: 1px solid #f0f0f0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .driver-mode-box {
        background-color: #fffde7;
        padding: 15px;
        border-radius: 12px;
        border: 1px dashed #fbc02d;
        margin-top: 15px;
    }
    .mapcode-text {
        font-family: monospace;
        font-weight: bold;
        color: #d32f2f;
        background: #ffebee;
        padding: 2px 6px;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. 資料加載
def load_data():
    with open('itinerary.json', 'r', encoding='utf-8') as f:
        return json.load(f)

itinerary = load_data()

# --- 側邊欄 ---
with st.sidebar:
    st.title("🌺 旅程助手")
    st.write("成員：8位 | 2025/1/25 - 1/28")
    st.divider()
    # 駕駛模式切換
    is_driver = st.toggle("🚀 切換至駕駛模式", help="開啟後顯示 Mapcode 與導航連結")
    st.divider()
    st.success("🤖 Gemini AI 引擎已就緒")

# --- 主畫面 ---
st.title("沖繩春之賞櫻團 🌸")

# 使用分頁
tab_titles = ["🗺️ 路線總覽"] + [f"🗓️ Day {i}" for i in range(1, 4)]
tabs = st.tabs(tab_titles)

with tabs[0]:
    st.subheader("旅程地理分佈")
    m = folium.Map(location=[26.4, 127.8], zoom_start=10, tiles="CartoDB positron")
    coords = [[l["lat"], l["lng"]] for l in itinerary]
    folium.PolyLine(coords, color="#ff4b4b", weight=3).add_to(m)
    for l in itinerary:
        folium.Marker([l["lat"], l["lng"]], popup=l["name"]).add_to(m)
    st_folium(m, width="100%", height=500)

for i in range(1, 4):
    with tabs[i]:
        day_items = [l for l in itinerary if l["day"] == i]
        if not day_items:
            st.info("今天暫無行程安排")
        for spot in day_items:
            # 乘客優先視角卡片
            st.markdown(f"""
            <div class="spot-card">
                <div style="display: flex; justify-content: space-between;">
                    <h2 style="margin:0;">📍 {spot['name']}</h2>
                    <span style="color: #999;">{spot['type']}</span>
                </div>
                <p style="margin-top:10px; color:#555;">預計花費：{spot['budget']} | 🌡️ 天氣預報：18°C 🌤️</p>
            </div>
            """, unsafe_allow_html=True)
            
            # AI 攻略按鈕 (全團可用)
            if st.button(f"✨ 查看 {spot['name']} 的 8 人團攻略", key=f"ai_{spot['name']}"):
                if model:
                    with st.spinner("AI 導遊正在整理重點..."):
                        prompt = f"以香港專業導遊口吻，針對 8 人團體介紹沖繩景點『{spot['name']}』。請點列式提供：必做、必吃、必睇、必打卡位。使用繁體中文。"
                        response = model.generate_content(prompt)
                        st.markdown(f"**【AI 建議】**\n{response.text}")

            # 駕駛模式隱藏區塊
            if is_driver:
                st.markdown(f"""
                <div class="driver-mode-box">
                    <strong>🛠️ 駕駛模式資訊</strong><br/>
                    本站 Mapcode：<span class="mapcode-text">{spot['mapcode']}</span>
                </div>
                """, unsafe_allow_html=True)
                st.link_button(f"🗺️ 導航至 {spot['name']}", 
                              f"https://www.google.com/maps/search/?api=1&query={spot['lat']},{loc['lng']}", 
                              use_container_width=True)

st.divider()
st.caption("2025 Okinawa Travel App | Powered by Streamlit & Gemini")
