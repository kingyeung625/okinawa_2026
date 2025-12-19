import streamlit as st
import json
import folium
from streamlit_folium import st_folium

# 頁面配置
st.set_page_config(page_title="沖繩 2025 團體行程", layout="wide", page_icon="🌺")

# 注入 CSS (優化 UX)
st.markdown("""
    <style>
    .passenger-card { background-color: white; padding: 25px; border-radius: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 25px; border: 1px solid #f0f0f0; }
    .driver-box { background-color: #fffde7; padding: 15px; border-radius: 12px; border: 1px dashed #fbc02d; margin-top: 15px; font-family: monospace; }
    .highlight-label { font-weight: bold; color: #ff4b4b; margin-right: 8px; }
    .budget-tag { background-color: #e8f5e9; color: #2e7d32; padding: 2px 8px; border-radius: 5px; font-size: 0.85em; }
    </style>
    """, unsafe_allow_html=True)

def load_data():
    with open('itinerary.json', 'r', encoding='utf-8') as f:
        return json.load(f)

itinerary = load_data()

# --- 側邊欄 ---
with st.sidebar:
    st.title("🌺 沖繩導覽助手")
    is_driver = st.toggle("🚀 駕駛模式 (顯示 Mapcode)", value=False)
    st.divider()
    st.markdown("### 團體資訊\n- 人數：8 位\n- 日期：1/25 - 1/28")

# --- 主畫面 ---
st.title("2025 沖繩春之行程 🌸")

tabs = st.tabs(["🗺️ 路線圖", "🗓️ Day 1", "🗓️ Day 2", "🗓️ Day 3"])

# Tab 0: 地圖
with tabs[0]:
    st.subheader("旅程全景")
    m = folium.Map(location=[26.4, 127.8], zoom_start=10, tiles="CartoDB positron")
    coords = [[l["lat"], l["lng"]] for l in itinerary]
    folium.PolyLine(coords, color="#318ce7", weight=3).add_to(m)
    for l in itinerary:
        folium.Marker([l["lat"], l["lng"]], popup=l["name"]).add_to(m)
    st_folium(m, width="100%", height=450)

# Day Tabs
for i in range(1, 4):
    with tabs[i]:
        day_items = [l for l in itinerary if l["day"] == i]
        for spot in day_items:
            # 乘客模式卡片
            st.markdown(f"""
            <div class="passenger-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h2 style="margin:0;">📍 {spot['name']}</h2>
                    <span class="budget-tag">預算: {spot['budget']}</span>
                </div>
                <p style="color:#666; font-style:italic; margin-top:8px;">"{spot['tips']['intro']}"</p>
                <hr style="margin: 15px 0; border:0; border-top:1px solid #eee;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div><span class="highlight-label">✅ 必做:</span>{spot['tips']['do']}</div>
                    <div><span class="highlight-label">😋 必食:</span>{spot['tips']['eat']}</div>
                    <div><span class="highlight-label">👀 必睇:</span>{spot['tips']['see']}</div>
                    <div><span class="highlight-label">📸 打卡:</span>{spot['tips']['photo']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 駕駛模式內容
            if is_driver:
                st.markdown(f"""
                <div class="driver-box">
                    <strong>🛠️ 司機資訊</strong><br/>
                    Mapcode: <code>{spot['mapcode']}</code>
                </div>
                """, unsafe_allow_html=True)
                st.link_button(f"🗺️ 導航至 {spot['name']}", 
                              f"https://www.google.com/maps/dir/?api=1&destination={spot['lat']},{spot['lng']}")

st.caption("本程式內容已預先生成，離線亦可輕鬆查閱行程建議。")
