# Setup / dependancies

#   Setup / dependancies / to retrieve .env variables
import os
from dotenv import load_dotenv

#   Setup / dependancies / to perform requests
import requests

#   Setup / dependancies / to scrape
from bs4 import BeautifulSoup
import time

#   Setup / dependancies / to scrape and timestamp
from datetime import datetime

#   Setup / dependancies / to send output
import json
#   Setup / dependancies / encryption
from cryptography.fernet import Fernet


# Setup / environmental variables to scope
rootdir = os.path.expanduser('~/wiki-news-scraper')
load_dotenv()

WIKI_NEWS_WRANGLER_URI = os.getenv("WIKI_NEWS_WRANGLER_URI")
WIKI_NEWS_WRANGLER_PASS = os.getenv("WIKI_NEWS_WRANGLER_PASS")
F_KEY = os.getenv("F_KEY")

# Setup / encrypting wiki-news-wrangler password for http request

key = bytes(F_KEY, 'utf-8')
f = Fernet(key)

pw = bytes(WIKI_NEWS_WRANGLER_PASS, 'utf-8')
token = f.encrypt(pw).decode('utf-8')

# Setup / utility functions


def get_soup(target):
    response = requests.get(url=target)
    return BeautifulSoup(response.content, 'html.parser')


def form_wiki_href_from_slug(slug):
    if slug[0:3] == "/w/" or len(slug) == 0:
        return None
    return "https://en.wikipedia.org" + slug


def get_clean_ele_text(ele):
    return ele.text.strip()

# Setup / time strings


now = datetime.now()
timestamp = datetime.timestamp(now)

t_str = str(datetime.fromtimestamp(timestamp))[:-10]
year = t_str[:-12]
day = t_str[8:-6]

# Setup / dictionary that will be exported
all_scraped_news = {}

## Scraping begins ##

# Scrape featured events

scrape_target = "https://en.wikipedia.org/wiki/Portal:Current_events"
soup = get_soup(scrape_target)

# Find the element containing "Topics in the news" (it's at the top of scrape target view)

wiki_current_itn = soup.find(
    "div",  {"aria-labelledby": "Topics_in_the_news"})

# The featured topics in the news are in the first ul. Get it, take all the li

wiki_current_itn_featured = wiki_current_itn.find('ul').find_all('li')

all_scraped_news['featured'] = []

for ele in wiki_current_itn_featured:
    news = {}
    link = ele.find('b').find('a')
    news['title'] = link['title']
    news['href'] = form_wiki_href_from_slug(link['href'])
    all_scraped_news['featured'].append(news)

# Scrape ongoing events

# Ongoing events are listed in a widget in the right-hand side of the view
# They will be added to the all_scraped_news dictionary by dynamic keys, as I'm not certain that each is always present

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

# Scrape recent deaths (a different page for efficiency)

scrape_target = "https://en.wikipedia.org/wiki/Deaths_in_%s" % (year)
soup = get_soup(scrape_target)

wiki_recent_deaths_day_header = soup.find('h3')

header_int = int(wiki_recent_deaths_day_header.text)

# Wikipedia has headers set automatically, so there is the risk of having the next day (int) as a header
# Current implementation is bad: should confirm that header_int is int(day)
if header_int > int(day):
    wiki_recent_deaths_day_header = soup.find('h3').find_next_sibling(
        'h3')

wiki_recent_deaths = wiki_recent_deaths_day_header.find_next_sibling(
    'ul').find_all('li')

all_scraped_news['deaths'] = []

for li in wiki_recent_deaths:
    news = {}
    link = li.find('a')
    news['title'] = link['title']
    href = form_wiki_href_from_slug(link['href'])

    if href:
        news['href'] = href

    all_scraped_news['deaths'].append(news)


# Using each news href (if it exists):
#   Scrape content, location, and featured image src to each news object (if they exist)

for category in all_scraped_news.keys():
    for news in all_scraped_news[category]:
        if "href" in news.keys():
            news['content'] = []
            scrape_target = news['href']
            soup = get_soup(scrape_target)

            article_first_p_els = soup.find("div", {"class": "mw-parser-output"}).find_all(
                "p", class_=False, id=False)

            img_parent = soup.find('a', {"class": "image"})

            if img_parent:
                img_ele = img_parent.find("img")
                # if this size, likely not a ui icon or somesuch
                if int(img_ele['width']) > 80:
                    news['feature_img_src'] = "https:" + img_ele["src"]

            for p_el in article_first_p_els:
                text_content = get_clean_ele_text(p_el)
                # if the p element is not in a table element
                #   and if there's less than three entries to the content list
                #   and if the p element is significant in size (more than 40 characters (arbitrary))
                if not p_el.find_parent('td') and len(news['content']) < 3 and len(text_content) > 40:
                    news['content'].append(text_content)
                else:
                    continue

            if category == "deaths":
                # Time/place of death
                tpod = ""
                tpod_header = soup.find("th", string="Died")
                if not tpod_header:
                    tpod_header = soup.find('th', string="Place of death")
                if not tpod_header:
                    tpod = soup.find(
                        'div', {"class": "deathplace"})
                if tpod:
                    news["tpod"] = get_clean_ele_text(tpod)
                elif tpod_header:
                    news["tpod"] = get_clean_ele_text(
                        tpod_header.next_element.next_element)

            else:
                location_ele = soup.find("div", {"class": "location"})
                if not location_ele:
                    location_ele = soup.find("td", {"class": "location"})
                if not location_ele:
                    location_ele = soup.find(
                        "th",  string="location")
                    if location_ele:
                        location_ele = location_ele.next_sibling()
                geo_dec = soup.find('span', {"class": "geo-dec"})
                geo_dms = soup.find('span', {"class": "geo-dms"})
                # If it exists, take the first one of the following values (in order of preferrence)
                if geo_dec:
                    news['geo_dec'] = get_clean_ele_text(geo_dec)
                elif geo_dms:
                    news['geo_dms'] = get_clean_ele_text(geo_dms)
                elif location_ele:
                    # Take a useful enough string segment to run a geocode search
                    news['location_string'] = get_clean_ele_text(location_ele)[
                        0: 20]

        # Be polite and don't create stress on target servers - wait 0.5 seconds before scraping again
        time.sleep(0.5)

## Scraping ends ##

# Ship it to my wiki-news-wrangler API for cleaning

output = {
    "time": t_str,
    "description": "This is the raw news data scraped from Wikipedia by wiki-news-scraper",
    "scraped": all_scraped_news,
    "token": token
}

# Optional, for viewing entertainment:

# for category in output['scraped']:
#     for news in output['scraped'][category]:
#         print("---------")
#         print("CATEGORY: " + category)
#         for key in news.keys():
#             print(key + ": ")
#             print(news[key])


output = json.dumps(output)


requests.post(WIKI_NEWS_WRANGLER_URI, json=output)
# requests.post("http://127.0.0.1:33507/api/wrangler", json=output)
