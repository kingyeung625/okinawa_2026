import streamlit as st
import json
import folium
from streamlit_folium import st_folium
from openai import OpenAI

# 頁面基本配置
st.set_page_config(page_title="日本自駕 AI 助手", layout="wide", page_icon="🚗")

# --- 1. 初始化 OpenAI (從 Secrets 讀取) ---
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.warning("⚠️ 未檢測到 API Key。請在 Secrets 中設定 OPENAI_API_KEY 以啟用 AI 功能。")
    client = None

# --- 2. 資料讀取函式 ---
def load_itinerary():
    try:
        with open('itinerary.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("❌ 找不到 itinerary.json 檔案！")
        return []

# --- 3. AI 生成亮點函式 ---
def get_ai_tips(location):
    if not client:
        return "請先設定 OpenAI API Key。"
    
    prompt = f"""
    你是一位日本旅遊專家。請針對『{location}』提供：
    1. 簡短景點介紹 (50字內)。
    2. 點列式：必做、必吃、必睇、必打卡。
    使用繁體中文，口吻要專業且具吸引力。
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI 請求失敗: {str(e)}"

# --- 4. UI 介面設計 ---
st.title("🏝️ 沖繩自駕 AI 行程助手")
st.markdown("📅 **2025年1月25日 - 1月28日** | 🚗 日本自駕專用版")

data = load_itinerary()

# 佈局：左側地圖，右側行程卡片
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("🗺️ 路線預覽")
    if data:
        # 初始化地圖中心點
        m = folium.Map(location=[26.4, 127.8], zoom_start=10, tiles="CartoDB positron")
        
        # 繪製景點標記與連線
        coords = [[loc["lat"], loc["lng"]] for loc in data]
        folium.PolyLine(coords, color="#318ce7", weight=4, opacity=0.7).add_to(m)
        
        for i, loc in enumerate(data):
            folium.Marker(
                [loc["lat"], loc["lng"]],
                popup=f"Day {loc['day']}: {loc['name']}",
                icon=folium.DivIcon(html=f"""<div style="font-family: sans-serif; color: white; background-color: #318ce7; border-radius: 50%; width: 25px; height: 25px; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 2px solid white;">{i+1}</div>""")
            ).add_to(m)
        
        st_folium(m, width="100%", height=600)

with col2:
    st.subheader("📅 詳細行程")
    
    for loc in data:
        with st.expander(f"📍 Day {loc['day']}: {loc['name']}", expanded=True):
            c1, c2 = st.columns([2, 1])
            with c1:
                st.write(f"💰 預估花費: **{loc['budget']}**")
                # 模擬天氣
                st.write("🌡️ 預報: 18°C ☀️ (適合自駕)")
            with c2:
                st.code(f"{loc['mapcode']}", language="markdown")
                st.caption("點擊上方複製 Mapcode")

            # AI 攻略按鈕
            if st.button(f"✨ AI 生成「四必」清單", key=loc['name']):
                with st.spinner("正在諮詢 AI 達人..."):
                    tips = get_ai_tips(loc['name'])
                    st.markdown(tips)
            
            # 導航跳轉
            nav_url = f"https://www.google.com/maps/dir/?api=1&destination={loc['lat']},{loc['lng']}"
            st.link_button("🚀 開啟 Google Maps 導航", nav_url)

st.divider()
st.info("💡 貼士：在日本開車請確保攜帶國際駕駛執照 (IDP) 以及護照正本。")
