import praw
import re
import csv
from dotenv import load_dotenv
load_dotenv()
import os

REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT')


print(REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT)

# List of Reddit post URLs or IDs to scrape
post_urls = [
	# Example: 'https://www.reddit.com/r/Python/comments/xxxxxx/example_post/',
	'https://www.reddit.com/r/ChikaPH/comments/1nh9fvk/all_flood_control_projects_for_2026_have_been/',
	'https://www.reddit.com/r/ChikaPH/comments/1nh9fht/pbbm_said_no_one_will_be_spared_in_the_flood/',
	'https://www.reddit.com/r/newsPH/comments/1n735a2/personalities_linked_to_anomalous_flood_control/'
]

def extract_post_id(url):
	"""Extract post ID from a Reddit URL or return the ID if already given."""
	match = re.search(r'/comments/([a-z0-9]+)/', url)
	if match:
		return match.group(1)
	# If it's just the ID
	return url.strip()

def save_to_csv(data, filename='reddit_comments.csv'):
    """Save the scraped data to a CSV file."""
    keys = data[0].keys() if data else ['url', 'user', 'comment']
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    print(f"Data saved to {filename}")

def main():
	reddit = praw.Reddit(
		client_id=REDDIT_CLIENT_ID,
		client_secret=REDDIT_CLIENT_SECRET,
		user_agent=REDDIT_USER_AGENT
	)
	
	data = []

	for url in post_urls:
		post_id = extract_post_id(url)
		submission = reddit.submission(id=post_id)
		print(f"\nPost: {submission.title}\nURL: {submission.url}")
		submission.comments.replace_more(limit=None)
		for comment in submission.comments:
			if not isinstance(comment, praw.models.Comment):
				continue
			if comment.parent_id != submission.fullname: #Ensures we only get top-level comments
				continue
			print(f"- {comment.author}: {comment.body[:200].replace('\n', ' ')}\n")
			data.append({
				'url': submission.url,
				'user': str(comment.author),
				'comment': comment.body,
				'id': comment.id,
				'parent_id': comment.parent_id
            })
		save_to_csv(data)
			

if __name__ == "__main__":
	main()
