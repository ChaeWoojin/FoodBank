import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import seaborn as sns
import matplotlib.pyplot as plt
import requests
import time
import xml.etree.ElementTree as ET
import matplotlib.font_manager as fm

font_path = "./MALGUN.TTF" 
font_name = fm.FontProperties(fname=font_path).get_name()
plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False


from api import getPreferInfo
from dict import areaCd, unitySignguCd, spctrCd, preferCnttgClscd

# ---------------------------
# 사이드바 메뉴
menu = st.sidebar.radio("메뉴 선택", ["전국 푸드뱅크 지도", "보유 물품 현황 조회"])

# ---------------------------
# 공통 변수
KAKAO_REST_API_KEY = "7758866813611c4b671d0ed485e11ce3"

def geocode_address_kakao(address):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}
    params = {"query": address}
    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 200:
        result = res.json()
        if result['documents']:
            loc = result['documents'][0]
            return float(loc['y']), float(loc['x'])  # 위도, 경도
    return None, None

@st.cache_data
def geocode_csv(df):
    geocoded_data = []
    progress = st.progress(0)
    for idx, row in df.iterrows():
        address = row["소재지도로명주소"] if pd.notnull(row["소재지도로명주소"]) else row["소재지지번주소"]
        lat, lon = geocode_address_kakao(address)
        if lat and lon:
            geocoded_data.append({
                "센터명": row["상호명"],
                "센터구분": row["센터구분"],
                "시도명": row["시도명"],
                "시군구명": row["시군구명"],
                "주소": address,
                "전화번호": row["전화번호"],
                "위도": lat,
                "경도": lon
            })
        progress.progress((idx + 1) / len(df))
        time.sleep(0.1)
    progress.empty()
    return pd.DataFrame(geocoded_data)


# ---------------------------
# 메뉴 1: 전국 푸드뱅크 지도
if menu == "전국 푸드뱅크 지도":
    st.title("전국 푸드뱅크 지도")

    raw_df = pd.read_csv("foodbank.csv", encoding="cp949")
    df = geocode_csv(raw_df)

    if not df.empty:
        st.sidebar.title("🔍 센터 필터링")
        selected_sido = st.sidebar.selectbox("시도 선택", sorted(df["시도명"].unique()))
        filtered_df = df[df["시도명"] == selected_sido]

        selected_sigungu = st.sidebar.selectbox("시군구 선택", sorted(filtered_df["시군구명"].unique()))
        filtered_df = filtered_df[filtered_df["시군구명"] == selected_sigungu]

        selected_center = st.sidebar.selectbox("센터 선택", sorted(filtered_df["센터명"].unique()))
        selected_row = filtered_df[filtered_df["센터명"] == selected_center].iloc[0]

        st.subheader("📍 지도 시각화")
        layer = pdk.Layer(
            "ScatterplotLayer",
            filtered_df,
            get_position='[경도, 위도]',
            get_radius=1000,
            get_fill_color='[255, 140, 0, 140]',
            pickable=True,
        )
        tooltip = {
            "html": "<b>{센터명}</b><br/>주소: {주소}",
            "style": {"backgroundColor": "white", "color": "black"}
        }
        view_state = pdk.ViewState(
            latitude=selected_row["위도"],
            longitude=selected_row["경도"],
            zoom=11
        )
        st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip))

        with st.expander("✅ 선택한 센터 정보"):
            st.write(f"**센터명**: {selected_row['센터명']}")
            st.write(f"**센터구분**: {selected_row['센터구분']}")
            st.write(f"**주소**: {selected_row['주소']}")
            st.write(f"**전화번호**: {selected_row['전화번호']}")
    else:
        st.warning("데이터가 없습니다.")

elif menu == "보유 물품 현황 조회":
    st.title("📦 보유 물품 현황 조회")

    # 1. 지역 선택
    selected_area_name = st.sidebar.selectbox("지역 선택", sorted(areaCd.values()))
    selected_area_code = [k for k, v in areaCd.items() if v == selected_area_name][0]

    # 2. 시군구 선택
    sigungu_options = {k: v for k, v in unitySignguCd.items() if k.startswith(selected_area_code)}
    sigungu_names = ["선택 안 함"] + sorted(sigungu_options.values())
    selected_sigungu_name = st.sidebar.selectbox("시군구 선택", sigungu_names)

    selected_sigungu_code = None
    if selected_sigungu_name != "선택 안 함":
        selected_sigungu_code = [k for k, v in sigungu_options.items() if v == selected_sigungu_name][0]

    # 3. 센터 선택
    matching_centers = {
        k: v for k, v in spctrCd.items()
        if selected_sigungu_name != "선택 안 함" and selected_sigungu_name[:2] in v
    } if selected_sigungu_code else {}

    center_names = ["선택 안 함"] + sorted(matching_centers.values())
    selected_center_name = st.sidebar.selectbox("센터 선택", center_names)

    selected_center_code = None
    if selected_center_name != "선택 안 함":
        selected_center_code = [k for k, v in matching_centers.items() if v == selected_center_name][0]

    # 4. API 호출
    dfs = []
    with st.spinner("📡 공공데이터 API에서 보유 물품 정보를 조회 중입니다..."):
        if selected_center_code:  # 단일 센터 조회
            df = getPreferInfo(
                page_no=1,
                num_of_rows=100,
                area_cd=selected_area_code,
                unity_signgu_cd=selected_sigungu_code,
                spctr_cd=selected_center_code
            )
            if not df.empty:
                df["센터명"] = selected_center_name
                dfs.append(df)
        elif selected_sigungu_code:  # 시군구 전체 센터 조회
            for center_code, center_name in matching_centers.items():
                df = getPreferInfo(
                    page_no=1,
                    num_of_rows=100,
                    area_cd=selected_area_code,
                    unity_signgu_cd=selected_sigungu_code,
                    spctr_cd=center_code
                )
                if not df.empty:
                    df["센터명"] = center_name
                    dfs.append(df)
        else:  # 지역만으로 조회 (시군구 및 센터 선택 안 함)
            df = getPreferInfo(
                page_no=1,
                num_of_rows=100,
                area_cd=selected_area_code,
                unity_signgu_cd=None,
                spctr_cd=None
            )
            if not df.empty:
                df["센터명"] = df["spctrCd"].map(spctrCd)  # 코드 → 센터명 매핑
                dfs.append(df)

    # 5. 결과 출력
    if dfs:
        df_all = pd.concat(dfs, ignore_index=True)
        df_all["물품명"] = df_all["preferCnttgClscd"].map(preferCnttgClscd)
        df_grouped = df_all.groupby(["센터명", "물품명"])["holdQy"].sum().reset_index()

        st.subheader("✅ 센터별 보유 물품 수량")
        st.dataframe(df_grouped)

        st.subheader("📊 물품 수량 시각화")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=df_grouped, y="물품명", x="holdQy", hue="센터명", ax=ax)
        ax.set_xlabel("보유 수량")
        ax.set_ylabel("물품 종류")
        ax.legend(title="센터명", bbox_to_anchor=(1.05, 1), loc='upper left')
        st.pyplot(fig)
    else:
        st.warning("조회된 데이터가 없습니다.")
