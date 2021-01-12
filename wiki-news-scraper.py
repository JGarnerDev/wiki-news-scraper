# Depedancies
#   to retrieve .env variables
import os
from dotenv import load_dotenv
#   to perform requests
import requests
#   to scrape
from bs4 import BeautifulSoup

# Environmental setup
rootdir = os.path.expanduser('~/wiki-news-scraper')
load_dotenv(os.path.join(rootdir, '.env'))

# Utility functions


def form_wiki_href_from_slug(slug):
    return "https://en.wikipedia.org" + slug


def get_clean_ele_text(ele):
    return ele.text.strip()

# Dictionary that will be exported


all_scraped_news = {
    "featured": [],


}

# Go!


initial_scrape_target = "https://en.wikipedia.org/wiki/Portal:Current_events"


response = requests.get(url=initial_scrape_target)
soup = BeautifulSoup(response.content, 'html.parser')

# Find the element containing "Topics in the news" (it's at the top)

wiki_current_itn = soup.find(
    "div",  {"aria-labelledby": "Topics_in_the_news"})

# The featured topics in the news are in the first ul. Get it, take all the li

wiki_current_itn_featured = wiki_current_itn.find('ul').find_all('li')


for ele in wiki_current_itn_featured:
    news = {}

    link = ele.find('b').find('a')
    # Title
    news['title'] = link['title']
    # Reference
    news['href'] = form_wiki_href_from_slug(link['href'])

    all_scraped_news['featured'].append(news)

# Add list to dictionary


# Ongoing events are listed in a widget in the right-hand side of the view

scraped_news_ongoing = []

wiki_current_ongoing = soup.find(
    "div",  {"aria-labelledby": "Ongoing_events"})

ongoing_categories_headers = wiki_current_ongoing.find_all("h3")
ongoing_categories_lists = wiki_current_ongoing.find_all("ul")


for i, category_header in enumerate(ongoing_categories_headers):
    category = get_clean_ele_text(category_header).lower()
    all_scraped_news[category] = []
    for li in ongoing_categories_lists[i].find_all('li'):
        news = {}
        link = li.find('a')
        news['title'] = link['title']
        news['href'] = form_wiki_href_from_slug(link['href'])
        all_scraped_news[category].append(news)
