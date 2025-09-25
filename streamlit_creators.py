import streamlit as st
import pandas as pd
import sqlite3
import datetime

def show_creators():
    # Helper function to format numbers (K, M)
    def format_number(n):
        try:
            if pd.isna(n):
                return "0"
            if n >= 1_000_000:
                return f"{n/1_000_000:.1f}M"
            elif n >= 1_000:
                return f"{n/1_000:.1f}K"
            else:
                return str(int(n))
        except:
            return str(n)

    # App title
    st.markdown("### <u>Creators Dashboard</u>", unsafe_allow_html=True)

    # === Connect to SQLite DB and get available date range ===
    db_path = "database/tiktokdb.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT MIN(crawl_date), MAX(crawl_date) FROM creators")
    min_date, max_date = cursor.fetchone()
    conn.close()

    if not min_date or not max_date:
        st.warning("No data available in creators table.")
        return

    # === Date selection based on DB values ===
    selected_date = st.date_input(
        "Select Date",
        min_value=pd.to_datetime(min_date).date(),
        max_value=pd.to_datetime(max_date).date(),
        value=pd.to_datetime(max_date).date(),
        key="creators_date"
    )

    # === Query creators table for selected date ===
    conn = sqlite3.connect(db_path)
    query = f"""
    SELECT * FROM creators
    WHERE crawl_date = '{selected_date}'
    """
    df = pd.read_sql(query, conn)

    # === Query creators table for previous day ===
    prev_date = pd.to_datetime(selected_date) - pd.Timedelta(days=1)
    query_prev = f"""
    SELECT * FROM creators
    WHERE crawl_date = '{prev_date.date()}'
    """
    df_prev = pd.read_sql(query_prev, conn)
    conn.close()

    if df.empty:
        st.warning("No data found for selected date.")
        return

    # Verify required columns exist
    required_cols = {
        "nickname", "user_id", "follower_count",
        "creator_rank", "video_item_id",
        "video_play_count", "video_like_count"
    }
    if not required_cols.issubset(df.columns):
        st.error(f"Database table must include columns: {', '.join(required_cols)}")
        return

    # Preprocess columns for display
    df["play_display"] = df["video_play_count"].apply(format_number)
    df["like_display"] = df["video_like_count"].apply(format_number)
    df["follower_display"] = df["follower_count"].apply(format_number)

    # ============ KPI Overview ============
    st.subheader("Overall Metrics")

    # Current metrics
    total_creators = df["user_id"].nunique()
    total_followers = df.groupby("user_id")["follower_count"].max().sum()
    total_videos = df["video_item_id"].nunique()
    total_views = df["video_play_count"].sum()
    total_likes = df["video_like_count"].sum()
    avg_engagement = (df["video_like_count"] / df["video_play_count"]).mean()

    # Previous day metrics (if available)
    if not df_prev.empty:
        prev_total_creators = df_prev["user_id"].nunique()
        prev_total_followers = df_prev.groupby("user_id")["follower_count"].max().sum()
        prev_total_videos = df_prev["video_item_id"].nunique()
        prev_total_views = df_prev["video_play_count"].sum()
        prev_total_likes = df_prev["video_like_count"].sum()
        prev_avg_engagement = (df_prev["video_like_count"] / df_prev["video_play_count"]).mean()
    else:
        prev_total_creators = prev_total_followers = prev_total_videos = prev_total_views = prev_total_likes = prev_avg_engagement = 0

    # Top creator and video (display name only, delta only compares values)
    top_creator = (
        df.groupby(["user_id","nickname"])["follower_count"]
        .max().sort_values(ascending=False)
        .reset_index().iloc[0]
    )
    top_creator_name = top_creator["nickname"]
    top_creator_followers = top_creator["follower_count"]
    top_creator_followers_display = format_number(top_creator_followers)

    # Previous day's top creator followers value
    if not df_prev.empty:
        prev_top_creator_followers = df_prev.groupby(["user_id"])["follower_count"].max().max()
    else:
        prev_top_creator_followers = 0

    top_video = (
        df.groupby(["video_item_id","nickname"])["video_play_count"]
        .max().sort_values(ascending=False)
        .reset_index().iloc[0]
    )
    top_video_creator = top_video["nickname"]
    top_video_views = top_video["video_play_count"]
    top_video_views_display = format_number(top_video_views)

    # Previous day's top video views value
    if not df_prev.empty:
        prev_top_video_views = df_prev.groupby(["video_item_id"])["video_play_count"].max().max()
    else:
        prev_top_video_views = 0

    # Display KPI metrics (delta only for numeric values)
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Top Creator by Followers", top_creator_name, delta=format_number(top_creator_followers - prev_top_creator_followers))
    kpi2.metric("Top Video by Views", top_video_creator, delta=format_number(top_video_views - prev_top_video_views))
    kpi3.metric("Unique Creators", total_creators, delta=total_creators - prev_total_creators)

    kpi4, kpi5, kpi6, kpi7 = st.columns(4)
    kpi4.metric("Total Videos", total_videos, delta=total_videos - prev_total_videos)
    kpi5.metric("Total Views", format_number(total_views), delta=format_number(total_views - prev_total_views))
    kpi6.metric("Total Likes", format_number(total_likes), delta=format_number(total_likes - prev_total_likes))
    kpi7.metric("Avg Engagement Rate", f"{avg_engagement:.2%}", delta=f"{(avg_engagement - prev_avg_engagement):.2%}")

    # ============ Top Creators ============
    st.subheader("Top 20 Creators by Followers")
    top_creators = (
        df.groupby(["user_id","nickname","profile_url"])["follower_count"]
        .max().sort_values(ascending=False).head(20).reset_index()
    )
    top_creators["follower_display"] = top_creators["follower_count"].apply(format_number)

    st.data_editor(
        top_creators[["nickname","profile_url","follower_count","follower_display"]],
        column_config={
            "nickname": st.column_config.TextColumn("Creator Name"),
            "profile_url": st.column_config.LinkColumn("Creator Profile"),
            "follower_count": st.column_config.NumberColumn("Followers (Sort by)", format="%d"),
            "follower_display": st.column_config.TextColumn("Followers"),
        },
        hide_index=True
    )

    # ============ Top Videos ============
    st.subheader("Top 20 Videos by Play Count")
    if "video_url" in df.columns:
        top_videos = (
            df.groupby(["video_item_id","video_url","nickname"])[["video_play_count","video_like_count"]]
            .max().sort_values("video_play_count",ascending=False).head(20).reset_index()
        )
        top_videos["play_display"] = top_videos["video_play_count"].apply(format_number)
        top_videos["like_display"] = top_videos["video_like_count"].apply(format_number)

        st.data_editor(
            top_videos[["video_url","nickname","video_play_count","play_display","video_like_count","like_display"]],
            column_config={
                "video_url": st.column_config.LinkColumn("Video Link"),
                "nickname": st.column_config.TextColumn("Creator"),
                "video_play_count": st.column_config.NumberColumn("Views (Sort by)", format="%d"),
                "play_display": st.column_config.TextColumn("Views"),
                "video_like_count": st.column_config.NumberColumn("Likes (Sort by)", format="%d"),
                "like_display": st.column_config.TextColumn("Likes"),
            },
            hide_index=True
        )
    else:
        st.warning("Database does not include video_url column.")

    # ============ Filter by Category ============
    if "video_type" in df.columns:
        st.subheader("Top 20 Videos by Category")
        categories = ["All"] + df["video_type"].dropna().unique().tolist()
        selected_cat = st.selectbox("Select a Category", categories)
        filtered_df = df if selected_cat=="All" else df[df["video_type"]==selected_cat]

        top_cat_videos = filtered_df.sort_values("video_play_count",ascending=False).head(20).reset_index(drop=True)
        top_cat_videos["play_display"] = top_cat_videos["video_play_count"].apply(format_number)
        top_cat_videos["like_display"] = top_cat_videos["video_like_count"].apply(format_number)

        show_cols = ["video_type","nickname","video_play_count","play_display","video_like_count","like_display"]
        if "video_url" in top_cat_videos.columns:
            show_cols.insert(1,"video_url")

        st.data_editor(
            top_cat_videos[show_cols],
            column_config={
                "video_url": st.column_config.LinkColumn("Video Link") if "video_url" in show_cols else None,
                "video_type": st.column_config.TextColumn("Category"),
                "nickname": st.column_config.TextColumn("Creator"),
                "video_play_count": st.column_config.NumberColumn("Views (Sort by)", format="%d"),
                "play_display": st.column_config.TextColumn("Views"),
                "video_like_count": st.column_config.NumberColumn("Likes (Sort by)", format="%d"),
                "like_display": st.column_config.TextColumn("Likes"),
            },
            hide_index=True
        )

    # ============ Display All Data ============
    st.subheader("All Data from DB")
    df_all = df.copy()
    df_all.insert(0,"No.",range(1,len(df_all)+1))
    df_all["user_id_str"] = df_all["user_id"].astype(str)
    df_all["video_item_id_str"] = df_all["video_item_id"].astype(str)

    # Filters
    col1,col2,col3,col4 = st.columns(4)
    creators = df_all["nickname"].dropna().unique().tolist()
    selected_creator = col1.selectbox("Creator Name", ["All"]+creators)
    video_types = df_all["video_type"].dropna().unique().tolist() if "video_type" in df_all.columns else []
    selected_video_type = col2.selectbox("Video Type", ["All"]+video_types)
    creator_ranks = df_all["creator_rank"].dropna().unique().tolist() if "creator_rank" in df_all.columns else []
    selected_creator_rank = col3.selectbox("Creator Rank", ["All"]+sorted(creator_ranks))
    video_ranks = df_all["video_rank"].dropna().unique().tolist() if "video_rank" in df_all.columns else []
    selected_video_rank = col4.selectbox("Video Rank", ["All"]+sorted(video_ranks))

    if selected_creator!="All":
        df_all = df_all[df_all["nickname"]==selected_creator]
    if selected_video_type!="All":
        df_all = df_all[df_all["video_type"]==selected_video_type]
    if selected_creator_rank!="All":
        df_all = df_all[df_all["creator_rank"]==selected_creator_rank]
    if selected_video_rank!="All":
        df_all = df_all[df_all["video_rank"]==selected_video_rank]

    columns_to_show = [
        "No.","nickname","uniqueId","user_id_str","follower_count","bio",
        "creator_rank","video_type","video_item_id_str","video_name",
        "video_url","profile_url","video_play_count","video_like_count","video_rank"
    ]

    st.data_editor(
        df_all[columns_to_show],
        column_config={
            "No.": st.column_config.NumberColumn("No.", format="%d"),
            "nickname": st.column_config.TextColumn("Creator Name"),
            "uniqueId": st.column_config.TextColumn("Unique ID"),
            "user_id_str": st.column_config.TextColumn("User ID"),
            "follower_count": st.column_config.NumberColumn("Followers", format="%d"),
            "bio": st.column_config.TextColumn("Bio"),
            "creator_rank": st.column_config.NumberColumn("Creator Rank", format="%d"),
            "video_type": st.column_config.TextColumn("Video Type"),
            "video_item_id_str": st.column_config.TextColumn("Video Item ID"),
            "video_name": st.column_config.TextColumn("Video Name"),
            "video_url": st.column_config.LinkColumn("Video Link"),
            "profile_url": st.column_config.LinkColumn("Profile URL"),
            "video_play_count": st.column_config.NumberColumn("Video Views", format="%d"),
            "video_like_count": st.column_config.NumberColumn("Video Likes", format="%d"),
            "video_rank": st.column_config.NumberColumn("Video Rank", format="%d"),
        },
        hide_index=True,
        use_container_width=True,
        key="all_creators_data"
    )
