import streamlit as st
from streamlit_creators import show_creators
from streamlit_posts import show_posts
from streamlit_hashtags import show_hashtags

# Page configuration
st.set_page_config(
    page_title="TikTok Dashboard",
    page_icon="image/tiktok.png",
    layout="wide"
)

# CSS to adjust max width
st.markdown(
    """
    <style>
    .block-container {
        max-width: 1200px;   /* 1000, 1100, 1300 */
        margin: auto;        /* Center the content */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.image("image/tiktok.png", width=80) 

st.title("TikTok Trending Dashboard")

# Tab pages
tab1, tab2, tab3 = st.tabs(["Creators", "Posts", "Hashtags"])

with tab1:
    show_creators()
with tab2:
    show_posts()
with tab3:
    show_hashtags()
