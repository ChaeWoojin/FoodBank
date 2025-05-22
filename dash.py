import streamlit as st
import pandas as pd
import matplotlib.font_manager as fm
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
import utils
import plotly.graph_objects as go
from var import areaCd, unitySignguCd, preferCnttgClscd, spctrCd, spctrSecd as spctrSecd_dict
from pathlib import Path

# ✅ 한글 폰트 등록
font_path = "./data/MALGUN.TTF"
if Path(font_path).exists():
    fm.fontManager.addfont(font_path)
    plt.rcParams['font.family'] = 'Malgun Gothic'
else:
    st.warning("❗ MALGUN.TTF 폰트 파일을 ./data 폴더에 넣어주세요.")

st.set_page_config(layout="wide")
st.title("📦 지역 기반 보유 수량 시각화 대시보드")

# ------------------------
# 센터 정보 로드
# ------------------------
@st.cache_data
def load_centers():
    return pd.read_csv("./data/food_centers_with_region_and_coords.csv", encoding="utf-8", dtype=object).dropna(subset=["위도", "경도"])

centers_df = load_centers()

# ------------------------
# 🧭 탭 구성
# ------------------------
tab1, tab2 = st.tabs(["🏢 푸드뱅크/마켓 물품 조회", "🔗 물품 공급 제안"])

