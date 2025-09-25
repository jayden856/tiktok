import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import datetime

def show_posts():
    def format_number(n):
        try:
            if pd.isna(n):
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
    st.markdown("### <u>Posts Dashboard</u>", unsafe_allow_html=True)

    # === Connect to SQLite DB and get available date range ===
    db_path = r"C:\Users\USER\Documents\Tunetouch\Code\Tiktok\testing\database\tiktokdb.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT MIN(crawl_date), MAX(crawl_date) FROM posts")
    min_date, max_date = cursor.fetchone()
    conn.close()

    if not min_date or not max_date:
        st.warning("No data available in posts table.")
        return

    # === Date selection based on DB values ===
    selected_date = st.date_input(
        "Select Date",
        min_value=pd.to_datetime(min_date).date(),
        max_value=pd.to_datetime(max_date).date(),
        value=pd.to_datetime(max_date).date(),
        key="posts_date"
    )

    # === Query posts table for selected date ===
    conn = sqlite3.connect(db_path)
    query = f"""
    SELECT * FROM posts
    WHERE crawl_date = '{selected_date}'
    """
    df = pd.read_sql(query, conn)
    conn.close()

    if df.empty:
        st.warning("No data found for selected date.")
        return

    # Format numbers for display
    df['play_count_dis'] = df['play_count'].apply(format_number)
    df['like_count_dis'] = df['like_count'].apply(format_number)

    # === KPI Overview ===
    st.subheader("Overall Metrics")
    total_plays = df['play_count'].sum()
    total_likes = df['like_count'].sum()
    total_videos = len(df)
    avg_engagement = (df['like_count'] / df['play_count']).mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Plays", format_number(total_plays))
    col2.metric("Total Likes", format_number(total_likes))
    col3.metric("Total Videos", total_videos)
    col4.metric("Avg Engagement Rate", f"{avg_engagement:.2%}")

    # === Required Columns Check ===
    required_cols = {'genre', 'play_count', 'like_count'}
    if not required_cols.issubset(df.columns):
        st.error("Database table must include columns: genre, play_count, like_count.")
        return

    # === Genre average statistics ===
    genre_avg = df.groupby('genre')[['play_count', 'like_count']].mean().round(0).reset_index()
    genre_avg['play_count_dis'] = genre_avg['play_count'].apply(format_number)
    genre_avg['like_count_dis'] = genre_avg['like_count'].apply(format_number)

    st.subheader("Average Metrics by Genre")
    st.data_editor(
        genre_avg[['genre','play_count','play_count_dis','like_count','like_count_dis']],
        column_config={
            "genre": st.column_config.TextColumn("Genre"),
            "play_count": st.column_config.NumberColumn("Avg Plays (Sort by)", format="%d"),
            "play_count_dis": st.column_config.TextColumn("Avg Plays"),
            "like_count": st.column_config.NumberColumn("Avg Likes (Sort by)", format="%d"),
            "like_count_dis": st.column_config.TextColumn("Avg Likes"),
        },
        hide_index=True,
        use_container_width=True
    )

    # === Chart Section ===
    st.subheader("Average Play Count by Genre")
    fig_play = px.bar(
        genre_avg,
        x="genre",
        y="play_count",
        color="genre",
        labels={"genre": "Genre", "play_count": "Average Play Count"},
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(fig_play, use_container_width=True)

    st.subheader("Average Like Count by Genre")
    fig_like = px.bar(
        genre_avg,
        x="genre",
        y="like_count",
        color="genre",
        labels={"genre": "Genre", "like_count": "Average Like Count"},
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig_like, use_container_width=True)

    # === Engagement Rate Analysis ===
    st.subheader("Engagement Rate by Genre")
    df["engagement_rate"] = df["like_count"] / df["play_count"]
    genre_engagement = df.groupby("genre")["engagement_rate"].mean().sort_values(ascending=False)
    fig_engagement = px.bar(
        genre_engagement,
        x=genre_engagement.index,
        y=genre_engagement.values,
        color=genre_engagement.index,
        labels={"x": "Genre", "y": "Avg Engagement Rate"},
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig_engagement.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig_engagement, use_container_width=True)

    # === Filter Top Videos / Creators ===
    st.subheader("Filter Top Videos / Creators")
    col1, col2 = st.columns(2)
    creators = df["nickname"].unique().tolist()
    genres = df["genre"].unique().tolist()
    selected_creator = col1.selectbox("Select Creator", ["All"] + creators)
    selected_genre = col2.selectbox("Select Genre", ["All"] + genres)
    df_filtered = df.copy()
    if selected_creator != "All":
        df_filtered = df_filtered[df_filtered["nickname"] == selected_creator]
    if selected_genre != "All":
        df_filtered = df_filtered[df_filtered["genre"] == selected_genre]

    # === Top 20 Videos / Creators Combined Ranking ===
    top20_play = df_filtered.sort_values(by='play_count', ascending=False).head(20)
    top20_like = df_filtered.sort_values(by='like_count', ascending=False).head(20)
    top_videos = pd.concat([top20_play, top20_like]).drop_duplicates().reset_index(drop=True)
    creator_stats = df_filtered.groupby("nickname")[["play_count","like_count"]].sum().reset_index()
    top_videos = top_videos.merge(creator_stats, on="nickname", suffixes=("", "_creator"))

    # Format display columns
    top_videos["play_count_dis"] = top_videos["play_count"].apply(format_number)
    top_videos["like_count_dis"] = top_videos["like_count"].apply(format_number)
    top_videos["play_count_creator_dis"] = top_videos["play_count_creator"].apply(format_number)
    top_videos["like_count_creator_dis"] = top_videos["like_count_creator"].apply(format_number)

    st.subheader("Top 20 Videos & Creators Combined Ranking")
    st.data_editor(
        top_videos[[
            "url","nickname","genre",
            "play_count","play_count_dis","like_count","like_count_dis",
            "play_count_creator","play_count_creator_dis",
            "like_count_creator","like_count_creator_dis"
        ]],
        column_config={
            "url": st.column_config.LinkColumn("Video Link"),
            "nickname": st.column_config.TextColumn("Creator"),
            "genre": st.column_config.TextColumn("Genre"),
            "play_count": st.column_config.NumberColumn("Video Plays (Sort by)", format="%d"),
            "play_count_dis": st.column_config.TextColumn("Video Plays"),
            "like_count": st.column_config.NumberColumn("Video Likes (Sort by)", format="%d"),
            "like_count_dis": st.column_config.TextColumn("Video Likes"),
            "play_count_creator": st.column_config.NumberColumn("Total Plays (Creator)", format="%d"),
            "play_count_creator_dis": st.column_config.TextColumn("Total Plays"),
            "like_count_creator": st.column_config.NumberColumn("Total Likes (Creator)", format="%d"),
            "like_count_creator_dis": st.column_config.TextColumn("Total Likes"),
        },
        hide_index=True,
        use_container_width=True
    )

    # === Correlation Scatter Plot ===
    st.subheader("Correlation: Video Plays vs Likes")
    fig_scatter = px.scatter(
        df_filtered,
        x="play_count",
        y="like_count",
        color="genre",
        hover_data=["nickname", "url"],
        labels={"play_count": "Video Plays", "like_count": "Video Likes"}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # === Display All Data from DB ===
    st.subheader("All Data from DB")
    df_display = df.copy()
    df_display.insert(0, "No.", range(1, len(df_display) + 1))
    df_display["user_id_str"] = df_display["user_id"].astype(str)
    df_display["item_id_str"] = df_display["item_id"].astype(str)

    col1, col2 = st.columns(2)
    creators = df_display["nickname"].dropna().unique().tolist()
    selected_creator = col1.selectbox("Filter by Creator", ["All"] + creators)
    genres = df_display["genre"].dropna().unique().tolist()
    selected_genre = col2.selectbox("Filter by Genre", ["All"] + genres)

    df_filtered = df_display.copy()
    if selected_creator != "All":
        df_filtered = df_filtered[df_filtered["nickname"] == selected_creator]
    if selected_genre != "All":
        df_filtered = df_filtered[df_filtered["genre"] == selected_genre]

    columns_to_show = ["No.","url","nickname","user_id_str","item_id_str","item_name","genre","like_count","play_count"]
    st.data_editor(
        df_filtered[columns_to_show],
        column_config={
            "No.": st.column_config.NumberColumn("No.", format="%d"),
            "url": st.column_config.LinkColumn("Video Link"),
            "nickname": st.column_config.TextColumn("Creator"),
            "user_id_str": st.column_config.TextColumn("User ID"),
            "item_id_str": st.column_config.TextColumn("Item ID"),
            "item_name": st.column_config.TextColumn("Item Name"),
            "genre": st.column_config.TextColumn("Genre"),
            "like_count": st.column_config.NumberColumn("Likes", format="%d"),
            "play_count": st.column_config.NumberColumn("Plays", format="%d"),
        },
        hide_index=True,
        use_container_width=True
    )
