import streamlit as st
import pandas as pd
import plotly.express as px
import os 


main_page = st.Page("./main_page.py", title="메인", icon="🛒")
page_1 = st.Page("./page_1.py", title="푸드뱅크/마켓 물품 조회", icon="🏢")
page_2 = st.Page("./page_2.py", title="물품 공급 제안", icon="🔗")

# Set up navigation 
pg = st.navigation([main_page, page_1, page_2])
st.set_page_config(layout="wide")

sidebar_logo = "./logo_sidebar.png"
main_logo = "./logo_main.png"
st.logo(image=sidebar_logo, icon_image=main_logo, size='large')

st.markdown("""
    <style>
    /* 사이드바 로고 이미지 */
    [data-testid="stSidebar"] img {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 70%;
        height: auto;
        margin-top: 30px;
        margin-bottom: 30px;
    }

    # /* 메인 바디 헤더 로고 이미지 */
    # img[data-testid="stLogo"] {
    #     width: 4rem !important;
    # }
    </style>
""", unsafe_allow_html=True)

# Run the selected page
pg.run()


