# 🔧 Imports
import streamlit as st
import pandas as pd
import matplotlib.font_manager as fm
import plotly.express as px
import matplotlib.pyplot as plt
import utils
import json
import requests
import folium
from streamlit_folium import st_folium
from var import areaCd, unitySignguCd, preferCnttgClscd, spctrCd, spctrSecd as spctrSecd_dict
from pathlib import Path
from math import radians, cos, sin, asin, sqrt

KAKAO_API_KEY = "7758866813611c4b671d0ed485e11ce3"

# 📁 Font Registration
font_path = "./data/MALGUN.TTF"
if Path(font_path).exists():
    fm.fontManager.addfont(font_path)
    plt.rcParams['font.family'] = 'Malgun Gothic'
else:
    st.warning("❗ MALGUN.TTF 폰트 파일을 ./data 폴더에 넣어주세요.")

# 📁 GeoJSON
geo_path = "./data/TL_SCCO_SIG.json"
with open(geo_path, encoding="utf-8") as f:
    geo_data = json.load(f)

@st.cache_data
def load_centers():
    return pd.read_csv("./data/food_centers_with_region_and_coords.csv", encoding="utf-8", dtype=object).dropna(subset=["위도", "경도"])

def geocode_kakao_query(query: str):
    base_url = "https://dapi.kakao.com/v2/local/search"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_API_KEY}"
    }
    addr_res = requests.get(f"{base_url}/address.json", headers=headers, params={"query": query})
    if addr_res.status_code == 200 and addr_res.json()["documents"]:
        doc = addr_res.json()["documents"][0]
        return doc["address"]["address_name"], float(doc["y"]), float(doc["x"])
    key_res = requests.get(f"{base_url}/keyword.json", headers=headers, params={"query": query})
    if key_res.status_code == 200 and key_res.json()["documents"]:
        doc = key_res.json()["documents"][0]
        return doc["place_name"], float(doc["y"]), float(doc["x"])
    return None, None, None

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    return 2 * R * asin(sqrt(a))

# 🧭 Main UI
st.markdown("# 🔗 물품 공급 제안")
centers_df = load_centers()

selected_sido = st.sidebar.selectbox("시도 선택", list(areaCd.values()), key="tab2_sido")
selected_sido_code = [k for k, v in areaCd.items() if v == selected_sido][0]

options = ["🍜 라면류", "🌾 쌀(곡식류)", "🌾 밀가루(류)", "🌶 고추장(류)", 
           "🍲 된장(류)", "🧴 참기름", "🥓 (즉석)가공햄류", "🧴 식용유(류)", 
           "🥫 통조림류", "🍬 설탕(류)", "🧂 간장(류)", "🍜 소면류(국수)", 
           "🍙 김(류)", "🍱 즉석밥류", "🧴 샴푸", "🪥 치약", "🧼 비누"]

try:
    st.markdown("### 🔍 선호 물품 선택")
    prefer_name = st.pills("물품 종류", options, selection_mode="single", label_visibility="collapsed")[2:]
    prefer_name_code = [k for k, v in preferCnttgClscd.items() if v == prefer_name][0]

    if prefer_name_code:
        df_raw = utils.getPreferInfo(area_cd=selected_sido_code, prefer_cnttg_clscd=prefer_name_code)
        df_raw = df_raw[df_raw['holdQy'] > 0]
        df = pd.merge(df_raw, centers_df, how='inner', on=['spctrCd', 'areaCd', 'unitySignguCd'])

        df['시도명'] = df['areaCd'].map(areaCd)
        df['지역구'] = df['unitySignguCd'].map(unitySignguCd)
        df['센터명'] = df['spctrCd'].map(spctrCd)
        df['주소'] = df['spctrAdres'] + df['spctrDetailAdres']
        df['보유수량'] = df['holdQy']
        df = df[['시도명', '지역구', '센터명', 'spctrTelno', '주소', '보유수량', '위도', '경도']]
        df.rename(columns={'spctrTelno': '전화번호'}, inplace=True)
        df = df.astype({'위도': 'float64', '경도': 'float64'})

        col1, col2 = st.columns(2)

        with col2:
            st.markdown("### 가까운 센터 추천")
            user_address = st.text_input("주소 입력창", placeholder="예: 서울특별시 중구 세종대로 110", label_visibility="collapsed")
            if user_address:
                full_addr, lat, lon = geocode_kakao_query(user_address)
                if full_addr:
                    confirm = st.radio(f"📍 유사 주소 확인: **{full_addr}**. 이 위치로 추천할까요?", ("예", "아니오"), horizontal=True)
                    if confirm == "예":
                        df["거리(km)"] = df.apply(lambda row: haversine(lat, lon, row["위도"], row["경도"]), axis=1)
                        df = df[df["보유수량"] > 0].sort_values("거리(km)").reset_index(drop=True)
                        df["거리(km)"] = df["거리(km)"].round(2)

                        st.success(f"기준 위치: {full_addr} (위도: {lat:.5f}, 경도: {lon:.5f})")

                        fig = px.scatter(df, x="거리(km)", y="보유수량", hover_data=["센터명", "주소"],
                                         labels={"거리(km)": "거리(km)", "보유수량": "보유 수량"}, title="센터 거리 vs 보유 수량")
                        st.plotly_chart(fig, use_container_width=True)

                else:
                    st.error("주소 인식 실패. 다시 시도해 주세요.")

        with col1:
            st.markdown(f"### {selected_sido} 내 {prefer_name} 보유 센터 지도")
            map_center = [lat, lon] if user_address and confirm == "예" else [df['위도'].mean(), df['경도'].mean()]
            m = folium.Map(location=map_center, zoom_start=11)

            df_grouped = df.groupby("지역구")["보유수량"].sum().reset_index()
            folium.Choropleth(
                geo_data=geo_data,
                name="choropleth",
                data=df_grouped,
                columns=["지역구", "보유수량"],
                key_on="feature.properties.SIG_KOR_NM",
                fill_color="PuRd",
                fill_opacity=0.75,
                line_opacity=0.2,
                highlight=True
            ).add_to(m)

            for _, row in df.iterrows():
                folium.Marker(
                    location=[row["위도"], row["경도"]],
                    popup=folium.Popup(f"<b>{row['센터명']}</b><br>{row['주소']}<br>{row['보유수량']}개", max_width=250),
                    icon=folium.Icon(color='red', icon='info-sign')
                ).add_to(m)

            if user_address and confirm == "예":
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(f"<b>검색 위치</b><br>{full_addr}", max_width=250),
                    icon=folium.Icon(color='blue', icon='user')
                ).add_to(m)

            st_folium(m, height=670, use_container_width=True)


        st.markdown("### 📄 푸드뱅크 상세 정보 (거리순)")
        st.dataframe(df[["센터명", "주소", "전화번호", "보유수량", "거리(km)"]], hide_index=True)
except Exception as e:
    st.error(f"오류 발생: {e}")