# ------------------------
# 🏢 Tab 1: 푸드뱅크/마켓 위치 + 물품 barplot
# ------------------------
with tab1:
    col1, col2 = st.columns([1,2])
    with col1:
        selected_sido = st.selectbox("시도 선택 (Tab1)", list(areaCd.values()), key="tab1_sido")
        selected_sido_code = [k for k, v in areaCd.items() if v == selected_sido][0]

    with col2:
        sigungu_options = {k: v for k, v in unitySignguCd.items() if k.startswith(selected_sido_code)}
        selected_sigungu_name = st.selectbox("지역구 선택", list(sigungu_options.values()), key="tab1_sigungu")
        selected_sigungu_code = [k for k, v in sigungu_options.items() if v == selected_sigungu_name][0]
        

    filtered_df = centers_df[(centers_df["areaCd"] == selected_sido_code) & (centers_df["unitySignguCd"] == selected_sigungu_code)]

    col1, col2 = st.columns([1, 2])
    with col1:
        centers_df_map = filtered_df.copy()
        if not centers_df_map.empty:
            st.markdown("### 🗺️ 푸드뱅크/마켓 위치 지도")
            centers_df_map["센터명"] = centers_df_map["spctrCd"].map(spctrCd)
            centers_df_map["tooltip"] = centers_df_map.apply(
                lambda row: f"{row['센터명']}\n주소: {row['spctrAdres']}\n전화: {row['spctrTelno']}", axis=1
            )
            centers_df_map[["위도", "경도"]] = centers_df_map[["위도", "경도"]].astype(float)
            centers_df_map.rename(columns={"위도": "lat", "경도": "lon"}, inplace=True)

            import pydeck as pdk
            scatter_layer = pdk.Layer(
                "ScatterplotLayer",
                data=centers_df_map,
                get_position="[lon, lat]",
                get_radius=100,
                get_fill_color="[0, 100, 200, 160]",
                pickable=True
            )

            text_layer = pdk.Layer(
                "TextLayer",
                data=centers_df_map,
                get_position="[lon, lat]",
                get_text="센터명",
                get_size=14,
                get_color=[40, 40, 40],
                get_angle=0,
                get_alignment_baseline="top"
            )

            view_state = pdk.ViewState(
                latitude=centers_df_map["lat"].mean(),
                longitude=centers_df_map["lon"].mean(),
                zoom=11,
                pitch=0
            )

            st.pydeck_chart(
                pdk.Deck(
                    map_style="mapbox://styles/mapbox/light-v9",
                    initial_view_state=view_state,
                    layers=[scatter_layer, text_layer],
                    tooltip={"text": "{tooltip}"}
                ),
                height=400
            )
        else:
            st.markdown("### 해당 지역에는 푸드뱅크/마켓이 없습니다")

        # # Leaflet용 JSON 생성
        # food_centers = [
        #     {
        #         "label": row["spctrCd"],
        #         "name": spctrCd.get(row["spctrCd"], row["spctrCd"]),
        #         "address": row["spctrAdres"],
        #         "phone": row["spctrTelno"],
        #         "lat": row["위도"],
        #         "lon": row["경도"],
        #         "sido": areaCd.get(row["areaCd"], row["areaCd"]),
        #         "sigungu": unitySignguCd.get(row["unitySignguCd"], row["unitySignguCd"]),
        #         "type": spctrSecd_dict.get(row["spctrSecd"], row["spctrSecd"])
        #     }
        #     for _, row in filtered_df.iterrows()
        # ]

        # food_centers_json = json.dumps(food_centers, ensure_ascii=False)

        # html_string = f"""
        # <!DOCTYPE html>
        # <html><head><meta charset='utf-8' />
        # <link rel='stylesheet' href='https://unpkg.com/leaflet@1.9.3/dist/leaflet.css' />
        # <script src='https://unpkg.com/leaflet@1.9.3/dist/leaflet.js'></script>
        # <style>#map {{ height: 650px; border-radius: 12px; }}</style></head>
        # <body><div id='map'></div><script>
        # const map = L.map('map').setView([36.5, 127.8], 7);
        # L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(map);
        # const centers = {food_centers_json};
        # centers.forEach(c => {{
        #     const popup = `<b>${{c.name}}</b><br/>주소: ${{c.address}}<br/>전화: ${{c.phone}}<br/><i>${{c.sido}} ${{c.sigungu}}</i><br/><span style='color:gray;'>[${{c.type}}]</span>`;
        #     let color = c.type === "푸드마켓" ? "#28a745" : c.type === "물류센터" ? "#fd7e14" : "#007BFF";
        #     L.circleMarker([c.lat, c.lon], {{ radius: 6, color, fillColor: color, fillOpacity: 0.9 }}).bindPopup(popup).addTo(map);
        # }});
        # if (centers.length > 0) {{
        #     const group = new L.featureGroup(centers.map(c => L.marker([c.lat, c.lon])));
        #     map.fitBounds(group.getBounds());
        # }}
        # </script></body></html>
        # """
        # components.html(html_string, height=650)

    # 📊 보유수량 시각화
    with col2:
        col2_1, col2_2 = st.columns(2)
        with col2_1:
            @st.cache_data
            def load_prefer_by_region(area_cd, unity_signgu_cd):
                records = []
                for prefer_code, prefer_name in preferCnttgClscd.items():
                    df = utils.getPreferInfo(prefer_cnttg_clscd=prefer_code, area_cd=area_cd, unity_signgu_cd=unity_signgu_cd)
                    if not df.empty:
                        df["물품명"] = prefer_name
                        df["보유수량"] = df["holdQy"]
                        records.append(df[["물품명", "보유수량"]])
                if len(records) > 0:
                    return pd.concat(records) 
                else:
                    return pd.DataFrame(records) 
                
            df = load_prefer_by_region(area_cd=selected_sido_code, unity_signgu_cd=selected_sigungu_code)
            if not df.empty:
                df_grouped = df.groupby("물품명")["보유수량"].sum().reset_index().sort_values("보유수량", ascending=False)
                st.markdown(f"### 📈 {selected_sigungu_name} 지역 보유 상위 품목")
                st.dataframe(df_grouped,
                            column_order=("물품명", "보유수량"),
                            hide_index=True,
                            use_container_width=True,
                            height=400,
                            column_config={
                                "물품명": st.column_config.TextColumn("물품명"),
                                "보유수량": st.column_config.ProgressColumn(
                                    "보유 수량",
                                    format="%d개",
                                    min_value=0,
                                    max_value=max(int(df_grouped["보유수량"].max()), 10)
                                )
                            })
            else:
                st.warning("보유 수량 정보가 없습니다.")
        
        with col2_2:
            st.markdown("### 🏬 센터별 보유 현황")
            selected_prefer_item = st.selectbox("선호 물품 선택", list(preferCnttgClscd.values()), key="col2_prefer")
            selected_prefer_code = [k for k, v in preferCnttgClscd.items() if v == selected_prefer_item][0]

            @st.cache_data
            def load_prefer_by_item(area_cd, unity_signgu_cd, prefer_code):
                df = utils.getPreferInfo(prefer_cnttg_clscd=prefer_code, area_cd=area_cd, unity_signgu_cd=unity_signgu_cd)
                df["센터명"] = df["spctrCd"].map(spctrCd)
                df["보유수량"] = df["holdQy"].astype(float)
                return df.dropna(subset=["센터명"])

            df_item = load_prefer_by_item(area_cd=selected_sido_code, unity_signgu_cd=selected_sigungu_code, prefer_code=selected_prefer_code)
            df_item = pd.merge(df_item, filtered_df[['spctrCd', '위도', '경도']], on='spctrCd', how='inner')
            df_item.rename(columns={'위도': 'lat', '경도': 'lon'}, inplace=True)
            df_item[['lat', 'lon']] = df_item[['lat', 'lon']].apply(pd.to_numeric, errors='coerce').fillna(0)
            
            if not df_item.empty:
                import pydeck as pdk
                chart_data = df_item.copy()
                chart_data["tooltip_text"] = chart_data.apply(
                    lambda row: f"{row['센터명']}\n보유수량: {int(row['보유수량'])}개", axis=1
                )

                column_layer = pdk.Layer(
                    "ColumnLayer",
                    data=chart_data,
                    get_position="[lon, lat]",
                    get_elevation="보유수량",
                    elevation_scale=10,
                    radius=150,
                    get_fill_color="[180, 0, 200, 140]",
                    pickable=True,
                    auto_highlight=True
                )
                view_state = pdk.ViewState(
                    latitude=chart_data["lat"].mean(),
                    longitude=chart_data["lon"].mean(),
                    zoom=11,
                    pitch=50
                )
                st.pydeck_chart(pdk.Deck(
                    map_style="mapbox://styles/mapbox/light-v9",
                    initial_view_state=view_state,
                    layers=[column_layer],
                    tooltip={"text": "{tooltip_text}"}
                    ),
                    height=315
                  )
            else:
                st.info("해당 물품을 보유한 센터 정보가 없습니다.")


