import os
import csv
import time
import sys
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, PleaseWaitFewMinutes, ChallengeRequired

SESSION_FILE = 'session.json'

def delete_session():
    """Delete existing session file to force fresh login"""
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
        print(f"✅ Deleted old session file: {SESSION_FILE}")
        return True
    else:
        print("ℹ️ No session file found to delete")
        return False

def setup_client(force_fresh_login=False):
    """Initialize and login to Instagram with better session handling"""
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
    
    # Delete session if force fresh login is requested
    if force_fresh_login:
        delete_session()
    
    try:
        # Try to load existing session first (unless forcing fresh login)
        if not force_fresh_login and os.path.exists(SESSION_FILE):
            print("Loading existing session...")
            cl.load_settings(SESSION_FILE)
            
            # Try to verify session without full login
            try:
                cl.get_timeline_feed()  # Test if session is still valid
                print("Session is still valid!")
                return cl
            except Exception:
                print("Session expired, deleting and attempting fresh login...")
                delete_session()  # Auto-delete corrupt session
        
        print("Attempting fresh login...")
        # Fresh login with more realistic behavior
        time.sleep(2)  # Wait before login attempt
        cl.login(username, password)
        cl.dump_settings(SESSION_FILE)
        print("Successfully logged in and saved session")
        
        return cl
        
    except (LoginRequired, PleaseWaitFewMinutes, ChallengeRequired) as e:
        print(f"Instagram security measure triggered: {e}")
        print("\n🚫 SECURITY SOLUTIONS:")
        print("1. Wait 24-48 hours before trying again")
        print("2. Log into Instagram manually through browser/app first")
        print("3. Complete any security challenges Instagram shows you")
        print("4. Use a VPN or different IP address")
        print("5. Run script with force_fresh_login=True")
        
        # Auto-delete potentially problematic session
        delete_session()
        return None
        
    except Exception as e:
        error_msg = str(e)
        print(f"Login failed: {error_msg}")
        
        # Auto-delete session on any login failure
        delete_session()
        
        if any(keyword in error_msg.lower() for keyword in ["blacklist", "ip", "blocked", "suspicious"]):
            print("\n🚫 IP BLOCKED SOLUTIONS:")
            print("1. Wait 24-48 hours before trying again")
            print("2. Use a VPN to change your IP address")
            print("3. Try from a different network (mobile hotspot)")
            print("4. Set INSTAGRAM_PROXY environment variable")
            print("5. Try logging in manually through Instagram app/website first")
            print("6. Run script with force_fresh_login=True")
        
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
    """Save comments to CSV file"""
    if not comments:
        print("No comments to save")
        return
    
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['comment_id', 'username', 'text', 'created_at_utc', 'like_count']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(comments)
    
    print(f"Saved {len(comments)} comments to {filename}")

def main():
    # Check for command line arguments
    force_fresh = "--fresh" in sys.argv or "--delete-session" in sys.argv
    if force_fresh:
        print("🔄 Force fresh login requested")
    
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
    cl = setup_client(force_fresh_login=force_fresh)
    if not cl:
        print("Failed to setup Instagram client")
        print("\n💡 TIP: Try running with --fresh flag to delete old session:")
        print("python scraper.py --fresh")
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