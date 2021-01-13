# Wiki-News-Scraper

## Introduction and Purpose

Wiki-News-Scraper is a web scraper that implements BeautifulSoup to identify specific articles of Wikipedia.com, travel to each article's page, and retrieve both a summary and, as best as possible, location data. It will be automated. When it is finished, it sends this data to a Flask API (another project of mine) to be processed and stored.

At a high level, this web scraper is the means of deriving content for my larger project (no title yet) which implements a microservice architecture. This application is purposed to provide a quick summary of current world events over a global map visual.

I like explaining things; there will be a .md file to articulate my thought process and, depending on interest, make thing approachable to anyone wanting to learn.

## Control Flow

1. Find the webpage of interest
1. Find the article links of interest
1. Per article...

   1. Take the title of the article
   1. Take the text of the top paragraphs per article
   1. Get the location of the news by (in order of reliability):

      1. Obtaining the DMS string if present, _or_
      1. Obtaining a location string if present, _or_
      1. Simply using the article title with a 3rd party API

   1. Get the featured image src of the article

1. Organize the scraped material, send it to my Flask API

## Environment

Wiki-News-Scraper will be automated at [Python Anywhere](https://www.pythonanywhere.com/)

## History

As seen in scraper.py, this project was originally designed to scrape and format information in run time, relying on an API to turn our locations into DD geolocation data. Now that I'm adopting the microservice architecture, this is a silly thing to do. Instead of burdening this task with many features (as some sort of love letter to how cool Python is), it will only scrape and submit scraped strings. A more efficient use of resources, less reliance on libraries, and less to test. I'm loving it.
