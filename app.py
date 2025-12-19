import streamlit as st
import json
import folium
from streamlit_folium import st_folium

# 頁面配置
st.set_page_config(page_title="沖繩 2025 團體手冊", layout="wide", page_icon="🌸")

# CSS 強化：圖片圓角與車程顯示
st.markdown("""
    <style>
    .spot-image { width: 100%; border-radius: 15px; margin-bottom: 15px; object-fit: cover; height: 200px; }
    .drive-time-tag { background-color: #f1f3f9; color: #1e3c72; padding: 5px 12px; border-radius: 20px; font-size: 0.85em; font-weight: bold; margin-bottom: 10px; display: inline-block; }
    .passenger-card { background-color: white; padding: 20px; border-radius: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

def load_data():
    with open('itinerary.json', 'r', encoding='utf-8') as f:
        return json.load(f)

itinerary = load_data()

# --- 側邊欄 ---
with st.sidebar:
    st.title("🍹 旅程控制台")
    is_driver = st.toggle("🚀 司機導航模式", value=False)
    st.divider()
    st.markdown("### 🚌 8人交通建議\n建議租用 Toyota Alphard 或兩部小型車，沖繩停車場通常很寬敞。")

# --- 主畫面 ---
st.title("2025 沖繩悠閒賞櫻團 🌸")

tabs = st.tabs(["🗺️ 全島地圖預覽", "🗓️ 行程詳情"])

# Tab 0: 地圖預覽 (讓大家知道大約位置)
with tabs[0]:
    st.subheader("地理位置分佈")
    # 地圖中心設在沖繩中部
    m = folium.Map(location=[26.48, 127.8], zoom_start=10, tiles="CartoDB positron")
    
    # 在地圖上畫出帶有編號的點
    for i, loc in enumerate(itinerary):
        folium.Marker(
            [loc["lat"], loc["lng"]], 
            popup=f"Day {loc['day']}: {loc['name']}",
            tooltip=loc["name"],
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)
    
    # 畫出建議行車路徑 (示意連線)
    coords = [[l["lat"], l["lng"]] for l in itinerary]
    folium.PolyLine(coords, color="#318ce7", weight=2, opacity=0.8).add_to(m)
    
    st_folium(m, width="100%", height=500)



# Tab 1: 行程詳情 (圖文並茂)
with tabs[1]:
    for i in range(1, 5): # 假設 4 天
        day_items = [l for l in itinerary if l["day"] == i]
        if day_items:
            st.markdown(f"## 🗓️ Day {i}")
            for spot in day_items:
                with st.container():
                    st.markdown('<div class="passenger-card">', unsafe_allow_html=True)
                    
                    col_img, col_txt = st.columns([1, 1.2])
                    
                    with col_img:
                        # 圖片預覽
                        st.markdown(f'<img src="{spot["image_url"]}" class="spot-image">', unsafe_allow_html=True)
                        st.markdown(f'<div class="drive-time-tag">{spot["drive_time"]}</div>', unsafe_allow_html=True)
                    
                    with col_txt:
                        st.markdown(f"### 📍 {spot['name']}")
                        st.write(f"*{spot['tips']['intro']}*")
                        st.markdown(f"✅ **必做:** {spot['tips']['do']}")
                        st.markdown(f"😋 **必食:** {spot['tips']['eat']}")
                        st.markdown(f"📸 **打卡:** {spot['tips']['photo']}")
                        st.write(f"💰 **人均預算:** {spot['budget']}")
                    
                    # 司機專屬資訊
                    if is_driver:
                        st.divider()
                        c1, c2 = st.columns([1, 1])
                        c1.info(f"📍 Mapcode: {spot['mapcode']}")
                        c2.link_button(f"🌐 導覽至 {spot['name']}", f"https://www.google.com/maps/search/?api=1&query={spot['lat']},{spot['lng']}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
