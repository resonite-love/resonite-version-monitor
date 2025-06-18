#!/usr/bin/env python3
import json
import requests
import sys
from pathlib import Path
from datetime import datetime

def fetch_steam_news(appid=2519830, count=10):
    """Fetch Steam news for the specified app ID."""
    url = f"https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/"
    params = {
        'appid': appid,
        'count': count,
        'feeds': 'steam_community_announcements'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Steam news: {e}")
        return None

def fetch_all_steam_news(appid=2519830):
    """Fetch all historical Steam news for the specified app ID."""
    print("Fetching all historical Steam news...")
    all_items = []
    seen_gids = set()
    
    # Start with a large batch to get as many as possible
    # Steam API typically returns up to 100 items per request
    batch_size = 100
    total_fetched = 0
    
    # Keep fetching until we don't get any new items
    max_attempts = 10  # Safety limit to prevent infinite loops
    attempt = 0
    
    while attempt < max_attempts:
        print(f"Fetching batch {attempt + 1} (requesting {batch_size} items)...")
        
        news_data = fetch_steam_news(appid, batch_size)
        if not news_data or 'appnews' not in news_data:
            print("No more data available")
            break
        
        newsitems = news_data['appnews'].get('newsitems', [])
        if not newsitems:
            print("No news items in response")
            break
        
        # Add new items only
        new_items = []
        for item in newsitems:
            gid = item.get('gid')
            if gid and gid not in seen_gids:
                new_items.append(item)
                seen_gids.add(gid)
        
        if not new_items:
            print("No new items found, stopping...")
            break
        
        all_items.extend(new_items)
        total_fetched += len(new_items)
        print(f"Added {len(new_items)} new items (total: {total_fetched})")
        
        # If we got fewer items than requested, we've probably reached the end
        if len(newsitems) < batch_size:
            print("Received fewer items than requested, likely reached the end")
            break
        
        attempt += 1
        
        # Small delay to be respectful to the API
        import time
        time.sleep(0.5)
    
    print(f"Finished fetching historical news. Total items: {total_fetched}")
    
    # Create a response structure similar to the regular API response
    return {
        'appnews': {
            'appid': appid,
            'newsitems': all_items,
            'count': len(all_items)
        }
    }

def process_news_data(news_data):
    """Process the raw news data into a cleaner format."""
    if not news_data or 'appnews' not in news_data:
        return None
    
    appnews = news_data['appnews']
    newsitems = appnews.get('newsitems', [])
    
    processed_items = []
    for item in newsitems:
        processed_item = {
            'gid': item.get('gid'),
            'title': item.get('title'),
            'url': item.get('url'),
            'is_external_url': item.get('is_external_url', False),
            'author': item.get('author'),
            'contents': item.get('contents'),
            'feedlabel': item.get('feedlabel'),
            'date': item.get('date'),
            'feedname': 'steam_community_announcements',
            'feed_type': item.get('feed_type'),
            'appid': item.get('appid'),
            # Add human-readable timestamp
            'date_formatted': datetime.fromtimestamp(item.get('date', 0)).isoformat() + 'Z' if item.get('date') else None
        }
        processed_items.append(processed_item)
    
    return {
        'appid': appnews.get('appid'),
        'count': appnews.get('count'),
        'newsitems': processed_items,
        'last_updated': datetime.utcnow().isoformat() + 'Z'
    }

def update_news_json(news_data):
    """Update the news JSON file with new data."""
    news_file = Path(__file__).parent.parent / 'data' / 'steam_news.json'
    
    # Check if this is the first run (empty or non-existent file)
    is_first_run = False
    existing_data = {'newsitems': [], 'last_updated': None}
    
    if news_file.exists():
        try:
            with open(news_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            # Check if this is effectively a first run (empty or no news items)
            if not existing_data.get('newsitems') or existing_data.get('last_updated') is None:
                is_first_run = True
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading existing news file: {e}")
            is_first_run = True
    else:
        is_first_run = True
    
    if not news_data:
        print("No news data to process")
        return False
    
    if is_first_run:
        # First run: fetch and save all historical news items
        print("First run detected - fetching all historical news items")
        
        # Fetch all historical news instead of just the recent ones
        all_news_data = fetch_all_steam_news()
        if not all_news_data:
            print("Failed to fetch historical news data")
            return False
        
        # Process all historical data
        processed_historical = process_news_data(all_news_data)
        if not processed_historical:
            print("Failed to process historical news data")
            return False
        
        updated_data = {
            'appid': processed_historical['appid'],
            'count': len(processed_historical['newsitems']),
            'newsitems': processed_historical['newsitems'],
            'last_updated': processed_historical['last_updated']
        }
        
        # Save to file
        with open(news_file, 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(processed_historical['newsitems'])} historical news items on first run")
        return True
    else:
        # Subsequent runs: only add new items
        # Get existing GIDs to avoid duplicates
        existing_gids = set()
        if 'newsitems' in existing_data:
            existing_gids = {item.get('gid') for item in existing_data['newsitems'] if item.get('gid')}
        
        # Add new items
        new_items = []
        for item in news_data['newsitems']:
            if item.get('gid') not in existing_gids:
                new_items.append(item)
        
        if new_items:
            # Combine existing and new items, sort by date descending
            all_items = existing_data.get('newsitems', []) + new_items
            all_items.sort(key=lambda x: x.get('date', 0), reverse=True)
            
            # Update the data structure
            updated_data = {
                'appid': news_data['appid'],
                'count': len(all_items),
                'newsitems': all_items,
                'last_updated': news_data['last_updated']
            }
            
            # Save to file
            with open(news_file, 'w', encoding='utf-8') as f:
                json.dump(updated_data, f, indent=2, ensure_ascii=False)
            
            print(f"Added {len(new_items)} new news items")
            return True
        else:
            # Update last_updated timestamp even if no new items
            existing_data['last_updated'] = news_data['last_updated']
            with open(news_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
            
            print("No new news items to add")
            return False

def main():
    """Main function to fetch and update Steam news."""
    print("Fetching Steam news for Resonite...")
    
    # Fetch news data
    raw_news = fetch_steam_news()
    if not raw_news:
        print("Failed to fetch Steam news")
        sys.exit(1)
    
    # Process the data
    processed_news = process_news_data(raw_news)
    if not processed_news:
        print("Failed to process news data")
        sys.exit(1)
    
    # Update the JSON file
    has_updates = update_news_json(processed_news)
    
    if has_updates:
        print("Successfully updated steam_news.json with new items")
        sys.exit(0)  # Exit with success code for GitHub Actions
    else:
        print("No new updates found")
        sys.exit(1)  # Exit with non-zero code to indicate no changes

if __name__ == '__main__':
    main()