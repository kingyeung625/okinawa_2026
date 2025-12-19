import streamlit as st
import json
import folium
from streamlit_folium import st_folium

# 1. 頁面配置
st.set_page_config(page_title="沖繩 2025 旅程誌", layout="wide")

# 2. CSS：實現線性時間軸、卡片設計與自動輪播
st.markdown("""
    <style>
    /* 容器與背景 */
    .main { background-color: #f4f7f9; }
    
    /* 線性時間軸效果 */
    .timeline-line {
        border-left: 3px dashed #1e3c72;
        margin-left: 20px;
        padding-left: 30px;
        position: relative;
    }
    
    /* 景點卡片 */
    .info-card {
        background: white;
        border-radius: 20px;
        padding: 0;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        overflow: hidden;
        border: 1px solid #eee;
    }
    
    /* 車程資訊格樣式 */
    .drive-info {
        background: #e3f2fd;
        color: #1565c0;
        padding: 8px 20px;
        border-radius: 50px;
        font-weight: bold;
        display: inline-block;
        margin: 10px 0 30px 20px;
        font-size: 0.9em;
    }

    /* 自動播放輪播圖 CSS */
    .slideshow-container { position: relative; width: 100%; height: 250px; overflow: hidden; }
    .slide {
        position: absolute; width: 100%; height: 100%;
        opacity: 0; animation: fadeEffect 15s infinite;
        object-fit: cover;
    }
    .slide:nth-child(1) { animation-delay: 0s; }
    .slide:nth-child(2) { animation-delay: 5s; }
    .slide:nth-child(3) { animation-delay: 10s; }
    @keyframes fadeEffect {
        0% { opacity: 0; }
        10% { opacity: 1; }
        33% { opacity: 1; }
        43% { opacity: 0; }
        100% { opacity: 0; }
    }
    
    .card-content { padding: 20px; }
    </style>
    """, unsafe_allow_html=True)

def load_data():
    with open('itinerary.json', 'r', encoding='utf-8') as f:
        return json.load(f)

data = load_data()

# --- 主視覺介面 ---
st.title("🌺 沖繩 2025 悠閒之旅")
st.write("8人團體 | UO820 → UO827")

is_driver = st.sidebar.toggle("🚀 開啟駕駛模式", value=False)

# 分日期 Tabs
tabs = st.tabs(["🗺️ 全圖", "🗓️ Day 1", "🗓️ Day 2", "🗓️ Day 3", "🗓️ Day 4"])

# Tab 0: 視覺化地理位置
with tabs[0]:
    m = folium.Map(location=[26.4, 127.8], zoom_start=10, tiles="CartoDB positron")
    for loc in data:
        folium.Marker([loc["lat"], loc["lng"]], popup=loc["name"]).add_to(m)
    st_folium(m, width="100%", height=400)

# Day Tabs (1-4)
for i in range(1, 5):
    with tabs[i]:
        day_items = [l for l in data if l["day"] == i]
        
        # 開啟線性時間軸容器
        st.markdown('<div class="timeline-line">', unsafe_allow_html=True)
        
        for idx, spot in enumerate(day_items):
            # 輪播圖 HTML 生成
            img_html = "".join([f'<img src="{url}" class="slide">' for url in spot['images']])
            
            # 景點 Info Card
            st.markdown(f"""
            <div class="info-card">
                <div class="slideshow-container">
                    {img_html}
                </div>
                <div class="card-content">
                    <h3 style="margin-top:0;">📍 {spot['name']}</h3>
                    <p style="color:#666;">{spot['tips']['intro']}</p>
                    <div style="display:grid; grid-template-columns:1fr 1fr; font-size:0.85em; gap:10px;">
                        <div><b>✅ 必做:</b> {spot['tips']['do']}</div>
                        <div><b>😋 必食:</b> {spot['tips']['eat']}</div>
                        <div><b>👀 必睇:</b> {spot['tips']['see']}</div>
                        <div><b>📸 打卡:</b> {spot['tips']['photo']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 顯示車程資料 (除了最後一站)
            if spot.get('next_drive'):
                st.markdown(f'<div class="drive-info">{spot["next_drive"]}</div>', unsafe_allow_html=True)

            if is_driver:
                st.info(f"駕駛專用 Mapcode: {spot['mapcode']}")
                st.link_button(f"導航至 {spot['name']}", f"google.navigation:q={spot['lat']},{spot['lng']}")

        st.markdown('</div>', unsafe_allow_html=True) # 結束線性容器
