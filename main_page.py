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

st.markdown("# 🏢 푸드뱅크/마켓 물품 조회")

# ✅ 한글 폰트 등록
font_path = "./data/MALGUN.TTF"
if Path(font_path).exists():
    fm.fontManager.addfont(font_path)
    plt.rcParams['font.family'] = 'Malgun Gothic'
else:
    st.warning("❗ MALGUN.TTF 폰트 파일을 ./data 폴더에 넣어주세요.")


@st.cache_data
def load_centers():
    return pd.read_csv("./data/food_centers_with_region_and_coords.csv", encoding="utf-8", dtype=object).dropna(subset=["위도", "경도"])


centers_df = load_centers()

selected_sido = st.sidebar.selectbox("시도 선택 (Tab1)", list(areaCd.values()), key="tab1_sido")
selected_sido_code = [k for k, v in areaCd.items() if v == selected_sido][0]

sigungu_options = {k: v for k, v in unitySignguCd.items() if k.startswith(selected_sido_code)}
selected_sigungu_name = st.sidebar.selectbox("지역구 선택", list(sigungu_options.values()), key="tab1_sigungu")
selected_sigungu_code = [k for k, v in sigungu_options.items() if v == selected_sigungu_name][0]
    

filtered_df = centers_df[(centers_df["areaCd"] == selected_sido_code) & (centers_df["unitySignguCd"] == selected_sigungu_code)]

col1, col2 = st.columns([1, 2])
with col1:
    centers_df_map = filtered_df.copy()
    if not centers_df_map.empty:
        st.markdown(f"### 🗺️ {selected_sigungu_name} 푸드뱅크/마켓 위치")
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