import streamlit as st
from streamlit_creators import show_creators
from streamlit_posts import show_posts
from streamlit_hashtags import show_hashtags

# === Page configuration ===
st.set_page_config(
    page_title="TikTok Dashboard",
    page_icon="image/tiktok.png",
    layout="wide"
)

# === Custom CSS ===
st.markdown(
    """
    <style>
    /* Adjust max width */
    .block-container {
        max-width: 1200px;
        margin: auto;
    }

    /* Metric cards styling */
    [data-testid="stMetric"] {
        border: 2px solid #FFD1DC;  /* 淡粉色边框 */
        border-radius: 10px;
        padding: 15px;
        background-color: #FFF0F5;  /* 淡粉色背景 */
    }

    /* Data editor / tables styling */
    div[data-testid="stDataEditor"] {
        border: 2px solid #FFD1DC;  /* 淡粉色边框 */
        border-radius: 10px;
        padding: 10px;
        background-color: #FFF0F5;  /* 淡粉色背景 */
    }

    /* Optional: make column headers bold */
    div[data-testid="stDataEditor"] th {
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# === Logo and title ===
st.image("image/tiktok.png", width=80)
st.title("TikTok Trending Dashboard")

# === Tabs ===
tab1, tab2, tab3 = st.tabs(["Creators", "Posts", "Hashtags"])

with tab1:
    show_creators()
with tab2:
    show_posts()
with tab3:
    show_hashtags()
