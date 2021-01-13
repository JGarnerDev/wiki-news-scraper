# Setup / dependancies

#   Setup / dependancies / to retrieve .env variables
import os
from dotenv import load_dotenv

#   Setup / dependancies / to perform requests
import requests

#   Setup / dependancies / to scrape
from bs4 import BeautifulSoup
import re
import time

#   Setup / dependancies / to scrape and timestamp
from datetime import date

# Setup / environmental variables to scope
rootdir = os.path.expanduser('~/wiki-news-scraper')
load_dotenv(os.path.join(rootdir, '.env'))

# Setup / utility functions


def form_wiki_href_from_slug(slug):
    if slug[0:3] == "/w/" or len(slug) == 0:
        return None
    return "https://en.wikipedia.org" + slug


def get_clean_ele_text(ele):
    return ele.text.strip()

# Setup / time strings


timestamp = str(date.today())
year = timestamp[0:4]
day = timestamp[-3:]

# Setup / dictionary that will be exported

all_scraped_news = {}

# Setup / metrics

news_amount = 0

## Scraping begins ##

# Scrape featured events

scrape_target = "https://en.wikipedia.org/wiki/Portal:Current_events"
response = requests.get(url=scrape_target)
soup = BeautifulSoup(response.content, 'html.parser')

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
response = requests.get(url=scrape_target)
soup = BeautifulSoup(response.content, 'html.parser')

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
        news_amount += 1

        if "href" in news.keys():
            scrape_target = news['href']
            response = requests.get(url=scrape_target)
            soup = BeautifulSoup(response.content, 'html.parser')

            article_first_p_els = soup.find("div", {"class": "mw-parser-output"}).find_all(
                "p", class_=False, id=False)

            news['content'] = []

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
                pod = ""
                pod_header = soup.find("th", string="Died")
                if not pod_header:
                    pod_header = soup.find('th', string="Place of death")
                if not pod_header:
                    pod = soup.find(
                        'div', {"class": "deathplace"})
                if pod:
                    news["location_string"] = get_clean_ele_text(pod)
                elif pod_header:
                    news["location_string"] = get_clean_ele_text(
                        pod_header.next_element.next_element)

            else:
                location_ele = soup.find("div", {"class": "location"})
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
                        0:20]

            img_parent = soup.find('a', {"class": "image"})
            if img_parent:
                img_ele = img_parent.find("img")
                # if this size, likely not a ui icon or somesuch
                if int(img_ele['width']) > 80:
                    news['feature_img_src'] = "https:" + img_ele["src"]

        # Be polite and don't create stress on target servers - wait 0.5 seconds before scraping again
        time.sleep(0.5)

## Scraping ends ##

# Metrics / final census

news_scraped_content = 0
news_possible_content = news_amount * 5

for category in all_scraped_news.keys():
    for news in all_scraped_news[category]:
        for content in news.keys():
            news_scraped_content += 1

news_content_saturation = (news_scraped_content / news_possible_content) * 100


# Ship it somewhere for cleaning

output = {
    "timestamp": timestamp,
    "amount": news_amount,
    "saturation": news_content_saturation,
    "description": "This is the raw news data scraped from Wikipedia by wiki-news-scraper",
    "scraped": all_scraped_news
}

print(output['saturation'])
