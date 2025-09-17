import os
import csv
import time
import sys
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, PleaseWaitFewMinutes, ChallengeRequired

"""Set credentials first: INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD as environment variables"""

def setup_client():
    """Initialize and login to Instagram (no session persistence)"""
    cl = Client()
    
    # Configure client settings to avoid detection
    cl.delay_range = [1, 3]  # Random delay between requests
    
    # Optional proxy support (set environment variable INSTAGRAM_PROXY)
    proxy = os.getenv('INSTAGRAM_PROXY')  # Format: http://user:pass@host:port
    if proxy:
        cl.set_proxy(proxy)
        print(f"Using proxy: {proxy}")
    
    # Use environment variables for security
    username = os.getenv('INSTAGRAM_USERNAME', 'your_username_here')
    password = os.getenv('INSTAGRAM_PASSWORD', 'your_password_here')
    
    if username == 'your_username_here' or password == 'your_password_here':
        print("Please set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD environment variables")
        return None
    
    try:
        print("Attempting fresh login (no session persistence)...")
        # Fresh login with more realistic behavior
        time.sleep(2)  # Wait before login attempt
        cl.login(username, password)
        print("Successfully logged in!")
        
        return cl
        
    except (LoginRequired, PleaseWaitFewMinutes, ChallengeRequired) as e:
        print(f"Instagram security measure triggered: {e}")
        print("\n🚫 SECURITY SOLUTIONS:")
        print("1. Wait 24-48 hours before trying again")
        print("2. Log into Instagram manually through browser/app first")
        print("3. Complete any security challenges Instagram shows you")
        print("4. Use a VPN or different IP address")
        return None
        
    except Exception as e:
        error_msg = str(e)
        print(f"Login failed: {error_msg}")
        
        if any(keyword in error_msg.lower() for keyword in ["blacklist", "ip", "blocked", "suspicious"]):
            print("\n🚫 IP BLOCKED SOLUTIONS:")
            print("1. Wait 24-48 hours before trying again")
            print("2. Use a VPN to change your IP address")
            print("3. Try from a different network (mobile hotspot)")
            print("4. Set INSTAGRAM_PROXY environment variable")
            print("5. Try logging in manually through Instagram app/website first")
        
        return None

def get_media_id_from_url(cl, url):
    """Extract media ID from Instagram URL"""
    try:
        media_pk = cl.media_pk_from_url(url)
        return cl.media_id(media_pk)
    except Exception as e:
        print(f"Error extracting media ID from {url}: {e}")
        return None

def scrape_comments(cl, media_id, max_comments=500):
    """Scrape comments from a post"""
    try:
        comments = cl.media_comments(media_id, amount=max_comments)
        
        comment_data = []
        for comment in comments:
            comment_data.append({
                'comment_id': comment.pk,
                'username': comment.user.username,
                'text': comment.text,
                'created_at_utc': comment.created_at_utc,
                'like_count': comment.comment_like_count if hasattr(comment, 'comment_like_count') else 0
            })
        
        print(f"Scraped {len(comment_data)} comments")
        return comment_data
    
    except Exception as e:
        print(f"Error scraping comments for media {media_id}: {e}")
        return []

def save_to_csv(comments, filename='instagram_comments.csv'):
    """Save comments to CSV file in the instagram-scraper folder"""
    if not comments:
        print("No comments to save")
        return
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, filename)
    
    with open(full_path, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['comment_id', 'username', 'text', 'created_at_utc', 'like_count']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(comments)
    
    print(f"Saved {len(comments)} comments to {full_path}")

def main():
    # Check for command line arguments (removing session-related ones)
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python scraper.py")
        print("Environment variables needed:")
        print("  INSTAGRAM_USERNAME - Your Instagram username")
        print("  INSTAGRAM_PASSWORD - Your Instagram password")
        print("  INSTAGRAM_PROXY - Optional proxy (http://user:pass@host:port)")
        return
    
    # Instagram post URLs to scrape
    urls = [
        "https://www.instagram.com/abscbnnews/p/DOVhI21CW1m/",
        "https://www.instagram.com/p/DOmsVdoAQM-/", 
        "https://www.instagram.com/p/DOmqZfqAfmT/",
        "https://www.instagram.com/p/DOqCgvZAPQs/",
        "https://www.instagram.com/p/DOewnOYCquK/",
        "https://www.instagram.com/p/DNcxuNnov5T/",
        "https://www.instagram.com/p/DNnRf_FPSQt/",
        "https://www.instagram.com/p/DOqzF_cjb4L/",
        "https://www.instagram.com/p/DOoIbQdiqhH/",
        "https://www.instagram.com/p/DOcwIl-kfg3/"
        # Add your URLs here
    ]
    
    # Initialize client
    cl = setup_client()
    if not cl:
        print("Failed to setup Instagram client")
        return
    
    all_comments = []
    
    for i, url in enumerate(urls, 1):
        print(f"\nProcessing URL {i}/{len(urls)}: {url}")
        
        # Get media ID
        media_id = get_media_id_from_url(cl, url)
        if not media_id:
            continue
        
        # Scrape comments
        comments = scrape_comments(cl, media_id, max_comments=100)
        all_comments.extend(comments)
        
        # Add delay to avoid rate limiting
        if i < len(urls):
            print("Waiting 3 seconds...")
            time.sleep(3)
    
    # Save all comments to CSV
    if all_comments:
        save_to_csv(all_comments, 'instagram_comments.csv')
        print(f"\nTotal comments scraped: {len(all_comments)}")
    else:
        print("No comments were scraped")

if __name__ == "__main__":
    main()