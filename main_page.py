import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from var import areaCd, spctrCd, unitySignguCd

# 🎉 타이틀 & 소개
st.markdown("## 🍽️ 푸드링크에 오신 걸 환영합니다!")
st.markdown("#### 당신의 손길이 지역의 따뜻한 식탁이 됩니다.")
st.write(
    "푸드링크는 전국 푸드뱅크 및 마켓의 물품 보유 현황을 시각화하고, "
    "필요한 물품 공급을 제안할 수 있는 데이터 기반 플랫폼입니다."
)
st.divider()

# 🔍 주요 기능
st.markdown("### 🔍 주요 기능")
col1, col2, col3 = st.columns(3)

with col1:
    with st.container():
        st.markdown("#### 🏢 푸드뱅크 조회")
        st.caption("지역별 보유 물품을 한눈에 확인하세요.")

        # 예시 데이터 (용산푸드마켓 보유 품목)
        df_yongsan = pd.DataFrame({
            "물품명": ["라면류", "즉석밥류", "쌀", "김", "통조림류", "간장", "샴푸"],
            "보유수량": [120, 95, 80, 60, 40, 0, 0]
        })

        df_grouped = df_yongsan.sort_values("보유수량", ascending=False)

        st.dataframe(
            df_grouped,
            column_order=("물품명", "보유수량"),
            hide_index=True,
            use_container_width=True,
            height=250,
            column_config={
                "물품명": st.column_config.TextColumn("물품명"),
                "보유수량": st.column_config.ProgressColumn(
                    "보유 수량",
                    format="%d개",
                    min_value=0,
                    max_value=max(int(df_grouped["보유수량"].max()), 10)
                )
            }
        )
        
import plotly.express as px

with col2:
    with st.container():
        st.markdown("#### 📊 통계 요약")
        st.caption("다양한 수치로 지역의 필요를 파악하세요.")

        # 예시 데이터
        df = pd.DataFrame({
            "지역구": ["용산구", "강남구", "은평구", "성동구", "송파구"],
            "보유수량": [120, 300, 180, 220, 90]
        })

        # 트렌디한 색상 팔레트 적용
        fig = px.bar(
            df, x="지역구", y="보유수량", color="지역구",
            color_discrete_sequence=px.colors.qualitative.Set3,
            height=250
        )
        fig.update_layout(
            showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)

with col3:
    with st.container():
        st.markdown("#### 🔗 공급 제안")
        st.caption("필요한 곳에 적절한 물품을 제안하세요.")
        
        # 예시 데이터: 즉석밥류 수요 vs 보유수량
        df_supply = pd.DataFrame({
            "지역구": ["강남구", "용산구", "성동구", "송파구", "은평구"],
            "예상수요": [150, 130, 120, 140, 100],
            "보유수량": [80, 90, 100, 70, 95]
        })
        df_supply["공급제안량"] = df_supply["예상수요"] - df_supply["보유수량"]
        df_supply["공급제안량"] = df_supply["공급제안량"].apply(lambda x: max(x, 0))

        # 트렌디한 색상 팔레트 적용
        fig = px.bar(
            df_supply, x="지역구", y="공급제안량", color="지역구",
            color_discrete_sequence=px.colors.qualitative.Pastel1,
            height=250,
            labels={"공급제안량": "제안 수량"}
        )
        fig.update_layout(
            showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)

        # 텍스트 예시
        st.markdown("""
        📦 예: *강남푸드뱅크에 즉석밥류 50개 제안*  
        📍 조건: `재고 부족` + `수요 많음`
        """, unsafe_allow_html=True)


# 데이터 로드 (캐시 포함)
@st.cache_data
def load_centers():
    return pd.read_csv("./data/food_centers_with_region_and_coords.csv", encoding="utf-8", dtype=object).dropna(subset=["위도", "경도"])

centers_df = load_centers()

col1, col2 = st.columns(2)

# 📍 왼쪽: 지도 표시
with col1:
    st.markdown("### 🗺️ 전국 푸드뱅크 위치")
    m = folium.Map(location=[36.5, 127.8], zoom_start=7)
    for _, row in centers_df.iterrows():
        try:
            # 안전하게 데이터 추출 (결측치 대비)
            spctr_cd = spctrCd.get(row["spctrCd"], row["spctrCd"])
            adres = row.get("spctrAdres", "")
            detail_adres = row.get("spctrDetailAdres", "")
            telno = row.get("spctrTelno", "번호 없음")

            # tooltip 구성
            popup_html = f"""
                <b>센터명:</b>{spctr_cd}<br>
                <b>주소:</b> {adres} {detail_adres} <br>
                <b>전화번호:</b> {telno}
            """

            # 마커 추가
            folium.Marker(
                location=[float(row["위도"]), float(row["경도"])],
                popup=folium.Popup(popup_html, max_width=250),
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(m)

        except Exception as e:
            # 오류 발생 시 로그 표시 (선택사항)
            st.warning(f"지도 마커 생성 중 오류: {e}")

    st_folium(m, height=500, use_container_width=True)


with col2:
    st.markdown("### 푸드뱅크/마켓 목록")
    select_sido = st.selectbox('시도 선택', areaCd.values())
    select_sido_code = [k for k, v in areaCd.items() if v==select_sido][0]
    
    temp_df = centers_df[centers_df['areaCd']==select_sido_code]
    filtered_df = temp_df.copy()
    filtered_df['spctrCd'] = filtered_df['spctrCd'].map(spctrCd)
    filtered_df['unitySignguCd'] = filtered_df['unitySignguCd'].map(unitySignguCd)
    filtered_df['Adres'] = filtered_df['spctrAdres'] + filtered_df['spctrDetailAdres'] 
    filtered_df.rename(
        columns={
        'spctrCd': '센터명', 
        'unitySignguCd': '지역구', 
        'spctrTelno': '전화번호', 
        'Adres': '주소'
    }, inplace=True)
    filtered_df = filtered_df[['센터명', '지역구', '전화번호', '주소']]
    filtered_df = filtered_df.sort_values(by=['지역구'], axis=0)
    st.dataframe(filtered_df, height=400, hide_index=True)