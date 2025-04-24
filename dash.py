import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import seaborn as sns
import matplotlib.pyplot as plt
import requests
import time
import xml.etree.ElementTree as ET  # 공공데이터 API용


# ---------------------------
# 사이드바 메뉴
menu = st.sidebar.radio("메뉴 선택", ["전국 푸드뱅크 지도", "선호 물품 분포 조회"])

if menu == "전국 푸드뱅크 지도":
    st.title("전국 푸드뱅크 지도")

    # =========================
    # API 설정
    KAKAO_REST_API_KEY = "7758866813611c4b671d0ed485e11ce3"
    PUBLIC_API_SERVICE_KEY = "j6wUNyCq/4vEC5xyrSKR99EsHqzxY3LvbI+kQUn+DgwsT0EfL/fkpPnWEN3d++3T2mbvOPPZUmnhYg3QxC5jFw=="
    PUBLIC_API_BASE_URL = "http://apis.data.go.kr/B460014/foodBankInfoService2"

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

    # =========================
    # 공공데이터 API + 지오코딩 (지금은 주석 처리)
    # @st.cache_data
    # def get_public_api_data(stdr_ym='201802'):
    #     url = f"{PUBLIC_API_BASE_URL}/getSpctrInfo"
    #     params = {
    #         "serviceKey": PUBLIC_API_SERVICE_KEY,
    #         "dataType": "xml",
    #         "pageNo": 1,
    #         "numOfRows": 100,
    #         "stdrYm": stdr_ym,
    #     }
    #     headers = {"Accept": "text/xml"}
    #     response = requests.get(url, params=params, headers=headers)
    #     root = ET.fromstring(response.content)

    #     centers = []
    #     for i in root.findall(".//item"):
    #         address = i.findtext("spctrAdres")
    #         name = i.findtext("spctrCd")
    #         rcept_amt = i.findtext("rceptAmt")
    #         provd_amt = i.findtext("provdAmt")
    #         undtake_amt = i.findtext("undtakeAmt")
    #         trnsfer_amt = i.findtext("trnsferAmt")
    #         user_co = i.findtext("userCo")

    #         lat, lon = geocode_address_kakao(address)
    #         if lat and lon:
    #             centers.append({
    #                 "센터명": name,
    #                 "주소": address,
    #                 "접수금액": rcept_amt,
    #                 "제공금액": provd_amt,
    #                 "인수금액": undtake_amt,
    #                 "이관금액": trnsfer_amt,
    #                 "이용자수": user_co,
    #                 "위도": lat,
    #                 "경도": lon
    #             })
    #     return pd.DataFrame(centers)

    # =========================
    # 카카오 지오코딩 (기본 흐름)
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
            time.sleep(0.1)  # API 호출 제한 대응
        
        progress.empty()
        return pd.DataFrame(geocoded_data)

    # =========================
    # 1. CSV 불러오기 → 카카오 API (기본)
    raw_df = pd.read_csv("foodbank.csv", encoding="cp949")
    df = geocode_csv(raw_df)

    # 2. 공공데이터 API (작동 시 사용 가능)
    # df = get_public_api_data()

    if not df.empty:
        # -------------------- 사이드바 필터링 --------------------
        st.sidebar.title("🔍 센터 필터링")
        selected_sido = st.sidebar.selectbox("시도 선택", sorted(df["시도명"].unique()))
        filtered_df = df[df["시도명"] == selected_sido]

        selected_sigungu = st.sidebar.selectbox("시군구 선택", sorted(filtered_df["시군구명"].unique()))
        filtered_df = filtered_df[filtered_df["시군구명"] == selected_sigungu]

        selected_center = st.sidebar.selectbox("센터 선택", sorted(filtered_df["센터명"].unique()))
        selected_row = filtered_df[filtered_df["센터명"] == selected_center].iloc[0]

        # -------------------- 지도 --------------------
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

        # -------------------- 상세 정보 --------------------
        with st.expander("✅ 선택한 센터 정보"):
            st.write(f"**센터명**: {selected_row['센터명']}")
            st.write(f"**센터구분**: {selected_row['센터구분']}")
            st.write(f"**주소**: {selected_row['주소']}")
            st.write(f"**전화번호**: {selected_row['전화번호']}")
    else:
        st.warning("데이터가 없습니다.")

elif menu == "선호 물품 분포 조회":
    st.title("선호 물품 분포 조회")
    st.write("📍 선택한 물품의 GeoHeatmap 시각화")

    # ---------------------------
    # 예시 데이터 (센터명, 위도, 경도, 물품 수량)
    centers = ["서울푸드뱅크", "부산푸드뱅크", "대구푸드뱅크", "광주푸드뱅크"]
    latitudes = [37.5665, 35.1796, 35.8714, 35.1595]
    longitudes = [126.9780, 129.0756, 128.6014, 126.8526]
    items = ["라면류", "쌀(곡식류)", "식용유(류)", "통조림류", "비누"]

    # 각 센터에 대해 물품별 수량 생성
    data = []
    for c, lat, lon in zip(centers, latitudes, longitudes):
        quantities = np.random.randint(10, 500, size=len(items))
        data.append({
            "센터명": c,
            "위도": lat,
            "경도": lon,
            **dict(zip(items, quantities))
        })
    df = pd.DataFrame(data)

    # ---------------------------
    # 사이드바에서 물품 선택
    selected_item = st.sidebar.selectbox("조회할 물품 선택", items)

    # pydeck을 위해 weight 컬럼 생성
    df["weight"] = df[selected_item]

    # ---------------------------
    # Heatmap Layer
    layer = pdk.Layer(
        "HeatmapLayer",
        df,
        get_position='[경도, 위도]',
        get_weight="weight",
        radiusPixels=60
    )

    # ---------------------------
    # View 설정
    view_state = pdk.ViewState(
        latitude=df["위도"].mean(),
        longitude=df["경도"].mean(),
        zoom=6
    )

    # ---------------------------
    # 지도 출력
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

    # ---------------------------
    # 데이터표 보여주기 (Optional)
    with st.expander("🔍 상세 데이터 보기"):
        st.dataframe(df[["센터명", selected_item]])