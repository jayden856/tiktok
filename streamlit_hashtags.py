import streamlit as st
import pandas as pd
import sqlite3
import datetime

def show_hashtags():
    def format_number(n):
        try:
            if pd.isna(n) or n == "":
                return ""
            if n >= 1_000_000:
                return f"{n/1_000_000:.1f}M"
            elif n >= 1_000:
                return f"{n/1_000:.1f}K"
            else:
                return str(int(n))
        except:
            return str(n)

    # App title
    st.markdown("### <u>Hashtags Dashboard</u>", unsafe_allow_html=True)

    # === Connect to SQLite DB ===
    db_path = r"C:\Users\USER\Documents\Tunetouch\Code\Tiktok\testing\database\tiktokdb.db"
    conn = sqlite3.connect(db_path)

    # Get min and max date from database
    minmax_query = "SELECT MIN(crawl_date) as min_date, MAX(crawl_date) as max_date FROM hashtags"
    minmax_df = pd.read_sql(minmax_query, conn)

    if minmax_df.empty or minmax_df["min_date"].iloc[0] is None:
        st.warning("No data found in database. Please run crawler first.")
        conn.close()
        return

    min_date = datetime.datetime.strptime(minmax_df["min_date"].iloc[0], "%Y-%m-%d").date()
    max_date = datetime.datetime.strptime(minmax_df["max_date"].iloc[0], "%Y-%m-%d").date()

    # === Select one crawl_date ===
    query_dates = f"SELECT DISTINCT crawl_date FROM hashtags ORDER BY crawl_date"
    dates_df = pd.read_sql(query_dates, conn)
    available_dates = [datetime.datetime.strptime(d, "%Y-%m-%d").date() for d in dates_df["crawl_date"].tolist()]

    selected_date = st.date_input(
        "Select Date",
        min_value=min(available_dates),
        max_value=max(available_dates),
        value=max(available_dates),
        key="hashtags_date"
    )

    # Query hashtags for selected date
    query = f"""
    SELECT * FROM hashtags
    WHERE crawl_date = '{selected_date}'
    """
    df = pd.read_sql(query, conn)
    conn.close()

    if df.empty:
        st.warning("No data found for selected date.")
        return

    if "industry_value" not in df.columns:
        df["industry_value"] = ""

    df = df.dropna(subset=["hashtag_name"])
    df['video_views_dis'] = df['video_views'].apply(format_number)
    df['publish_count_dis'] = df['publish_count'].apply(format_number)

    # === KPI Overview ===
    st.subheader("Overall Metrics")
    total_views = df['video_views'].sum()
    total_hashtags = df['hashtag_name'].nunique()
    total_posts = df['publish_count'].sum()
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Hashtag Views", format_number(total_views))
    col2.metric("Unique Hashtags", total_hashtags)
    col3.metric("Total Posts", format_number(total_posts))

    # === Top Hashtags by Views ===
    st.subheader("Top 20 Hashtags by Views")
    industries_views = [i for i in df["industry_value"].dropna().unique() if i != ""]
    selected_industry_views = st.selectbox("Select Industry (Views)", ["All"] + industries_views, key="hashtags_views_industry")

    df_views = df.copy()
    if selected_industry_views != "All":
        df_views = df_views[df_views["industry_value"] == selected_industry_views]

    top20_views = (
        df_views.groupby(["hashtag_name", "industry_value"], dropna=False)["video_views"]
        .sum()
        .sort_values(ascending=False)
        .head(20)
        .reset_index()
    )
    top20_views['video_views_dis'] = top20_views['video_views'].apply(format_number)

    st.data_editor(
        top20_views[["hashtag_name", "industry_value", "video_views", "video_views_dis"]],
        column_config={
            "hashtag_name": st.column_config.TextColumn("Hashtag"),
            "industry_value": st.column_config.TextColumn("Industry"),
            "video_views": st.column_config.NumberColumn("Views (Sort by)", format="%d"),
            "video_views_dis": st.column_config.TextColumn("Views")
        },
        hide_index=True,
        use_container_width=True
    )

    # === Top Hashtags by Post Count ===
    st.subheader("Top 20 Hashtags by Post Count")
    industries_posts = [i for i in df["industry_value"].dropna().unique() if i != ""]
    selected_industry_posts = st.selectbox("Select Industry (Posts)", ["All"] + industries_posts, key="hashtags_posts_industry")

    df_posts = df.copy()
    if selected_industry_posts != "All":
        df_posts = df_posts[df_posts["industry_value"] == selected_industry_posts]

    top20_posts = (
        df_posts.groupby(["hashtag_name", "industry_value"], dropna=False)["publish_count"]
        .sum()
        .sort_values(ascending=False)
        .head(20)
        .reset_index()
    )
    top20_posts['publish_count_dis'] = top20_posts['publish_count'].apply(format_number)

    st.data_editor(
        top20_posts[["hashtag_name", "industry_value", "publish_count", "publish_count_dis"]],
        column_config={
            "hashtag_name": st.column_config.TextColumn("Hashtag"),
            "industry_value": st.column_config.TextColumn("Industry"),
            "publish_count": st.column_config.NumberColumn("Posts (Sort by)", format="%d"),
            "publish_count_dis": st.column_config.TextColumn("Posts")
        },
        hide_index=True,
        use_container_width=True
    )

    # === Full Dataset Display ===
    st.subheader("All Data from DB")

    industries_all = [i for i in df["industry_value"].dropna().unique() if i != ""]
    selected_industry_all = st.selectbox("Select Industry (All Data)", ["All"] + industries_all, key="hashtags_all_industry")

    df_all = df.copy()
    if selected_industry_all != "All":
        df_all = df_all[df_all["industry_value"] == selected_industry_all]

    df_all.insert(0, "No.", range(1, len(df_all) + 1))
    df_all["hashtag_id"] = df_all["hashtag_id"].astype(str)

    st.data_editor(
        df_all,
        column_config={
            "No.": st.column_config.NumberColumn("No.", format="%d"),
            "hashtag_id": st.column_config.TextColumn("Hashtag ID"),
            "hashtag_name": st.column_config.TextColumn("Hashtag Name"),
            "country": st.column_config.TextColumn("Country"),
            "rank": st.column_config.NumberColumn("Rank", format="%d"),
            "video_views": st.column_config.NumberColumn("Video Views (Raw)", format="%d"),
            "video_views_dis": st.column_config.TextColumn("Video Views"),
            "publish_count": st.column_config.NumberColumn("Publish Count (Raw)", format="%d"),
            "publish_count_dis": st.column_config.TextColumn("Publish Count"),
            "industry_value": st.column_config.TextColumn("Industry"),
        },
        hide_index=True,
        use_container_width=True
    )
