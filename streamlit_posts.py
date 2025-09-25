import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import datetime

def show_posts():
    # Helper function to format numbers (K, M)
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
    db_path = "database/tiktokdb.db"
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

    # === Query posts table for selected date and previous day ===
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(f"SELECT * FROM posts WHERE crawl_date = '{selected_date}'", conn)
    prev_date = pd.to_datetime(selected_date) - pd.Timedelta(days=1)
    df_prev = pd.read_sql(f"SELECT * FROM posts WHERE crawl_date = '{prev_date.date()}'", conn)
    conn.close()

    if df.empty:
        st.warning("No data found for selected date.")
        return

    # Format numbers for display
    df['play_count_dis'] = df['play_count'].apply(format_number)
    df['like_count_dis'] = df['like_count'].apply(format_number)

    # === KPI Overview with delta compared to previous day ===
    st.subheader("Overall Metrics")

    # Current metrics
    total_plays = df['play_count'].sum()
    total_likes = df['like_count'].sum()
    total_videos = len(df)
    avg_engagement = (df['like_count'] / df['play_count']).mean()

    # Previous day metrics
    if not df_prev.empty:
        prev_total_plays = df_prev['play_count'].sum()
        prev_total_likes = df_prev['like_count'].sum()
        prev_total_videos = len(df_prev)
        prev_avg_engagement = (df_prev['like_count'] / df_prev['play_count']).mean()
    else:
        prev_total_plays = prev_total_likes = prev_total_videos = prev_avg_engagement = 0

    # === Top Creator ===
    top_creator_row = df.groupby("nickname")["play_count"].sum().sort_values(ascending=False)
    top_creator_name = top_creator_row.index[0]
    top_creator_plays = top_creator_row.iloc[0]

    # Previous day Top Creator plays
    if not df_prev.empty and top_creator_name in df_prev["nickname"].values:
        prev_top_creator_plays = df_prev.groupby("nickname")["play_count"].sum().get(top_creator_name, 0)
    else:
        prev_top_creator_plays = 0

    # === Top Genre ===
    top_genre_row = df.groupby("genre")["play_count"].sum().sort_values(ascending=False)
    top_genre_name = top_genre_row.index[0]
    top_genre_plays = top_genre_row.iloc[0]

    # Previous day Top Genre plays
    if not df_prev.empty and top_genre_name in df_prev["genre"].values:
        prev_top_genre_plays = df_prev.groupby("genre")["play_count"].sum().get(top_genre_name, 0)
    else:
        prev_top_genre_plays = 0

    # Display KPIs
    # First row: Top Creator & Top Genre
    row1_col1, row1_col2, row1_col3 = st.columns(3)
    row1_col1.metric("Top Creator", top_creator_name, delta=format_number(top_creator_plays - prev_top_creator_plays))
    row1_col2.metric("Top Creator Plays", format_number(top_creator_plays), delta=format_number(top_creator_plays - prev_top_creator_plays))
    row1_col3.metric("Top Genre", top_genre_name, delta=format_number(top_genre_plays - prev_top_genre_plays))

    # Second row: Top Genre Plays & Total Plays & Total Likes
    row2_col1, row2_col2, row2_col3 = st.columns(3)
    row2_col1.metric("Top Genre Plays", format_number(top_genre_plays), delta=format_number(top_genre_plays - prev_top_genre_plays))
    row2_col2.metric("Total Plays", format_number(total_plays), delta=format_number(total_plays - prev_total_plays))
    row2_col3.metric("Total Likes", format_number(total_likes), delta=format_number(total_likes - prev_total_likes))
    # Optional: add more KPIs as needed

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

    # === Charts & Remaining Sections ===
    # Play count by genre
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

    # Like count by genre
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

    # Engagement Rate
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

    # Correlation scatter plot
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

    # All Data Table
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
