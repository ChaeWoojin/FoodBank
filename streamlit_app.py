import streamlit as st

# Define the pages
main_page = st.Page("main_page.py", title="푸드뱅크/마켓 물품 조회", icon="🏢")
page_2 = st.Page("page_2.py", title="물품 공급 제안", icon="🔗")

# Set up navigation
pg = st.navigation([main_page, page_2])
st.set_page_config(layout="wide")

# Run the selected page
pg.run()