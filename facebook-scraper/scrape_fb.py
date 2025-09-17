import os
import time
import json
import random
from io import StringIO
import pandas as pd

# ==== Selenium imports ====
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# ==========================
# Helper functions
# ==========================

def configure_driver():
    """Configure Chrome driver with webdriver-manager"""
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver


def login_facebook(username, password, driver):
    """Login to Facebook"""
    driver.get("https://www.facebook.com/")
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "email"))
    ).send_keys(username)
    driver.find_element(By.ID, "pass").send_keys(password)          
    driver.find_element(By.NAME, "login").click()                   
    time.sleep(5)  # wait for login
    print("Logged into Facebook.")


def scroll_and_click_button(driver):
    """Scroll until the 'All comments | Most relevant' button is clickable"""
    cnt = 3
    try:
        while cnt > 0:
            try:
                button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "div.x9f619.x1n2onr6.x1ja2u2z.x6s0dn4.x3nfvp2.xxymvpz")
                    )
                )
                button.click()
                print("Comment sort button clicked.")
                return True
            except Exception:
                driver.execute_script("window.scrollBy(0, 1000);")
                cnt -= 1
        return False
    except Exception as e:
        print("Unable to click comment sort button:", e)
        return False


def click_showed_type_btn(driver, btn_name):
    """Click 'All comments' or 'Most relevant'"""
    try:
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{btn_name}')]"))
        )
        button.click()
        return True
    except Exception:
        print(f"Could not click {btn_name}")
        return False


def click_view_more_btn(driver):
    """Click 'View more comments' if available"""
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        view_more_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'more comments')]"))
        )
        view_more_btn.click()
        print("Clicked 'View more comments'.")
        return True
    except Exception:
        return False


def show_more_comments(driver, max_attempts=10):
    """Keep clicking 'View more comments' until done"""
    attempts = 0
    while attempts < max_attempts:
        if not click_view_more_btn(driver):
            break
        time.sleep(2)
        attempts += 1
    print("Finished loading more comments.")


def filter_spam(text):
    """Basic spam filter"""
    spam_text = ['http', 'miễn phí', '100%', 'kèo bóng', 'khóa học', 'netflix', 'shopee', 'lazada']
    for spam in spam_text:
        if spam.lower() in text.lower():
            return True
    return False


def get_comments(driver, limit_text=2500):
    """Extract visible comments"""
    cnt = 0
    results = []
    comments = driver.find_elements(By.XPATH, "//div[contains(@class, 'x1n2onr6')]")
    for comment in comments:
        try:
            text_ele = comment.find_element(By.XPATH, ".//div[contains(@class, 'xdj266r')]")
            username = comment.find_element(By.XPATH, ".//span[@class='x3nfvp2']/span")
            if text_ele:
                cnt += 1
                if cnt > limit_text:
                    break
                text = text_ele.text
                results.append({
                    "id": cnt,
                    "username": username.text if username else "",
                    "text": text,
                    "is_spam": 1 if filter_spam(text) else 0
                })
        except Exception:
            continue
    print(f"Collected {cnt} comments.")
    return results, cnt


def save_to_csv(df, file_name):
    """Save DataFrame to CSV"""
    df.to_csv(file_name, index=False)

# ==========================
# Core crawler
# ==========================

def crawl_one_post(driver, url):
    """Crawl a single FB post (assumes already logged in)"""
    driver.get(url)
    time.sleep(5)

    scroll_and_click_button(driver)
    click_showed_type_btn(driver, "All comments")
    show_more_comments(driver)

    cmts, cnt = get_comments(driver, limit_text=2500)
    return cmts, cnt

# ==========================
# Main script
# ==========================

if __name__ == "__main__":
    # ==== EDIT THESE ====
    username = "2234664@slu.edu.ph"
    password = "Scraper1234567890"

    urls = [
        "https://www.facebook.com/reel/624010930646756",
        "https://www.facebook.com/photo/?fbid=1279436697548194&set=a.647063400785530",
        "https://www.facebook.com/kapusomojessicasoho/videos/4243492582599046"
    ]
    # ====================

    driver = configure_driver()
    all_rows = []

    try:
        login_facebook(username, password, driver)

        for idx, url in enumerate(urls, start=1):
            print(f"\nScraping: {url}")
            cmt_data, cnt = crawl_one_post(driver, url)

            # Limit to 40 random comments (or fewer if <40 available)
            if cmt_data:
                if len(cmt_data) > 40:
                    cmt_data = random.sample(cmt_data, 40)

                all_rows.extend(cmt_data)

                # Save per-post file
                df_post = pd.read_json(StringIO(json.dumps(cmt_data, ensure_ascii=False)), orient="records")
                per_post_path = os.path.join(os.path.expanduser("~"), "Downloads", f"comments_post_{idx}.csv")
                save_to_csv(df_post, per_post_path)
                print(f"Saved per-post CSV (max 40 comments): {per_post_path}")

        # Save combined (sum of per-post limits)
        if all_rows:
            df_all = pd.read_json(StringIO(json.dumps(all_rows, ensure_ascii=False)), orient="records")
            combined_path = os.path.join(os.path.expanduser("~"), "Downloads", "comments.csv")
            save_to_csv(df_all, combined_path)
            print(f"\nSaved combined CSV: {combined_path}")

    finally:
        driver.quit()
