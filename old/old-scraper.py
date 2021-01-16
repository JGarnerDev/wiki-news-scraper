
from bs4 import BeautifulSoup
from dms2dec.dms_convert import dms2dec
from urllib.parse import quote
from datetime import date
from pymongo import MongoClient
from dotenv import load_dotenv
import pymongo
import geograpy
import json
import re
import os
import requests


# Env variables

rootdir = os.path.expanduser('~/wiki-news-scraper')
load_dotenv(os.path.join(rootdir, '.env'))

WIKI_SCRAPE_HERE_API_KEY = os.getenv("WIKI_SCRAPE_HERE_API_KEY")
WIKI_SCRAPE_DB_PASS = os.getenv("WIKI_SCRAPE_DB_PASS")
WIKI_SCRAPE_DB_USER = os.getenv("WIKI_SCRAPE_DB_USER")


response = requests.get(url="https://en.wikipedia.org/wiki/Main_Page")
soup = BeautifulSoup(response.content, 'html.parser')

# Mongo

mongo_connection_template = "mongodb+srv://wiki-scrape:%s@cluster0.5f7z9.mongodb.net/%s?retryWrites=true&w=majority"
mongo_connection_string = mongo_connection_template % (
    WIKI_SCRAPE_DB_PASS, WIKI_SCRAPE_DB_USER)

cluster = MongoClient(
    mongo_connection_string)

# End product

news_featured = []
news_ongoing = []
news_recent_deaths = []


all_news = {
    "featured": news_featured,
    "ongoing": news_ongoing,
    "recent_deaths": news_recent_deaths
}


# Scraping featured news - Wikipedia main page, the top-right section with the heading "In the news", the dotted ul of recent news

wiki_itn_featured = soup.find(id="mp-itn").find_all("li")

for news in wiki_itn_featured:
    main_article_link = news.find('b')
    if main_article_link:
        title = main_article_link.find('a')['title']
        if "Wikipedia:" in title:
            continue
        slug = main_article_link.find('a', href=True)['href']
        news_featured.append(
            {"title": title, "href": "https://en.wikipedia.org" + slug}
        )

# Scraping ongoing news - Wikipedia main page, the top-right section with the heading "In the news", the "Ongoing" section in the footer (immediately below featured news)

wiki_itn_ongoing = soup.find(
    "div",  {"class": "itn-footer"}).find('ul').find_all('a')

for news in wiki_itn_ongoing:
    title = news['title']
    slug = news['href']
    news_ongoing.append(
        {"title": title, "href": "https://en.wikipedia.org" + slug}
    )

# Scraping recent deaths - Wikipedia main page, the top-right section with the heading "In the news", the "Recent deaths" section in the footer (immediately below ongoing news)

wiki_itn_recent_deaths = soup.find(
    "div",  {"class": "itn-footer"}).find_all('ul')[-1].find_all('a')

for news in wiki_itn_recent_deaths:
    title = news['title']
    slug = news['href']
    news_recent_deaths.append(
        {"title": title, "href": "https://en.wikipedia.org" + slug}
    )

# For each news object, go to the wikipedia page and scrape the top three paragraphs of main subject content, add it as a value to the news object


def query_for_dd(location_query):
    query_string = quote(location_query)
    api_query_template = "https://geocode.search.hereapi.com/v1/geocode?q=%s&apiKey=%s"
    api_query = api_query_template % (
        query_string, WIKI_SCRAPE_HERE_API_KEY)
    response = requests.get(api_query)
    response_dict = response.json()

    return response_dict['items'][0]['position']


for category in all_news.keys():
    for news in all_news[category]:
        href = news['href']

        response = requests.get(url=href)
        soup = BeautifulSoup(response.content, 'html.parser')

        topmost_paragraphs_elements = soup.find(
            id="mw-content-text").find_all('p', {'class': ''})[0:3]

        news['content'] = []
        for p_el in topmost_paragraphs_elements:
            content_with_citation_marks = p_el.text
            content_without_citation_marks = re.sub(
                r"\[\d\]", "", content_with_citation_marks)

            news['content'].append(content_without_citation_marks)

        # Some articles have a DMS string providing the location

        dms_el = soup.find('span', {'class': 'geo-dms'})
        # If they do, great! Convert it to Decimal Degrees, add it to the news object
        if dms_el:
            dms = dms_el.text.split(' ')
            news['coords'] = {'lat': dms2dec(dms[0]), 'lng': dms2dec(dms[1])}
            continue
        # ...If they don't, we have to infer from a string. Finding a table header of "location", "place of death", or a div with class "deathplace" are good starts
        else:
            location_query = ''
            if (location_table_header := soup.find('th', string="Location")):
                location_query = location_table_header.next_element.next_element.text.strip()

            elif (location_table_header := soup.find('th', string="Place of death")):
                location_query = location_table_header.next_element.next_element.text.strip()
            elif (location_table_header := soup.find('th', string="Died")):
                location_query = location_table_header.next_element.next_element.text.strip()

            elif (location := soup.find('div', {"class": "deathplace"})):
                location_query = location.text.strip()
            # ... pick the article heading and look for country as a fallback
            else:
                heading = soup.find(
                    id="firstHeading").text

                location_query = geograpy.get_geoPlace_context(
                    text=heading).countries[0]

            # ... and ask the HERE Geocoding API for help, recieving geolocation based on the best string we found and add it to the news object
            news['coords'] = query_for_dd(location_query)


today = date.today()
timestamp = today.strftime("%d %B %Y")

# Send it to mongo


db = cluster['wiki-scrape']
collection = db[timestamp]


collection.insert_one(all_news)

if collection.count_documents({}) > 14:
    oldestNews = collection.delete_one({})