# ------------------------
# 🔗 Tab 2: 물품 공급 제안
# ------------------------
with tab2:
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        selected_sido2 = st.selectbox("시도 선택", list(areaCd.values()), key="tab2_sido")
        selected_sido_code2 = [k for k, v in areaCd.items() if v == selected_sido2][0]

    with col2:
        sigungu_options2 = {k: v for k, v in unitySignguCd.items() if k.startswith(selected_sido_code2)}
        selected_sigungu_name2 = st.selectbox("지역구 선택", list(sigungu_options2.values()), key="tab2_sigungu")
        selected_sigungu_code2 = [k for k, v in sigungu_options2.items() if v == selected_sigungu_name2][0]

    with col3:
        options = ["🍜 라면류", "🌾 쌀(곡식류)", "🌾 밀가루(류)", "🌶 고추장(류)", 
                   "🫘 된장(류)", "🥄 참기름", "🥓 (즉석)가공햄류", "🛢 식용유(류)", 
                   "🥫 통조림류", "🍬 설탕(류)", "🧂 간장(류)", "🍜 소면류(국수)", 
                   "🥢 김(류)", "🍱 즉석밥류", "🧴 샴푸", "🪥 치약", "🧼 비누"]
        prefer_code = st.pills(
            "물품 종류", options, selection_mode="single"
        )

    col1, col2 = st.columns([1, 2])
    with col1:
        filtered_df = centers_df.copy()
        df = utils.getPreferInfo(prefer_cnttg_clscd=prefer_code, area_cd=selected_sido_code2)
        df_sigungu = df[df['unitySignguCd'] == selected_sigungu_code2]
        if not df_sigungu.empty:
            st.dataframe(df_sigungu)
    # with col2:
        

    # # ✅ 데이터 로드 및 정제
    # centers_df = pd.read_csv("./data/food_centers_with_region_and_coords.csv", dtype=object)
    # centers_df["userCo"] = pd.to_numeric(centers_df["userCo"], errors="coerce").fillna(0)
    # centers_df["시군구"] = centers_df["unitySignguCd"].map(unitySignguCd)
    # centers_df["시도"] = centers_df["areaCd"].map(areaCd)

    # prefer_data = []
    # for code, name in preferCnttgClscd.items():
    #     df = utils.getPreferInfo(prefer_cnttg_clscd=code, area_cd=selected_sido_code2)
    #     if not df.empty:
    #         df["시군구"] = df["unitySignguCd"].map(unitySignguCd)
    #         df["품목"] = name
    #         df["보유수량"] = pd.to_numeric(df["holdQy"], errors="coerce").fillna(0)
    #         prefer_data.append(df[["시군구", "품목", "보유수량"]])
    # prefer_df = pd.concat(prefer_data)

    # user_stats = centers_df[centers_df["시도"] == selected_sido2].groupby("시군구")["userCo"].sum().reset_index()
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