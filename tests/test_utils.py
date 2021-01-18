import os
from bs4 import BeautifulSoup
import unittest

from main.utils import *

script_dir = os.path.dirname(__file__)
rel_path = "mock"
abs_file_path = os.path.join(script_dir, rel_path)

target_current_events_page = abs_file_path + '\page_current_events.html'

# console command: python -m  tests.test_utils


# Because requests doesn't work with local files,
# and that 'get_soup' is stable, we'll mock it.

def mock_get_soup(target):
    page = open(target, encoding="utf-8")
    return BeautifulSoup(page.read())


soup = mock_get_soup(target_current_events_page)
print(soup)


class TestUtils(unittest.TestCase):
    def test_something(self):
        return
