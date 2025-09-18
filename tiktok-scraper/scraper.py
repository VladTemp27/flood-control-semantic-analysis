import asyncio
import csv
from playwright.async_api import async_playwright
from datetime import datetime

# XPaths from your JS
COMMENTS_DIV_XPATH = '//div[contains(@class, "DivCommentListContainer")]'
ALL_COMMENTS_XPATH = '//div[contains(@class, "DivCommentContentContainer")]'
LEVEL2_COMMENTS_XPATH = '//div[contains(@class, "DivReplyContainer")]'
PUBLISHER_PROFILE_XPATH = '//span[contains(@class, "SpanUniqueId")]'
NICKNAME_TIME_XPATH = '//span[contains(@class, "SpanOtherInfos")]'
LIKES_COMMENTS_SHARES_XPATH = "//strong[contains(@class, 'StrongText')]"
DESCRIPTION_XPATH = '//h4[contains(@class, "H4Link")]/preceding-sibling::div'
VIEW_MORE_XPATH = '//p[contains(@class, "PReplyAction") and contains(., "View")]'


def format_date(str_date: str):
    """Convert TikTok style date to DD-MM-YYYY"""
    if not str_date:
        return "No date"
    f = str_date.split('-')
    if len(f) == 1:
        return str_date
    elif len(f) == 2:
        return f"{f[1]}-{f[0]}-{datetime.now().year}"
    elif len(f) == 3:
        return f"{f[2]}-{f[1]}-{f[0]}"
    return "Malformed date"


async def scrape_tiktok_comments(url: str, output_csv: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url)

        # Scroll to load all 1st level comments
        loading_buffer = 30
        prev_len = 0
        while loading_buffer > 0:
            comments = await page.locator(ALL_COMMENTS_XPATH).all()
            if comments:
                await comments[-1].scroll_into_view_if_needed()

            new_len = len(comments)
            if new_len != prev_len:
                loading_buffer = 15
            else:
                await page.locator(COMMENTS_DIV_XPATH).scroll_into_view_if_needed()
                loading_buffer -= 1

            prev_len = new_len
            await page.wait_for_timeout(300)
        print("Opened all 1st level comments")

        # Expand replies (2nd level comments)
        loading_buffer = 5
        while loading_buffer > 0:
            read_more_buttons = await page.locator(VIEW_MORE_XPATH).all()
            for btn in read_more_buttons:
                await btn.click()
            await page.wait_for_timeout(500)
            if not read_more_buttons:
                loading_buffer -= 1
            else:
                loading_buffer = 5
        print("Opened all 2nd level comments")

        # Extract metadata
        publisher = await page.locator(PUBLISHER_PROFILE_XPATH).first.inner_text()
        nickname_and_time = (await page.locator(NICKNAME_TIME_XPATH).first.inner_text()).replace("\n", " ").split(" · ")
        description = await page.locator(DESCRIPTION_XPATH).first.inner_text()

        strong_tags = [await el.inner_text() for el in await page.locator(LIKES_COMMENTS_SHARES_XPATH).all()]
        likes_comments_shares = strong_tags[-3:] if strong_tags[-3].isdigit() else strong_tags[-2:]
        likes = likes_comments_shares[0]
        total_comments = likes_comments_shares[1]
        shares = likes_comments_shares[2] if len(likes_comments_shares) > 2 else "N/A"

        comments = await page.locator(ALL_COMMENTS_XPATH).all()
        level2_count = len(await page.locator(LEVEL2_COMMENTS_XPATH).all())

        # Write to CSV
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Now", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            writer.writerow(["Post URL", url])
            writer.writerow(["Publisher Nickname", nickname_and_time[0]])
            writer.writerow(["Publisher @", publisher])
            writer.writerow(["Publisher URL", f"https://www.tiktok.com/@{publisher}"])
            writer.writerow(["Publish Time", format_date(nickname_and_time[1])])
            writer.writerow(["Post Likes", likes])
            writer.writerow(["Post Shares", shares])
            writer.writerow(["Description", description])
            writer.writerow(["Number of 1st level comments", len(comments) - level2_count])
            writer.writerow(["Number of 2nd level comments", level2_count])
            writer.writerow(["Total Comments (rendered)", len(comments)])
            writer.writerow(["Total Comments (TikTok)", total_comments])
            writer.writerow([])
            writer.writerow(["ID", "Nickname", "User @", "User URL", "Comment Text", "Time", "Likes", "Profile Pic", "Is Reply"])

            for idx, c in enumerate(comments, start=1):
                try:
                    nickname = await c.locator("./div[1]/a").first.inner_text()
                    user_url = await c.locator("./a").first.get_attribute("href")
                    user = user_url.split("/")[3].lstrip("@")
                    comment_text = await c.locator("./div[1]/p").first.inner_text()
                    time_text = await c.locator("./div[1]/p[2]/span").first.inner_text()
                    comment_time = format_date(time_text)
                    likes_count = await c.locator("./div[2]").first.inner_text()
                    pic = await c.locator("./a/span/img").first.get_attribute("src") or "N/A"
                    is_reply = "Reply" in (await c.evaluate("el => el.parentElement.className"))

                    writer.writerow([idx, nickname, user, f"https://www.tiktok.com/@{user}", comment_text, comment_time, likes_count, pic, "Yes" if is_reply else "No"])
                except Exception as e:
                    print(f"Error parsing comment {idx}: {e}")

        print(f"Saved to {output_csv}")
        await browser.close()


if __name__ == "__main__":
    url = input("Enter TikTok post URL: ").strip()
    asyncio.run(scrape_tiktok_comments(url, "tiktok_comments.csv"))
