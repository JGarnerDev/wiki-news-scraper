import requests
from bs4 import BeautifulSoup
import time
import json

from utils import get_soup, get_clean_ele_text, form_wiki_href_from_slug
from setup import t_str, token, day, year, WIKI_NEWS_WRANGLER_URI


all_scraped_news = {}

scrape_target = "https://en.wikipedia.org/wiki/Portal:Current_events"
soup = get_soup(scrape_target)

wiki_current_itn = soup.find(
    "div",  {"aria-labelledby": "Topics_in_the_news"})

wiki_current_itn_featured = wiki_current_itn.find('ul').find_all('li')

all_scraped_news['featured'] = []

for ele in wiki_current_itn_featured:
    news = {}
    link = ele.find('b').find('a')
    news['title'] = link['title']
    news['href'] = form_wiki_href_from_slug(link['href'])
    all_scraped_news['featured'].append(news)

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

scrape_target = "https://en.wikipedia.org/wiki/Deaths_in_%s" % (year)
soup = get_soup(scrape_target)

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
    href = form_wiki_href_from_slug(link['href'])

    if href:
        news['href'] = href

    all_scraped_news['deaths'].append(news)

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
                if int(img_ele['width']) > 80:
                    news['feature_img_src'] = "https:" + img_ele["src"]

            for p_el in article_first_p_els:
                text_content = get_clean_ele_text(p_el)
                if not p_el.find_parent('td') and len(news['content']) < 3 and len(text_content) > 40:
                    news['content'].append(text_content)
                else:
                    continue

            if category == "deaths":
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
                if geo_dec:
                    news['geo_dec'] = get_clean_ele_text(geo_dec)
                elif geo_dms:
                    news['geo_dms'] = get_clean_ele_text(geo_dms)
                elif location_ele:
                    # Take a useful enough string segment to run a geocode search
                    news['location_string'] = get_clean_ele_text(location_ele)[
                        0: 20]

        time.sleep(0.5)

output = {
    "time": t_str,
    "description": "This is the raw news data scraped from Wikipedia by wiki-news-scraper",
    "scraped": all_scraped_news,
    "token": token
}

output = json.dumps(output)

print(output)

# requests.post(WIKI_NEWS_WRANGLER_URI, json=output)
