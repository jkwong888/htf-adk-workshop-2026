import os
import sys
import json
import argparse
import asyncio
import sqlite3
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import dateutil.parser
from apify_client import ApifyClient
from google.adk import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types
from google.adk.plugins import ReflectAndRetryToolPlugin


# Import the root_agent from agent.py
from agent import root_agent

# Load environment variables
load_dotenv()

APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN", "")

def get_apify_subreddit_timeframe(minutes):
    """Map minutes to the closest Apify subredditTimeframe enum."""
    if minutes is None:
        return None
    if minutes <= 60:
        return "hour"
    elif minutes <= 1440:
        return "day"
    elif minutes <= 10080:
        return "week"
    elif minutes <= 43200:
        return "month"
    elif minutes <= 525600:
        return "year"
    return "all"

def init_db(db_path="reddit_events.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reddit_posts (
            url TEXT PRIMARY KEY,
            subreddit TEXT,
            title TEXT,
            time_posted TEXT,
            num_comments INTEGER,
            processed BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def upsert_posts(posts, db_path="reddit_events.db"):
    print(f"Upserting {len(posts)} posts to database...")
    if not posts:
        return
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for post in posts:
        cursor.execute('''
            INSERT INTO reddit_posts (url, subreddit, title, time_posted, num_comments, processed)
            VALUES (?, ?, ?, ?, ?, 0)
            ON CONFLICT(url) DO UPDATE SET
                subreddit=excluded.subreddit,
                title=excluded.title,
                time_posted=excluded.time_posted,
                num_comments=excluded.num_comments
        ''', (post['url'], post['subreddit'], post['title'], post['time_posted'], post['num_comments']))
    conn.commit()
    conn.close()

def get_posts_to_process(subreddit, minutes_ago=None, reprocess=False, db_path="reddit_events.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    query = """
    SELECT 
        url, 
        subreddit, 
        title, 
        time_posted, 
        num_comments, 
        processed 
    FROM reddit_posts 
    WHERE subreddit = ?
    """
    params = [subreddit]
    
    if not reprocess:
        query += " AND processed = 0"

    print(f"Querying database for {subreddit} posts from the last {minutes_ago} minutes, query={query}, params={params}")
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    posts = []
    cutoff_time = None
    if minutes_ago is not None:
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)
        
    for row in rows:
        post_time = dateutil.parser.isoparse(row[3])
        if post_time.tzinfo is None:
            post_time = post_time.replace(tzinfo=timezone.utc)
            
        if cutoff_time and post_time < cutoff_time:
            continue
            
        posts.append({
            "url": row[0],
            "subreddit": row[1],
            "title": row[2],
            "time_posted": row[3],
            "num_comments": row[4]
        })
        
    conn.close()
    return posts

def mark_post_processed(url, db_path="reddit_events.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE reddit_posts SET processed = 1 WHERE url = ?", (url,))
    conn.commit()
    conn.close()

def fetch_posts_from_apify(subreddit, minutes_ago=None):
    if not APIFY_API_TOKEN:
        print("Error: APIFY_API_TOKEN is not set.")
        sys.exit(1)

    # Calculate cutoff time if minutes_ago is provided
    cutoff_time = None
    subreddit_timeframe = None
    if minutes_ago is not None:
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)
        subreddit_timeframe = get_apify_subreddit_timeframe(minutes_ago)

    client = ApifyClient(APIFY_API_TOKEN)
    actor_id = "fatihtahta/reddit-scraper-search-fast"
    
    # Prepare Actor input based on the provided OpenAPI schema
    run_input = {
        "subredditName": subreddit,
        "subredditSort": "new",
        "maxPosts": 100 if cutoff_time else 10,
        "scrapeComments": False
    }

    # Add subredditTimeframe if specified to optimize the actor search
    if subreddit_timeframe:
        run_input["subredditTimeframe"] = subreddit_timeframe
    else:
         run_input["subredditTimeframe"] = "all"
    
    try:
        # Run the Actor and wait for it to finish
        print(f"Running Apify actor {actor_id}...")
        run = client.actor(actor_id).call(run_input=run_input)
        
        # Fetch Actor results from the run's dataset
        dataset_items = client.dataset(run["defaultDatasetId"]).iterate_items()
        
        posts = []
        for item in dataset_items:
            # The exact keys depend on the actor, usually createdAt or parsedTime
            time_posted_str = item.get("createdAt") or item.get("parsedTime")
            if time_posted_str:
                # Ensure it has timezone info for comparison
                post_time = dateutil.parser.isoparse(time_posted_str)
                if post_time.tzinfo is None:
                    post_time = post_time.replace(tzinfo=timezone.utc)
            else:
                post_time = datetime.now(timezone.utc)
                
            # Filter exactly to the minute
            if cutoff_time and post_time < cutoff_time:
                continue
                
            posts.append({
                "title": item.get("title", "No Title"),
                "subreddit": item.get("subreddit", subreddit),
                "url": item.get("url", ""),
                "time_posted": post_time.isoformat(),
                "num_comments": item.get("numberOfComments", item.get("numComments", 0))
            })
            
        return posts
        
    except Exception as e:
        print(f"Error fetching from Apify: {e}")
        sys.exit(1)

async def trigger_adk_agent(runner: Runner, event_payload: dict, session_id: str = "reddit_monitor_session"):


    # instruction = """

    # """
    

    new_message = types.Content(role="user", parts=[types.Part.from_text(text=json.dumps(event_payload, indent=2))])
    
    print(f"Triggering ADK Agent workflow (session: {session_id})...")
    
    # Run the agent directly within the script
    async for event in runner.run_async(
        user_id="cli_user", 
        session_id=session_id, 
        new_message=new_message):
        if hasattr(event, 'content') and event.content:
            if hasattr(event.content, 'parts') and event.content.parts:
                 for part in event.content.parts:
                     if hasattr(part, 'text') and part.text:
                         print(f"Agent: {part.text}")
                     if hasattr(part, 'function_call') and part.function_call:
                         print(f"Agent Tool Call: {part.function_call.name}({part.function_call.args})")
        elif hasattr(event, 'tool_call') and event.tool_call:
             print(f"Agent Tool Call: {event.tool_call.name}")
        elif hasattr(event, 'error_message') and event.error_message:
             print(f"Agent Error: {event.error_message}")

async def main():
    parser = argparse.ArgumentParser(description="Reddit Monitor Script using Apify")
    parser.add_argument("--subreddit", help="Subreddit to monitor (e.g. 'python')", default="LocalLLaMA")
    parser.add_argument("--minutes-ago", type=int, help="Optional: Number of minutes ago to fetch posts since (e.g., 5)", default=60)
    parser.add_argument("--replay", action="store_true", help="Replay posts from the local database instead of scraping")
    parser.add_argument("--reprocess", action="store_true", help="Process posts even if they already exist in the database")
    args = parser.parse_args()
    
    init_db()

    runner = Runner(
        app_name="reddit_monitor",
        agent=root_agent,
        session_service=InMemorySessionService(),
        auto_create_session=True,
        plugins=[
            ReflectAndRetryToolPlugin(max_retries=3)
        ]
    )

    
    print(f"Monitoring subreddit: r/{args.subreddit}")
    if args.minutes_ago is not None:
        print(f"Fetching posts since {args.minutes_ago} minutes ago.")
    else:
        print("Fetching the latest post.")
        
    if not args.replay:
        posts = fetch_posts_from_apify(args.subreddit, args.minutes_ago)
        print(f"Fetched {len(posts)} posts from Apify.")
        upsert_posts(posts)
        
    posts_to_process = get_posts_to_process(args.subreddit, args.minutes_ago, args.reprocess)
    
    if posts_to_process:
        print(f"Found {len(posts_to_process)} posts to process.")
        import hashlib
        for post in posts_to_process:
            event_payload = {"event_type": "reddit_monitor_update", "posts": [post]}
            print("\nGenerated Event Payload for single post:")
            print(json.dumps(event_payload, indent=2))
            
            # Use unique session_id per post to avoid memory accumulation across independent posts
            url_hash = hashlib.md5(post['url'].encode('utf-8')).hexdigest()
            session_id = f"reddit_monitor_session_{url_hash}"
            
            await trigger_adk_agent(runner, event_payload, session_id=session_id)
            mark_post_processed(post['url'])
    else:
        print("No new posts found in the specified timeframe. Skipping agent trigger.")

if __name__ == "__main__":
    asyncio.run(main())
