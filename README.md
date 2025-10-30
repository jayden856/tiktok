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

## 🌐 Streamlit Dashboard Visualization

This project includes interactive dashboards built with Streamlit to visualize the scraped TikTok data.

### Dashboard Features

The dashboard consists of three main sections accessible via tabs:

1. **Creators Dashboard** (`streamlit_creators.py`)
   - Overall metrics and KPIs for trending creators
   - Top 20 creators by followers
   - Top 20 videos by play count
   - Filter videos by category
   - Full data table with advanced filters

2. **Posts Dashboard** (`streamlit_posts.py`)
   - Overall video metrics (total plays, likes, engagement rate)
   - Average metrics by genre with charts
   - Engagement rate analysis
   - Top videos and creators combined ranking
   - Correlation scatter plots
   - Interactive filters

3. **Hashtags Dashboard** (`streamlit_hashtags.py`)
   - Overall hashtag metrics
   - Top 20 hashtags by views
   - Top 20 hashtags by post count
   - Filter by industry
   - Full dataset display

### Running Locally

To run the dashboard on your local machine:

1. Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

2. Run the Streamlit app:
```bash
streamlit run app.py
```

3. Open your browser to `http://localhost:8501`

### 🚀 Deploy to Streamlit Share (Cloud Hosting)

Share your dashboard publicly using Streamlit Share - it's **FREE**!

#### Prerequisites

1. A GitHub account
2. Your code pushed to a GitHub repository
3. A Streamlit Share account (free, sign up with GitHub)

#### Step-by-Step Deployment Guide

##### Step 1: Prepare Your Repository

1. **Ensure these files are in your repository:**
   - `app.py` (main application file)
   - `streamlit_creators.py`
   - `streamlit_posts.py`
   - `streamlit_hashtags.py`
   - `requirements.txt` (dependencies list)
   - `database/tiktokdb.db` (your SQLite database)
   - `image/tiktok.png` (app icon)

2. **Update database path in Streamlit files:**

   Since Streamlit Share runs on Linux, you need to update the database path in all three Streamlit files to use a relative path:

   **In `streamlit_creators.py`, `streamlit_posts.py`, and `streamlit_hashtags.py`:**
   
   Change:
   ```python
   db_path = r"C:\Users\USER\Documents\Tunetouch\Code\Tiktok\testing\database\tiktokdb.db"
   ```
   
   To:
   ```python
   import os
   db_path = os.path.join(os.path.dirname(__file__), "database", "tiktokdb.db")
   ```

3. **Commit and push to GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for Streamlit Share deployment"
   git push origin main
   ```

##### Step 2: Deploy on Streamlit Share

1. **Go to** [https://share.streamlit.io/](https://share.streamlit.io/)

2. **Sign in** with your GitHub account

3. **Click "New app"** button

4. **Fill in the deployment form:**
   - **Repository**: Select your GitHub repository (e.g., `username/tiktok-testing`)
   - **Branch**: `main` (or your default branch)
   - **Main file path**: `app.py`
   - **App URL** (optional): Choose a custom subdomain

5. **Click "Deploy!"**

6. **Wait for deployment** (usually takes 2-5 minutes)
   - Streamlit Share will:
     - Clone your repository
     - Install dependencies from `requirements.txt`
     - Launch your app

7. **Access your app!** 
   - Your app URL will be something like: `https://your-app-name.streamlit.app`
   - Share this link with anyone!

##### Step 3: Update Your App

Whenever you push changes to your GitHub repository:

```bash
git add .
git commit -m "Update dashboard"
git push origin main
```

Streamlit Share will **automatically redeploy** your app with the latest changes!

#### Important Notes for Deployment

⚠️ **Database Considerations:**
- Streamlit Share apps are **read-only** for the file system
- You can include your SQLite database in the repository, but it won't be updated when you run the scraper
- For production use, consider:
  - **Option 1**: Manually run scraper locally, commit updated database, and push to GitHub
  - **Option 2**: Use a cloud database (PostgreSQL, MySQL, etc.) instead of SQLite
  - **Option 3**: Use Streamlit's secrets management for database connection strings

⚠️ **File Size Limits:**
- GitHub repositories have file size limits (100 MB per file)
- If your database is too large, consider using Git LFS or a cloud database

⚠️ **Privacy:**
- Public repositories = public app (anyone can access)
- Private repositories = you control access (requires Streamlit Teams plan for private apps)

#### Managing Secrets (Optional)

If you need to store sensitive information (API keys, database credentials):

1. **In Streamlit Share dashboard**, click on your app
2. Go to **Settings** > **Secrets**
3. Add your secrets in TOML format:
   ```toml
   [database]
   connection_string = "your-database-url"
   
   [api]
   tiktok_api_key = "your-api-key"
   ```

4. **Access secrets in your code:**
   ```python
   import streamlit as st
   
   db_connection = st.secrets["database"]["connection_string"]
   api_key = st.secrets["api"]["tiktok_api_key"]
   ```

#### Troubleshooting Deployment

**Problem: App won't start**
- Check the logs in Streamlit Share dashboard
- Verify `requirements.txt` has all necessary packages
- Ensure file paths are relative, not absolute

**Problem: Database not found**
- Verify `database/tiktokdb.db` is committed to repository
- Check file paths use forward slashes `/` or `os.path.join()`

**Problem: Missing dependencies**
- Add all required packages to `requirements.txt`
- Include version numbers for stability

**Problem: App runs locally but not on Streamlit Share**
- Check for Windows-specific code (use `os.path` instead of hardcoded paths)
- Verify all imports are available in `requirements.txt`

### 📊 Updating Dashboard Data

To keep your dashboard data fresh:

1. **Run the scraper** locally:
   ```bash
   python script.py
   ```

2. **Commit the updated database**:
   ```bash
   git add database/tiktokdb.db
   git commit -m "Update TikTok data - $(date +%Y-%m-%d)"
   git push origin main
   ```

3. **Streamlit Share automatically redeploys** with new data!

---

## 📄 License

This project is for educational and research purposes only.

---

**Last Updated**: October 29, 2025
