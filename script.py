import requests
import json
from datetime import datetime
import pandas as pd
import csv
import time
import sqlite3

# === TikTok Vertical Categories & Regions ===
vertical = [
    "Entertainment", "Beauty_Style", "Performance", "Sport & Outdoor",
    "Society", "Lifestyle", "Auto_Vehicle", "Talents", "Nature",
    "Culture_Education_Technology", "Supernatural_Horror"
]
region = ["US","JP","UK","DE","MX","CA","FR","KR","ID","BZ","PL","AU","IT","ES"]

# === API Calls ===
def call_tiktok_trending_api(genre, page_num):
    """
    Call TikTok Creator Studio trending videos API
    """
    url = "https://www.tiktok.com/creator_studio/inspiration/trending/video/v2"
    
    params = {
        "locale": "en",
        "aid": "1988",
        "priority_region": "MY",
        "region": "MY",
        "tz_name": "Asia/Kuala_Lumpur",
        "app_name": "tiktok_creator_center",
        "app_language": "en",
        "device_platform": "web_pc",
        "channel": "tiktok_web",
        "device_id": "7537224491294852615",
        "os": "win",
        "screen_width": "1920",
        "screen_height": "1080",
        "browser_language": "en-US",
        "browser_platform": "Win32",
        "browser_name": "Mozilla",
        "browser_version": "5.0+(Windows+NT+10.0;+Win64;+x64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/140.0.0.0+Safari/537.36",
        "key": "trendingListAllEntertainment",
        "PageNum": str(page_num),
        "PageSize": "10",
        "Region": "All",
        "Vertical": genre,
        "op_region": "MY",
        "TrendingType": "0"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Referer": "https://www.tiktok.com/creator_studio/",
        "Origin": "https://www.tiktok.com",
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        if response.status_code == 200:
            print(f"Trending Videos [{genre}] Page {page_num+1} success")
            data = response.json()
            result = [
                {
                    "url": f"https://tiktok.com/@username/video/{video['ItemId']}",
                    "nickname": video["Author"]["NickName"],
                    "user_id": video["Author"]["UserId"],
                    "item_id": video["ItemId"],
                    "item_name": video["ItemName"],
                    "genre": genre,
                    "like_count": video["LikeCount"],
                    "play_count": video["PlayCount"],
                }
                for video in data.get("TrendingVideos", [])
            ]
            return result
        else:
            print(f"Trending Videos [{genre}] Page {page_num+1} failed! Status Code: {response.status_code}")
            print(response.text[:300])
            return None
    except Exception as e:
        print(f"Error fetching Trending Videos: {e}")
        return None


def call_tiktok_trending_creators(vertical, page_num):
    """
    Call TikTok Creator Studio trending creators API with vertical
    """
    url = "https://www.tiktok.com/creator_studio/inspiration/trending/creator/v2"
    
    params = {
        "locale": "en",
        "aid": "1988",
        "priority_region": "MY",
        "region": "MY",
        "tz_name": "Asia/Kuala_Lumpur",
        "app_name": "tiktok_creator_center",
        "app_language": "en",
        "device_platform": "web_pc",
        "channel": "tiktok_web",
        "device_id": "7537224491294852615",
        "os": "win",
        "screen_width": "1920",
        "screen_height": "1080",
        "browser_language": "en-US",
        "browser_platform": "Win32",
        "browser_name": "Mozilla",
        "browser_version": "5.0+(Windows+NT+10.0;+Win64;+x64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/140.0.0.0+Safari/537.36",
        "key": "trendingCreators",
        "PageNum": str(page_num),
        "PageSize": "10",
        "Region": "All",
        "Vertical": vertical,
        "op_region": "MY",
        "TrendingType": "0"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Referer": "https://www.tiktok.com/creator_studio/",
        "Origin": "https://www.tiktok.com",
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        if response.status_code == 200:
            print(f"Trending Creators [{vertical}] Page {page_num+1} success")
            data = response.json()
            creators = []
            for idx, creator in enumerate(data.get("TrendingCreators", [])):
                creator_rank = page_num * 10 + (idx + 1)
                base_info = {
                    "nickname": creator.get("NickName"),
                    "uniqueId": creator.get("UniqueId"),
                    "user_id": creator.get("UserId"),
                    "follower_count": creator.get("FollowerCount"),
                    "bio": creator.get("BioDescription"),
                    "creator_rank": creator_rank
                }
                videos_sorted = sorted(
                    creator.get("ProfileVideoList", []),
                    key=lambda v: (v.get("PlayCount", 0) + v.get("LikeCount", 0)),
                    reverse=True
                )
                for video_rank, video in enumerate(videos_sorted, start=1):
                    creators.append({
                        **base_info,
                        "video_type": vertical,
                        "video_item_id": video.get("ItemId"),
                        "video_name": video.get("ItemName"),
                        "video_url": f"https://www.tiktok.com/@{creator.get('UniqueId','')}/video/{video.get('ItemId')}",
                        "profile_url": f"https://www.tiktok.com/@{creator.get('UniqueId','')}",
                        "video_play_count": video.get("PlayCount"),
                        "video_like_count": video.get("LikeCount"),
                        "video_rank": video_rank
                    })
            return creators
        else:
            print(f"Trending Creators [{vertical}] Page {page_num+1} failed! Status Code: {response.status_code}")
            print(response.text[:300])
            return None
    except Exception as e:
        print(f"Error fetching Trending Creators [{vertical}] Page {page_num+1}: {e}")
        return None


def call_tiktok_trending_hashtags(page_num, limit=20, period=7, country="MY"):
    """
    Call TikTok Ads Creative Radar API for trending hashtags
    """
    url = "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/hashtag/list"
    
    params = {
        "page": str(page_num),
        "limit": str(limit),
        "period": str(period),
        "country_code": country,
        "sort_by": "popular"
    }
    
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "anonymous-user-id": "a68bfee9-5b14-42ab-a712-a8f5235e5d65",
        "lang": "en",
        "priority": "u=1, i",
        "referer": "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en",
        "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "timestamp": "1761799644",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
        "user-sign": "9797d4d5fc3494ea",
        "web-id": "7551636089719506439",
        "x-csrftoken": "0KaG8PExFULV8Lh7Pqr037oOtO83m6Ls",
        "Cookie": "_ttp=318EgmQiv1gQgNgXgdcaCP9kWfq; tt_chain_token=uANO3xQSmn+rFUIJPjuTbQ==; passport_csrf_token=25258bca59ea942eec61ecea7d18718c; passport_csrf_token_default=25258bca59ea942eec61ecea7d18718c; multi_sids=7549085889809630215%3A92cdc5726a9b4e00e197c04cff45abfb; cmpl_token=AgQQAPO0F-RO0rj9UzkxNp0-8vgAjgOeP4U_YNyC_Q; uid_tt=3c539828c3a827359f6d0a12f91c49e905a9dab7a3b824adea83ea6c63485229; uid_tt_ss=3c539828c3a827359f6d0a12f91c49e905a9dab7a3b824adea83ea6c63485229; sid_tt=92cdc5726a9b4e00e197c04cff45abfb; sessionid=92cdc5726a9b4e00e197c04cff45abfb; sessionid_ss=92cdc5726a9b4e00e197c04cff45abfb; store-idc=alisg; tt-target-idc=alisg; tt-target-idc-sign=i2NRwVy554W7KNR1CohT-NRVGub_fmksAyL_36DS-wGqpWGPWNJC8ZUf3mvuq3ueIHK1iJzPO0HGkYhRAm2fpvEkf_Tk2UkJ6u11LeFBn0i5wSQyU1j0NLfTDp3R1CkcWCwEL95tzlUzAc4Rptn1R4mxEKbKpXK3eB6Fm1qdTXVeGnWDhPHkeKSWpA767vCipladelzrIpC1bqV7APkRIuFZsUJ8winmROxnWPDX4nIMCd4FQrQI-v3NESfnNervgEubPPE5gQ4bcfE5vxalEOl83NB5xvYEnaDL37k3vgnPDerffUniE6weBZJhal8kToQFTAAvaEnQmLlcRWXbtW0JfeWPDqZAzlZI6o29OHohqiHYTvjWVgbpEbUxJYO5JmnrbEhT9CuFGoDcgvAMsYnB94wklMZYxFDG5FIECTO8sJr8QcRy4viT19pl3GS6QJQ8uZU9MIp7UXlkPhVywJTtKTqJz34ZuUhQk0IZpMyFd4stNDrMfivzH1MPAaVL; sid_guard=92cdc5726a9b4e00e197c04cff45abfb%7C1758075458%7C15551972%7CMon%2C+16-Mar-2026+02%3A17%3A10+GMT; sid_ucp_v1=1.0.0-KDk2MzhkYmRmMmFkYWEyOTVjYzY4ODA4ZTYyNGI2YjU0YjQ1ZmI3ZjUKGQiHiJHI67Pv4WgQwrSoxgYYsws4CEASSAQQAxoCbXkiIDkyY2RjNTcyNmE5YjRlMDBlMTk3YzA0Y2ZmNDVhYmZi; ssid_ucp_v1=1.0.0-KDk2MzhkYmRmMmFkYWEyOTVjYzY4ODA4ZTYyNGI2YjU0YjQ1ZmI3ZjUKGQiHiJHI67Pv4WgQwrSoxgYYsws4CEASSAQQAxoCbXkiIDkyY2RjNTcyNmE5YjRlMDBlMTk3YzA0Y2ZmNDVhYmZi; from_way=paid; tta_attr_id_mirror=0.1758190239.7551369577817620498; i18next=en; lang_type=en; pre_country=MY; csrftoken=0KaG8PExFULV8Lh7Pqr037oOtO83m6Ls; passport_auth_status_ads=975ae0fd4a36aa0e546b67c8a8776bc7%2C584eed7cafce7fa98b60cc0ee9fb24df; passport_auth_status_ss_ads=975ae0fd4a36aa0e546b67c8a8776bc7%2C584eed7cafce7fa98b60cc0ee9fb24df; sid_guard_ads=4fff5c3c24bd86a44273c6bdd44b9e7a%7C1759471044%7C259200%7CMon%2C+06-Oct-2025+05%3A57%3A24+GMT; tt_session_tlb_tag=sttt%7C1%7Cks3FcmqbTgDhl8BM_0Wr-__________OvGo7zIt8-h_gkgRfNA5xqVN5qS-FiYPjUsuE6yJPZN4%3D; store-country-code=my; store-country-code-src=uid; store-country-sign=MEIEDM2t0bL9Ev4kPP9FzwQgK3Enhy1V_R88F4BnpuI-YEjcaAYTFZhfPoGeD6xz-0oEEL3WpY5u1_RHvoi-bskx3sk; odin_tt=86dfee71798bc4fa1505cf571fda9a1699adf993a83a42a0c2beabeb770a0613adac9975557d8769f27843170cc9214a020e03f0ad4ce0277f97073b5cb7f794b39ad35b7c5091d4d6b3a274779b33bf; tt_csrf_token=y90YJfJk-21NTtPsil7-YZr_FVBGbRH4hck0; msToken=zEvZNB3U1k2JSzHLQrJhKvJG4fQeIfWPO_IjBJvupxvAyRWaawbXD0x8BQKoAwx6xGySe1kI3gX1CfKG69a6w3t2JuHkUUG988BL0BBolZ6xN2TBXbXhgrVCQyT-eLpeStUMzdEE; msToken=9Ov_yMTdVmBypikMg3d2-JTEWgqiWxmis6blxx_rBUnvqapCqHXSIdoGmoNNnAeDHd0Foo3Bb-Opip095OjT8eCESf_6wmUNf3pVkDUNpC_Sz5csoRJGgC8AoBnVZeQW9JQve8f2WUIjlsXubfn7Vq8=; ttwid=1%7CnL2heIMH0jMb9-A9UDP9jzEMdBvnk8TBPLfA39TpM4E%7C1761799642%7C2fd2af7d431295fbba30b23fb2165d3dd71d93f295827dc782345aa6510d4dd3"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            hashtags = []
            for item in data.get("data", {}).get("list", []):
                hashtags.append({
                    "hashtag_id": item.get("hashtag_id"),
                    "hashtag_name": item.get("hashtag_name"),
                    "country": item.get("country_info", {}).get("value", ""),
                    "rank": item.get("rank"),
                    "video_views": item.get("video_views"),
                    "publish_count": item.get("publish_cnt"),
                    "industry_value": item.get("industry_info", {}).get("value", ""),
                })
            print(f"Trending Hashtags Page {page_num} success")
            return hashtags
        else:
            print(f"Trending Hashtags Page {page_num} failed! Status Code: {response.status_code}")
            print(response.text[:300])
            return None
    except Exception as e:
        print(f"Error fetching Trending Hashtags Page {page_num}: {e}")
        return None

# === Save to SQLite ===
def save_to_sqlite(db_path, table_name, data, columns):
    """
    Save data to SQLite with INSERT OR IGNORE (to avoid duplicate PK errors)
    """
    if not data:
        print(f"No data to save for table {table_name}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    placeholders = ", ".join(["?" for _ in columns])
    column_names = ", ".join(columns)
    insert_sql = f"INSERT OR IGNORE INTO {table_name} ({column_names}) VALUES ({placeholders})"
    
    values = [[row.get(col, None) for col in columns] for row in data]
    cursor.executemany(insert_sql, values)
    
    conn.commit()
    conn.close()
    print(f"Saved {len(values)} records into '{table_name}' (duplicates ignored)")

# === Main Function ===
def main():
    target_page = 10
    file_videos = "trending_tiktok_posts.csv"
    file_creators = "trending_tiktok_creators.csv"
    file_hashtags = "trending_tiktok_hashtags.csv"
    db_path = r"C:\Users\USER\Documents\Tunetouch\Code\Tiktok\testing\database\tiktokdb.db"

    data_videos, data_creators, data_hashtags = [], [], []

    crawl_datetime = datetime.now()
    crawl_date = crawl_datetime.strftime("%Y-%m-%d")
    crawl_time = crawl_datetime.strftime("%H:%M:%S")

    # --- Trending Videos ---
    for genre in vertical:
        for page_num in range(target_page):
            result = call_tiktok_trending_api(genre, page_num)
            if result:
                for r in result:
                    r["crawl_date"] = crawl_date
                    r["crawl_time"] = crawl_time
                data_videos.extend(result)
            time.sleep(0.5)

    df_videos = pd.DataFrame(data_videos)
    df_videos.to_csv(file_videos, index=False, quoting=csv.QUOTE_NONNUMERIC)
    print(f"Saved Trending Videos to {file_videos}")

    save_to_sqlite(db_path, "posts", data_videos, [
        "url", "nickname", "user_id", "item_id", "item_name", "genre",
        "like_count", "play_count", "crawl_date", "crawl_time"
    ])

    # --- Trending Creators ---
    for vertical_cat in vertical:
        for page_num in range(target_page):
            result = call_tiktok_trending_creators(vertical_cat, page_num)
            if result:
                for r in result:
                    r["crawl_date"] = crawl_date
                    r["crawl_time"] = crawl_time
                data_creators.extend(result)
            time.sleep(0.5)

    df_creators = pd.DataFrame(data_creators)
    df_creators.to_csv(file_creators, index=False, quoting=csv.QUOTE_NONNUMERIC)
    print(f"Saved Trending Creators to {file_creators}")

    save_to_sqlite(db_path, "creators", data_creators, [
        "nickname", "uniqueId", "user_id", "follower_count", "bio", "creator_rank",
        "video_type", "video_item_id", "video_name", "video_url", "profile_url",
        "video_play_count", "video_like_count", "video_rank", "crawl_date", "crawl_time"
    ])

    # --- Trending Hashtags ---
    for page_num in range(target_page):
        result = call_tiktok_trending_hashtags(page_num, limit=20, period=7, country="MY")
        if result:
            for r in result:
                r["crawl_date"] = crawl_date
                r["crawl_time"] = crawl_time
            data_hashtags.extend(result)
        time.sleep(0.5)

    df_hashtags = pd.DataFrame(data_hashtags)
    df_hashtags.to_csv(file_hashtags, index=False, quoting=csv.QUOTE_NONNUMERIC)
    print(f"Saved Trending Hashtags to {file_hashtags}")

    save_to_sqlite(db_path, "hashtags", data_hashtags, [
        "hashtag_id", "hashtag_name", "country", "rank", "video_views",
        "publish_count", "industry_value", "crawl_date", "crawl_time"
    ])

if __name__ == "__main__":
    main()
