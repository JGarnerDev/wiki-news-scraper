from bs4 import BeautifulSoup
import requests


def get_soup(target):
    response = requests.get(url=target)
    return BeautifulSoup(response.content, 'html.parser')


def form_wiki_href_from_slug(slug):
    if slug[0:3] == "/w/" or len(slug) == 0:
        return None
    return "https://en.wikipedia.org" + slug


def get_clean_ele_text(ele):
    return ele.text.strip()


def get_current_events_from_soup(soup, day, year, destination):
    wiki_current_itn = soup.find(
        "div",  {"aria-labelledby": "Topics_in_the_news"})

    wiki_current_itn_featured = wiki_current_itn.find('ul').find_all('li')

    destination['featured'] = []

    for ele in wiki_current_itn_featured:
        news = {}
        link = ele.find('b').find('a')
        news['title'] = link['title']
        news['href'] = form_wiki_href_from_slug(link['href'])
        destination['featured'].append(news)

    wiki_current_ongoing = soup.find(
        "div",  {"aria-labelledby": "Ongoing_events"})

    ongoing_categories_headers = wiki_current_ongoing.find_all("h3")
    ongoing_categories_lists = wiki_current_ongoing.find_all("ul")

    for i, category_header in enumerate(ongoing_categories_headers):
        category = get_clean_ele_text(category_header).lower()
        destination[category] = []

        for li in ongoing_categories_lists[i].find_all('li'):
            news = {}
            link = li.find('a')
            news['title'] = link['title']
            news['href'] = form_wiki_href_from_slug(link['href'])
            destination[category].append(news)

    scrape_target = "https://en.wikipedia.org/wiki/Deaths_in_%s" % (year)
    soup = get_soup(scrape_target)

    wiki_recent_deaths_day_header = soup.find('h3')

    header_int = int(wiki_recent_deaths_day_header.text)

    if header_int > int(day):
        wiki_recent_deaths_day_header = soup.find('h3').find_next_sibling(
            'h3')

    wiki_recent_deaths = wiki_recent_deaths_day_header.find_next_sibling(
        'ul').find_all('li')

    destination['deaths'] = []

    for li in wiki_recent_deaths:
        news = {}
        link = li.find('a')
        news['title'] = link['title']
        href = form_wiki_href_from_slug(link['href'])

        if href:
            news['href'] = href

        destination['deaths'].append(news)

    return
