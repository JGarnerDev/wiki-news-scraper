from utils import *
from .main.utils import *
import os
import sys
from bs4 import BeautifulSoup
import unittest

sys.path.append('/main/utils.py')

script_dir = os.path.dirname(__file__)
rel_path = "mock"
abs_file_path = os.path.join(script_dir, rel_path)


# console command: python -m  tests.test_utils

# Because requests doesn't work with local files,
# and that 'get_soup' is stable, we'll mock it.

def mock_get_soup(target):
    page = open(target, encoding="utf-8")
    return BeautifulSoup(page.read())

# Testing the initial gathering of desired news titles and links


class TestGetCurrentEvents(unittest.TestCase):
    def test_initial_scrape(self):

        target_current_events_page = abs_file_path + '\page_current_events.html'
        soup = mock_get_soup(target_current_events_page)

        all_scraped_news = {}

        day = "17"
        year = "2021"

        get_current_events_from_soup(
            soup, day, year, destination=all_scraped_news)

        self.assertIn("feauterd", all_scraped_news)
