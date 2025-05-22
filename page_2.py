import streamlit as st
import pandas as pd
import matplotlib.font_manager as fm
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
import utils
import json
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from var import areaCd, unitySignguCd, preferCnttgClscd, spctrCd, spctrSecd as spctrSecd_dict
from pathlib import Path
from math import radians, cos, sin, asin, sqrt



# ✅ 한글 폰트 등록
font_path = "./data/MALGUN.TTF"
if Path(font_path).exists():
    fm.fontManager.addfont(font_path)
    plt.rcParams['font.family'] = 'Malgun Gothic'
else:
    st.warning("❗ MALGUN.TTF 폰트 파일을 ./data 폴더에 넣어주세요.")
    
# GeoJSON 경로
geo_path = "./data/TL_SCCO_SIG.json"
with open(geo_path, encoding="utf-8") as f:
    geo_data = json.load(f)
    
@st.cache_data
def load_centers():
    return pd.read_csv("./data/food_centers_with_region_and_coords.csv", encoding="utf-8", dtype=object).dropna(subset=["위도", "경도"])

st.markdown("# 🔗 물품 공급 제안")

centers_df = load_centers()

selected_sido = st.sidebar.selectbox("시도 선택", list(areaCd.values()), key="tab2_sido")
selected_sido_code = [k for k, v in areaCd.items() if v == selected_sido][0]

options = ["🍜 라면류", "🌾 쌀(곡식류)", "🌾 밀가루(류)", "🌶 고추장(류)", 
            "🍲 된장(류)", "🧴 참기름", "🥓 (즉석)가공햄류", "🧴 식용유(류)", 
            "🥫 통조림류", "🍬 설탕(류)", "🧂 간장(류)", "🍜 소면류(국수)", 
            "🍙 김(류)", "🍱 즉석밥류", "🧴 샴푸", "🪥 치약", "🧼 비누"]


try:
    prefer_name = st.sidebar.pills(
        "물품 종류", options, selection_mode="single"
    )[2:]
    prefer_name_code = [k for k, v in preferCnttgClscd.items() if v == prefer_name][0]

    if prefer_name_code:
        filtered_df = centers_df.copy()
        df_sigungu = utils.getPreferInfo(area_cd=selected_sido_code, prefer_cnttg_clscd=prefer_name_code)
        df_sigungu = df_sigungu[df_sigungu['holdQy'] > 0]
        
        df = pd.merge(df_sigungu, filtered_df, how='inner', on=['spctrCd', 'areaCd', 'unitySignguCd'])
        # df = df[['areaCd', 'unitySignguCd', 'spctrCd', 'spctrTelno', 'spctrAdres', 'spctrDetailAdres' 'holdQy']]
        df['areaCd'] = df['areaCd'].map(areaCd)
        df['unitySignguCd'] = df['unitySignguCd'].map(unitySignguCd)
        df['spctrCd'] = df['spctrCd'].map(spctrCd)
        df['Addr'] = df['spctrAdres'] + df['spctrDetailAdres']
        
        df = df[['areaCd', 'unitySignguCd', 'spctrCd', 'spctrTelno', 'Addr', 'holdQy', '위도', '경도']]
        df = df.astype({'위도': 'float64', '경도': 'float64'})
        
        df.rename(columns={'areaCd': '시도명', 'unitySignguCd': '지역구', 'spctrCd': '센터명', 'holdQy': '보유수량', 'spctrTelno': '전화번호', 'Addr': '주소'}, inplace=True)
        
        if not df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"### {selected_sido} 내 {prefer_name} 보유 중인 푸드뱅크/마켓")
                lon = df['위도'].mean()
                lat = df['경도'].mean()

                m = folium.Map(location=[lon, lat], zoom_start=10)

                df_grouped = df.groupby("지역구")["보유수량"].sum().reset_index()
                df_grouped.columns = ["district", "value"]

                # ✅ fancy choropleth 추가
                choropleth = folium.Choropleth(
                    geo_data=geo_data,
                    name="choropleth",
                    data=df_grouped,
                    columns=["district", "value"],
                    key_on="feature.properties.SIG_KOR_NM",
                    fill_color="PuRd",
                    fill_opacity=0.75,
                    line_opacity=0.2,
                    highlight=True
                )
                choropleth.add_to(m)
                
                # ✅ star 마커 추가 (푸드뱅크/마켓 위치에 팝업 정보 포함)
                for _, row in df.iterrows():
                    popup_html = f"""
                    <b>센터명:</b> {row['센터명']}<br>
                    <b>주소:</b> {row['주소']}<br>
                    <b>전화번호:</b> {row['전화번호']}<br>
                    <b>보유수량:</b> {row['보유수량']}개
                    """
                    folium.Marker(
                        location=[row["위도"], row["경도"]],
                        popup=folium.Popup(popup_html, max_width=250),
                        icon=folium.Icon(color='red', icon='star', prefix='fa')  # Font Awesome 'star'
                    ).add_to(m)

                st_folium(m, width=500, height=800)
            
            with col2:
                st.markdown("### 가까운 센터 추천")

                # 사용자 입력
                user_address = st.text_input("주소를 입력하세요 (예: 서울특별시 중구 세종대로 110)", "")

                def geocode_kakao_query(address):
                    import requests
                    headers = {"Authorization": "KakaoAK 7758866813611c4b671d0ed485e11ce3"}
                    url = "https://dapi.kakao.com/v2/local/search/address.json"
                    params = {"query": address}
                    response = requests.get(url, headers=headers, params=params).json()
                    if response.get("documents"):
                        doc = response["documents"][0]
                        full_addr = doc["address"]["address_name"]
                        lat = float(doc["y"])
                        lon = float(doc["x"])
                        return full_addr, lat, lon
                    return None, None, None


                def haversine(lat1, lon1, lat2, lon2):
                    R = 6371  # km
                    dlat = radians(lat2 - lat1)
                    dlon = radians(lon2 - lon1)
                    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
                    c = 2 * asin(sqrt(a))
                    return R * c

                if user_address:
                    full_addr, lat, lon = geocode_kakao_query(user_address)
                    if full_addr:
                        confirm = st.radio(f"🔍 가장 유사한 주소는 다음과 같습니다:\n**{full_addr}**\n이 위치를 기준으로 추천을 진행할까요?", ("예", "아니오"), horizontal=True)
                        if confirm == "예":
                            df["거리(km)"] = df.apply(lambda row: haversine(lat, lon, row["위도"], row["경도"]), axis=1)
                            df_recommend = df[df["보유수량"] > 0].sort_values("거리(km)").reset_index(drop=True)

                            st.success(f"✅ 기준 주소: {full_addr} (위도: {lat:.5f}, 경도: {lon:.5f})")
                            st.markdown("### 🔽 가까운 순 추천 센터")
                            st.dataframe(df_recommend[["센터명", "주소", "전화번호", "보유수량", "거리(km)"]].round(2), hide_index=True, height=500)
                        else:
                            st.info("❗ 다른 주소로 다시 검색해주세요.")
                    else:
                        st.error("❌ 주소 인식 실패. 더 정확한 주소를 입력해 주세요.")
                else:
                    st.info("🏠 추천을 받으려면 주소를 입력해주세요.")

            st.markdown("### 푸드뱅크/마켓 상세 정보")                     
            st.dataframe(df.iloc[:,:-3], hide_index=True)
                        
        else:
            st.text("조회 결과가 없습니다")
    
