# Depedancies
#   to retrieve .env variables
import os
from dotenv import load_dotenv
#   to perform requests
import requests
#   to scrape
from bs4 import BeautifulSoup
import re
import time
#   to scrape and timestamp
from datetime import date

# Environmental setup
rootdir = os.path.expanduser('~/wiki-news-scraper')
load_dotenv(os.path.join(rootdir, '.env'))

# Utility functions


def form_wiki_href_from_slug(slug):
    print(slug)
    print(slug[0:3])
    if slug[0:3] == "/w/" or len(slug) == 0:
        return ""
    return "https://en.wikipedia.org" + slug


def get_clean_ele_text(ele):
    return ele.text.strip()

# Dictionary that will be exported


all_scraped_news = {}

# --- Start by getting the title and link for each news

timestamp = str(date.today())

scrape_target = "https://en.wikipedia.org/wiki/Portal:Current_events"
response = requests.get(url=scrape_target)
soup = BeautifulSoup(response.content, 'html.parser')

# Find the element containing "Topics in the news" (it's at the top)

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

# Recent deaths, though on the Current Events page, can be more efficiently gathered on the Deaths page

year = timestamp[0:4]

scrape_target = "https://en.wikipedia.org/wiki/Deaths_in_%s" % (year)
response = requests.get(url=scrape_target)
soup = BeautifulSoup(response.content, 'html.parser')

day = timestamp[-3:]

wiki_recent_deaths_day_header = soup.find('h3')

header_int = int(wiki_recent_deaths_day_header.text)

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
    news['href'] = form_wiki_href_from_slug(link['href'])
    all_scraped_news['deaths'].append(news)

# --- Now to add content, location, and featured image src to each news object (if they news has its own page (and if these things are present))

for category in all_scraped_news.keys():
    for news in all_scraped_news[category]:
        if len(news['href']):
            scrape_target = news['href']
            response = requests.get(url=scrape_target)
            soup = BeautifulSoup(response.content, 'html.parser')

            article_first_p_els = soup.find("div", {"class": "mw-parser-output"}).find_all(
                "p", class_=False, id=False)

            news['content'] = []

            for p_el in article_first_p_els:
                text_content = p_el.text.strip()

                if len(text_content) > 40 and len(news['content']) < 3 and not p_el.find_parent('td'):

                    news['content'].append(text_content)
                else:
                    continue

            if category == "deaths":
                pod = ""
                pod_header = soup.find("th", string="Died")
                if not pod_header:
                    pod_header = soup.find('th', string="Place of death")
                if not pod_header:
                    pod = soup.find(
                        'div', {"class": "deathplace"})
                if pod:
                    news["location_string"] = pod.text.strip()
                elif pod_header:
                    news["location_string"] = pod_header.next_element.next_element.text.strip()
            else:
                location_ele = soup.find("div", {"class": "location"})
                geo_dec = soup.find('span', {"class": "geo-dec"})
                geo_dms = soup.find('span', {"class": "geo-dms"})
                if geo_dec:
                    news['geo_dec'] = geo_dec.text.strip()
                elif geo_dms:
                    news['geo_dms'] = geo_dms.text.strip()
                elif location_ele:
                    news['location_string'] = location_ele.text.strip()[0:20]

            img_parent = soup.find('a', {"class": "image"})
            if img_parent:
                img_ele = img_parent.find("img")
                if int(img_ele['width']) > 80:
                    news['feature_img_src'] = "https:" + img_ele["src"]

        print("______________")
        time.sleep(0.5)
