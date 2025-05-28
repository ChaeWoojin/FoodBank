import streamlit as st
import pandas as pd
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import pydeck as pdk
import plotly.express as px
import utils
from var import areaCd, unitySignguCd, preferCnttgClscd, spctrCd, spctrSecd as spctrSecd_dict
from pathlib import Path

st.markdown("# 🏢 푸드뱅크/마켓 물품 조회")

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

ITEM_COLORS = {
    "라면류": [255, 99, 132],
    "쌀(곡식류)": [54, 162, 235],
    "밀가루(류)": [255, 206, 86],
    "고추장(류)": [75, 192, 192],
    "된장(류)": [153, 102, 255],
    "참기름": [255, 159, 64],
    "(즉석)가공햄류": [199, 199, 199],
    "식용유(류)": [83, 102, 255],
    "통조림류": [255, 102, 255],
    "설탕(류)": [102, 255, 178],
    "간장(류)": [102, 178, 255],
    "소면류(국수)": [204, 102, 255],
    "김(류)": [255, 153, 102],
    "즉석밥류": [100, 100, 100],
    "샴푸": [0, 255, 255],
    "치약": [255, 0, 255],
    "비누": [0, 255, 0]
}

options = ["🍜 라면류", "🌾 쌀(곡식류)", "🌾 밀가루(류)", "🌶 고추장(류)", 
            "🍲 된장(류)", "🧴 참기름", "🥓 (즉석)가공햄류", "🧴 식용유(류)", 
            "🥫 통조림류", "🍬 설탕(류)", "🧂 간장(류)", "🍜 소면류(국수)", 
            "🍙 김(류)", "🍱 즉석밥류", "🧴 샴푸", "🪥 치약", "🧼 비누"]

selected_sido = st.sidebar.selectbox("시도 선택", list(areaCd.values()), key="tab1_sido")
selected_sido_code = [k for k, v in areaCd.items() if v == selected_sido][0]

sigungu_options = {k: v for k, v in unitySignguCd.items() if k.startswith(selected_sido_code)}
selected_sigungu_name = st.sidebar.selectbox("지역구 선택", list(sigungu_options.values()), key="tab1_sigungu")
selected_sigungu_code = [k for k, v in sigungu_options.items() if v == selected_sigungu_name][0]
    
filtered_df = centers_df[(centers_df["areaCd"] == selected_sido_code) & (centers_df["unitySignguCd"] == selected_sigungu_code)]

st.markdown("### 🔍선호 물품 선택")
selected_items = st.pills("선호 물품 선택", options, selection_mode="multi", default=options, label_visibility="collapsed")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏬 센터별 보유 현황")
    selected_items = [item[2:] for item in selected_items]
    
    records = []
    offset_dict = {}
    for i, item in enumerate(selected_items):
        code = [k for k, v in preferCnttgClscd.items() if v == item][0]
        df = utils.getPreferInfo(prefer_cnttg_clscd=code, area_cd=selected_sido_code, unity_signgu_cd=selected_sigungu_code)
        if not df.empty:
            df["물품명"] = item
            df["color"] = [ITEM_COLORS.get(item, [180, 180, 180])] * len(df)
            df["x_offset"] = (i - len(selected_items) / 2) * 0.001  # longitude offset to separate bars
            records.append(df)

    if records:
        df_all = pd.concat(records)
        df_all["센터명"] = df_all["spctrCd"].map(spctrCd)
        df_all["보유수량"] = df_all["holdQy"].astype(float)
        df_all = pd.merge(df_all, filtered_df[["spctrCd", "위도", "경도"]], on='spctrCd', how='inner')
        df_all.rename(columns={'위도': 'lat', '경도': 'lon'}, inplace=True)
        df_all[['lat', 'lon']] = df_all[['lat', 'lon']].apply(pd.to_numeric, errors='coerce').fillna(0)
        df_all["lon"] = df_all["lon"] + df_all["x_offset"]

        df_all["tooltip_text"] = df_all.apply(
            lambda row: f"{row['센터명']}\n{row['물품명']} 보유수량: {int(row['보유수량'])}개", axis=1
        )

        column_layers = []
        for item in selected_items:
            item_df = df_all[df_all["물품명"] == item]
            if not item_df.empty:
                layer = pdk.Layer(
                    "ColumnLayer",
                    data=item_df,
                    get_position="[lon, lat]",
                    get_elevation="보유수량",
                    elevation_scale=10,
                    radius=150,
                    get_fill_color="color",
                    pickable=True,
                    auto_highlight=True
                )
                column_layers.append(layer)

        if column_layers:
            view_state = pdk.ViewState(
                latitude=df_all["lat"].mean(),
                longitude=df_all["lon"].mean(),
                zoom=11,
                pitch=50
            )

            st.pydeck_chart(
                pdk.Deck(
                    map_style="mapbox://styles/mapbox/light-v9",
                    initial_view_state=view_state,
                    layers=column_layers,
                    tooltip={"text": "{tooltip_text}"}
                ),
                height=450
            )
        else:
            st.info("시각화할 수 있는 유효한 물품 데이터가 없습니다.")
    else:
        st.info("해당 물품을 보유한 센터 정보가 없습니다.")


with col2:
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
        st.markdown(f"### 📈 {selected_sigungu_name} 보유 상위 품목")
        df_grouped["color"] = df_grouped["물품명"].map(lambda x: f"rgb{tuple(ITEM_COLORS.get(x, [180, 180, 180]))}")

        fig = px.bar(
            df_grouped,
            x="보유수량",
            y="물품명",
            color="물품명",
            color_discrete_map={name: f"rgb{tuple(color)}" for name, color in ITEM_COLORS.items()},
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("보유 수량 정보가 없습니다.")
