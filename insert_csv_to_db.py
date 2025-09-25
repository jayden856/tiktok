import sqlite3
import os
import pandas as pd

# === Database path ===
db_path = r"C:\Users\USER\Documents\Tunetouch\Code\Tiktok\testing\database\tiktokdb.db"

# === CSV files path ===
file_creators = r"C:\Users\USER\Documents\Tunetouch\Code\Tiktok\testing\24092025\2\trending_tiktok_creators.csv"
file_posts = r"C:\Users\USER\Documents\Tunetouch\Code\Tiktok\testing\24092025\2\trending_tiktok_posts.csv"
file_hashtags = r"C:\Users\USER\Documents\Tunetouch\Code\Tiktok\testing\24092025\2\trending_tiktok_hashtags.csv"

# === Connect to SQLite ===
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# === Load CSVs ===
df_creators = pd.read_csv(file_creators)
df_posts = pd.read_csv(file_posts)
df_hashtags = pd.read_csv(file_hashtags)

# === Insert creators ===
for _, row in df_creators.iterrows():
    try:
        cursor.execute("""
        INSERT OR IGNORE INTO creators (
            nickname, uniqueId, user_id, follower_count, bio,
            creator_rank, video_type, video_item_id, video_name, video_url,
            profile_url, video_play_count, video_like_count, video_rank,
            crawl_date, crawl_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row.get("nickname"),
            row.get("uniqueId"),
            row.get("user_id"),
            row.get("follower_count"),
            row.get("bio"),
            row.get("creator_rank"),
            row.get("video_type"),
            row.get("video_item_id"),
            row.get("video_name"),
            row.get("video_url"),
            row.get("profile_url"),
            row.get("video_play_count"),
            row.get("video_like_count"),
            row.get("video_rank"),
            row.get("crawl_date"),
            row.get("crawl_time"),
        ))
    except Exception as e:
        print("Creators insert error:", e, row.to_dict())

# === Insert posts ===
for _, row in df_posts.iterrows():
    try:
        cursor.execute("""
        INSERT OR IGNORE INTO posts (
            url, nickname, user_id, item_id, item_name, genre,
            like_count, play_count, crawl_date, crawl_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row.get("url"),
            row.get("nickname"),
            row.get("user_id"),
            row.get("item_id"),
            row.get("item_name"),
            row.get("genre"),
            row.get("like_count"),
            row.get("play_count"),
            row.get("crawl_date"),
            row.get("crawl_time"),
        ))
    except Exception as e:
        print("Posts insert error:", e, row.to_dict())

# === Insert hashtags ===
for _, row in df_hashtags.iterrows():
    try:
        cursor.execute("""
        INSERT OR IGNORE INTO hashtags (
            hashtag_id, hashtag_name, country, rank, video_views,
            publish_count, industry_value, crawl_date, crawl_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row.get("hashtag_id"),
            row.get("hashtag_name"),
            row.get("country"),
            row.get("rank"),
            row.get("video_views"),
            row.get("publish_count"),
            row.get("industry_value"),
            row.get("crawl_date"),
            row.get("crawl_time"),
        ))
    except Exception as e:
        print("Hashtags insert error:", e, row.to_dict())

# === Commit and close ===
conn.commit()
conn.close()
print("CSV data inserted successfully into database.")
