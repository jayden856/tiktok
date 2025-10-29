# TikTok Trending Data Scraper

## 📋 Overview

This script automatically scrapes TikTok trending data, including:
- **Trending Videos**: Hot videos across different categories
- **Trending Creators**: Popular creators and their video information
- **Trending Hashtags**: Trending hashtag data

All data is saved to both CSV files and SQLite database.

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install requests pandas
```

### 2. Run the Script

```bash
python script.py
```

---

## ⚙️ Configuration

### Modify Scraping Parameters

In the `main()` function of `script.py`, you can modify these parameters:

```python
def main():
    target_page = 10  # Number of pages to scrape per category (10 items per page)
    
    # CSV output filenames
    file_videos = "trending_tiktok_posts.csv"
    file_creators = "trending_tiktok_creators.csv"
    file_hashtags = "trending_tiktok_hashtags.csv"
    
    # Database path
    db_path = r"C:\Users\USER\Documents\Tunetouch\Code\Tiktok\testing\database\tiktokdb.db"
```

### Available Video Categories (Verticals)

- Entertainment
- Beauty_Style
- Performance
- Sport & Outdoor
- Society
- Lifestyle
- Auto_Vehicle
- Talents
- Nature
- Culture_Education_Technology
- Supernatural_Horror

---

## 🔑 **IMPORTANT: Updating Hashtag API Credentials**

### ⚠️ Why Manual Update is Required?

TikTok's hashtag API requires valid authentication information (Cookie, CSRF Token, etc.) that expires regularly. Manual updates are necessary to continue scraping hashtag data.

### 📝 Detailed Update Steps

#### Step 1: Open TikTok Creative Center

1. Open your browser and visit:
   ```
   https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en
   ```

2. **Make sure you are logged in** to your TikTok Ads account

#### Step 2: Open Developer Tools

1. Press `F12` to open browser developer tools
2. Click on the **Network** tab

#### Step 3: Capture the API Request

1. In the Network tab, ensure network activity is being recorded (red record button should be active)
2. Refresh the page (press `F5` or `Ctrl+R`)
3. In the Network panel's **Filter** box, type:
   ```
   list?page
   ```
4. You should see a request like `hashtag/list?page=1&limit=20...`

#### Step 4: Copy cURL

1. Find and click on the `hashtag/list?page=...` request
2. Right-click on the request
3. Select **Copy** > **Copy as cURL (cmd)** or **Copy as cURL (bash)**

   Different browsers:
   - **Chrome**: Copy > Copy as cURL (cmd)
   - **Edge**: Copy > Copy as cURL (cmd)
   - **Firefox**: Copy > Copy as cURL

#### Step 5: Extract Information Using Postman

1. Open [https://www.postman.com/](https://www.postman.com/)
2. If you don't have an account, use the web version (click "Try Postman Web")
3. In Postman:
   - Click **Import** in the top left
   - Select **Raw text**
   - Paste the cURL command you just copied
   - Click **Continue** then **Import**

4. After importing, click the **Headers** tab to see all request header information

#### Step 6: Update script.py

In `script.py`, find the `call_tiktok_trending_hashtags()` function (around line 173) and update the following information:

##### Fields to Update:

1. **Cookie (MOST IMPORTANT)**
   ```python
   "Cookie": "Your complete Cookie value copied from Postman"
   ```

2. **x-csrftoken**
   ```python
   "x-csrftoken": "Value found in Postman Headers"
   ```

3. **web-id**
   ```python
   "web-id": "Value found in Postman Headers"
   ```

4. **anonymous-user-id**
   ```python
   "anonymous-user-id": "Value found in Postman Headers"
   ```

5. **timestamp** (optional but recommended)
   ```python
   "timestamp": "Current timestamp"
   ```

6. **user-sign** (optional)
   ```python
   "user-sign": "Value found in Postman Headers"
   ```

##### Complete Example:

```python
headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
    "anonymous-user-id": "your-new-value",  # UPDATE THIS
    "lang": "en",
    "priority": "u=1, i",
    "referer": "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pad/en",
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "timestamp": "your-new-value",  # UPDATE THIS
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "user-sign": "your-new-value",  # UPDATE THIS
    "web-id": "your-new-value",  # UPDATE THIS
    "x-csrftoken": "your-new-value",  # UPDATE THIS
    "Cookie": "your-complete-cookie-string"  # MOST IMPORTANT! MUST UPDATE
}
```

#### Step 7: Test the Update

1. Save `script.py`
2. Run the script to test if hashtag scraping works:
   ```bash
   python script.py
   ```
3. Check console output, you should see "Trending Hashtags Page X success" messages

### 🔄 Update Frequency

Update credentials when you encounter:
- Script errors like 403 Forbidden or 401 Unauthorized
- Unable to scrape hashtag data
- More than 24 hours since last update

---

## 📊 Output Data

### CSV Files

The script generates three CSV files in the current directory:

1. **trending_tiktok_posts.csv** - Trending videos data
   - url, nickname, user_id, item_id, item_name, genre
   - like_count, play_count, crawl_date, crawl_time

2. **trending_tiktok_creators.csv** - Trending creators data
   - nickname, uniqueId, user_id, follower_count, bio, creator_rank
   - video_type, video_item_id, video_name, video_url, profile_url
   - video_play_count, video_like_count, video_rank, crawl_date, crawl_time

3. **trending_tiktok_hashtags.csv** - Trending hashtags data
   - hashtag_id, hashtag_name, country, rank
   - video_views, publish_count, industry_value
   - crawl_date, crawl_time

### SQLite Database

Data is simultaneously saved to SQLite database in three tables:
- `posts` - Video data
- `creators` - Creator data
- `hashtags` - Hashtag data

The database uses `INSERT OR IGNORE` strategy to avoid duplicate data.

---

## 🛠️ Function Documentation

### call_tiktok_trending_api(genre, page_num)
Scrapes trending videos for a specific category
- **Parameters**:
  - `genre`: Video category (e.g., "Entertainment")
  - `page_num`: Page number (starts from 0)
- **Returns**: List of video data

### call_tiktok_trending_creators(vertical, page_num)
Scrapes trending creators for a specific category
- **Parameters**:
  - `vertical`: Creator category
  - `page_num`: Page number (starts from 0)
- **Returns**: List of creator and their video data

### call_tiktok_trending_hashtags(page_num, limit=20, period=7, country="MY")
Scrapes trending hashtags (requires valid credentials)
- **Parameters**:
  - `page_num`: Page number (starts from 0)
  - `limit`: Items per page (default 20)
  - `period`: Time range in days (default 7 days)
  - `country`: Country code (default "MY" for Malaysia)
- **Returns**: List of hashtag data

### save_to_sqlite(db_path, table_name, data, columns)
Saves data to SQLite database
- **Parameters**:
  - `db_path`: Database file path
  - `table_name`: Table name
  - `data`: List of data to save
  - `columns`: List of column names

---

## ⚡ Performance Optimization

- 0.5 second delay after each API call to avoid rate limiting
- Uses `INSERT OR IGNORE` to prevent duplicate data
- Default scrapes 10 pages per category (100 items total)

---

## 🐛 Troubleshooting

### Q1: Hashtag scraping fails with 403 error
**A**: Cookie has expired. Follow the "Updating Hashtag API Credentials" steps above to get new credentials.

### Q2: Video or creator scraping fails
**A**: Check network connection, or TikTok API may be temporarily unavailable. Try again later.

### Q3: How to change country/region for scraping?
**A**: Modify the `country` parameter when calling `call_tiktok_trending_hashtags()`:
```python
call_tiktok_trending_hashtags(page_num, limit=20, period=7, country="US")
```

### Q4: What about duplicate data in database?
**A**: The script uses `INSERT OR IGNORE`, which automatically skips duplicate data (based on primary key).

---

## 📝 Important Notes

1. ⚠️ **Follow TikTok Terms of Service**: Use responsibly, avoid excessive requests
2. 🔐 **Protect Your Credentials**: Don't upload code with Cookie to public repositories
3. 📊 **Data Freshness**: TikTok trending data changes in real-time, run script regularly
4. 💾 **Backup Data**: Backup important data regularly

---

## 📞 Technical Support

If you encounter issues, check:
1. Python version >= 3.7
2. Dependencies installed correctly
3. Network connection is working
4. Cookie credentials are valid (for hashtags)

---

## 📄 License

This project is for educational and research purposes only.

---

**Last Updated**: October 29, 2025