except Exception as e:
    st.empty()
                
    
# # ✅ 데이터 로드 및 정제
# centers_df = pd.read_csv("./data/food_centers_with_region_and_coords.csv", dtype=object)
# centers_df["userCo"] = pd.to_numeric(centers_df["userCo"], errors="coerce").fillna(0)
# centers_df["시군구"] = centers_df["unitySignguCd"].map(unitySignguCd)
# centers_df["시도"] = centers_df["areaCd"].map(areaCd)

# prefer_data = []
# for code, name in preferCnttgClscd.items():
#     df = utils.getPreferInfo(prefer_cnttg_clscd=code, area_cd=selected_sido_code)
#     if not df.empty:
#         df["시군구"] = df["unitySignguCd"].map(unitySignguCd)
#         df["품목"] = name
#         df["보유수량"] = pd.to_numeric(df["holdQy"], errors="coerce").fillna(0)
#         prefer_data.append(df[["시군구", "품목", "보유수량"]])
# prefer_df = pd.concat(prefer_data)

# user_stats = centers_df[centers_df["시도"] == selected_sido].groupby("시군구")["userCo"].sum().reset_index()
# prefer_stats = prefer_df.groupby(["시군구", "품목"])["보유수량"].sum().reset_index()

# # ✅ 시각화
# left_col, mid_col, right_col = st.columns([1, 1, 2])

# with left_col:
#     st.markdown("### 👥 지역구별 이용자 수")
#     fig1, ax1 = plt.subplots(figsize=(6, len(user_stats) * 0.35))
#     user_stats_sorted = user_stats.sort_values("userCo", ascending=False)
#     colors = ["#ff6f61" if name in selected_sigungu_names else "#6baed6" for name in user_stats_sorted["시군구"]]
#     ax1.barh(user_stats_sorted["시군구"], user_stats_sorted["userCo"], color=colors)
#     ax1.set_xlabel("이용자 수")
#     ax1.invert_yaxis()
#     st.pyplot(fig1)

# with mid_col:
#     st.markdown("### 🔗 물품 공급 제안: 부족 ↔ 여유 비교")
#     pivot = prefer_stats.pivot(index="시군구", columns="품목", values="보유수량").fillna(0)
#     shortages = (pivot < pivot.mean()).stack().reset_index()
#     shortages.columns = ["시군구", "품목", "수량"]
#     shortages = shortages[shortages["시군구"].isin(selected_sigungu_names)]

#     supply_candidates = []
#     for _, row in shortages.iterrows():
#         others = pivot[pivot[row["품목"]] > pivot[row["품목"]].mean()]
#         for donor in others.index:
#             supply_candidates.append({
#                 "부족 지역구": row["시군구"],
#                 "품목": row["품목"],
#                 "수량(부족)": row["수량"],
#                 "공급 지역구": donor,
#                 "수량(공급)": pivot.loc[donor, row["품목"]]
#             })

#     if supply_candidates:
#         df_supply = pd.DataFrame(supply_candidates).sort_values(by="수량(부족)")
#         st.dataframe(df_supply, use_container_width=True)
#     else:
#         st.info("선택한 지역구의 공급-부족 매칭 결과가 없습니다.")

# with right_col:
#     st.markdown("### 📊 선호 물품별 지역구 보유 수량 비교")
#     if not prefer_stats.empty:
#         fig = go.Figure()
#         for sigungu in selected_sigungu_names:
#             subset = prefer_stats[prefer_stats["시군구"] == sigungu]
#             fig.add_trace(go.Bar(
#                 x=subset["품목"],
#                 y=subset["보유수량"],
#                 name=sigungu
#             ))
#         fig.update_layout(
#             barmode="group",
#             xaxis_title="선호 물품",
#             yaxis_title="보유 수량",
#             xaxis_tickangle=-45
#         )
#         st.plotly_chart(fig, use_container_width=True)
#     else:
#         st.info("보유 수량 데이터가 없습니다.")