import streamlit as st
import json
import folium
from streamlit_folium import st_folium
from openai import OpenAI

# 頁面配置
st.set_page_config(page_title="沖繩 2025 團體旅程", layout="wide", page_icon="🌺")

# 注入更柔和的 CSS 樣式
st.markdown("""
    <style>
    .passenger-card {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 20px;
        border: 1px solid #f0f2f6;
        box-shadow: 0 10px 25px rgba(0,0,0,0.03);
        margin-bottom: 25px;
    }
    .driver-info-box {
        background-color: #f1f3f9;
        padding: 15px;
        border-radius: 12px;
        border-left: 5px solid #1e3c72;
        margin-top: 15px;
    }
    .highlight-badge {
        background-color: #ff4b4b;
        color: white;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 初始化 OpenAI (從 Secrets)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def load_data():
    with open('itinerary.json', 'r', encoding='utf-8') as f:
        return json.load(f)

data = load_data()

# --- 側邊欄：控制台 ---
with st.sidebar:
    st.header("⚙️ 設定")
    # 關鍵功能：切換模式
    is_driver_mode = st.toggle("🚀 開啟駕駛模式", value=False)
    
    st.divider()
    st.markdown("### 👥 全團資訊")
    st.write("成員：8 位 (2部車或大車)")
    st.write("預算建議：每人準備 ¥45,000 現金")
    
    if is_driver_mode:
        st.warning("駕駛模式已開啟：顯示 Mapcode 與導航連結")

# --- 主畫面 ---
st.title("🌺 沖繩 2025 春之假期")
st.write("2025年1月25日 - 1月28日 | 🌸 寒緋櫻賞櫻之旅")

# 使用 Tabs 區分日期
tab_titles = ["🗺️ 路線總覽"] + [f"🗓️ Day {i}" for i in range(1, 4)]
tabs = st.tabs(tab_titles)

# Tab 0: 乘客的地圖導覽
with tabs[0]:
    st.subheader("我們的旅程路線")
    m = folium.Map(location=[26.4, 127.8], zoom_start=10, tiles="CartoDB positron")
    coords = [[loc["lat"], loc["lng"]] for loc in data]
    folium.PolyLine(coords, color="#ff4b4b", weight=3, opacity=0.6).add_to(m)
    for loc in data:
        folium.Marker([loc["lat"], loc["lng"]], popup=loc["name"]).add_to(m)
    st_folium(m, width="100%", height=450)

# Tab 1-3: 每日行程卡片
for i in range(1, 4):
    with tabs[i]:
        day_locs = [l for l in data if l["day"] == i]
        
        for loc in day_locs:
            with st.container():
                # 使用乘客視角顯示卡片
                st.markdown(f"""
                <div class="passenger-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h2 style="margin:0;">📍 {loc['name']}</h2>
                        <span class="highlight-badge">{loc['type']}</span>
                    </div>
                    <p style="color: #666; margin-top: 5px;">預計花費：{loc['budget']} | 🌡️ 預報：18°C 🌤️</p>
                </div>
                """, unsafe_allow_html=True)

                # AI 攻略按鈕 (全團都會感興趣)
                if st.button(f"✨ 查看 {loc['name']} AI 必玩攻略", key=f"tourist_{loc['name']}"):
                    with st.spinner("正在呼叫導遊小助手..."):
                        prompt = f"請針對沖繩景點『{loc['name']}』，以活潑的語氣列出：必做、必吃名物、必睇景點、必打卡位。繁體中文。"
                        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
                        st.info(res.choices[0].message.content)

                # --- 駕駛模式隱藏內容 ---
                if is_driver_mode:
                    with st.container():
                        st.markdown(f"""
                        <div class="driver-info-box">
                            <strong>🛠️ 司機專用資訊</strong><br/>
                            📍 日本導航 Mapcode: <code>{loc['mapcode']}</code><br/>
                            🛣️ 建議：檢查目的地是否有專屬停車場
                        </div>
                        """, unsafe_allow_html=True)
                        st.link_button(f"🗺️ 開啟 Google Maps 導航至 {loc['name']}", 
                                      f"https://www.google.com/maps/search/?api=1&query={loc['lat']},{loc['lng']}",
                                      use_container_width=True)
                
                st.write("") # 增加間隔
