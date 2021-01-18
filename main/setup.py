import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from datetime import datetime

rootdir = os.path.expanduser('~/wiki-news-scraper')
load_dotenv()

WIKI_NEWS_WRANGLER_URI = os.getenv("WIKI_NEWS_WRANGLER_URI")
WIKI_NEWS_WRANGLER_PASS = os.getenv("WIKI_NEWS_WRANGLER_PASS")
F_KEY = os.getenv("F_KEY")

key = bytes(F_KEY, 'utf-8')
f = Fernet(key)

pw = bytes(WIKI_NEWS_WRANGLER_PASS, 'utf-8')
token = f.encrypt(pw).decode('utf-8')

now = datetime.now()
timestamp = datetime.timestamp(now)

t_str = str(datetime.fromtimestamp(timestamp))[:-10]
year = t_str[:-12]
day = t_str[8:-6]
