import requests
from bs4 import BeautifulSoup

response = requests.get(url="https://en.wikipedia.org/wiki/Main_Page")
soup = BeautifulSoup(response.content, 'html.parser')


news_featured = []
news_ongoing = []
news_recent_deaths = []

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

wiki_itn_ongoing = soup.find(
    "div",  {"class": "itn-footer"}).find('ul').find_all('a')

for news in wiki_itn_ongoing:
    title = news['title']
    slug = news['href']
    news_ongoing.append(
        {"title": title, "href": "https://en.wikipedia.org" + slug}
    )

wiki_itn_recent_deaths = soup.find(
    "div",  {"class": "itn-footer"}).find_all('ul')[-1].find_all('a')

for news in wiki_itn_recent_deaths:
    title = news['title']
    slug = news['href']
    news_recent_deaths.append(
        {"title": title, "href": "https://en.wikipedia.org" + slug}
    )

all_news = {
    "featured": news_featured,
    "ongoing": news_ongoing,
    "recent_deaths": news_recent_deaths
}

for category in all_news.keys():
    for news in all_news[category]:
        href = news['href']

        response = requests.get(url=href)
        soup = BeautifulSoup(response.content, 'html.parser')

        topmost_paragraphs_elements = soup.find(
            id="mw-content-text").find_all('p', {'class': ''})[0:3]

        for p_el in topmost_paragraphs_elements:
            news['content'] = p_el.text


print(all_news)
