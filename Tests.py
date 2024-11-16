import unittest
import os
from wiki_parser import WikiLinkDB
import wiki_parser

def mock_test_1(url: str):
    res = {
        "https://ru.wikipedia.org/wiki/Python1": '"href="/wiki/Python2"',
        "https://ru.wikipedia.org/wiki/Python2": '"href="/wiki/Python3"',
        "https://ru.wikipedia.org/wiki/Python3": '"href="/wiki/Python4"',
        "https://ru.wikipedia.org/wiki/Python4": '"href="/wiki/Python5"',
        "https://ru.wikipedia.org/wiki/Python5": '"href="/wiki/Python6"',
        "https://ru.wikipedia.org/wiki/Python6": '"href="/wiki/Python7"',
        "https://ru.wikipedia.org/wiki/Python7": '"href="/wiki/Python8"',
        "https://ru.wikipedia.org/wiki/Python8": '"href="/wiki/Python9"',
        "https://ru.wikipedia.org/wiki/Python9": '"href="/wiki/Python10"'
    }
    return res[url]

def mock_test_2(url: str) :
    res = {
        "https://ru.wikipedia.org/wiki/Python1": '"href="/wiki/Python2", "href="/wiki/Python3", "href="/wiki/Python4"',
        "https://ru.wikipedia.org/wiki/Python2": '"href="/wiki/Python3"',
        "https://ru.wikipedia.org/wiki/Python3": '"href="/wiki/Python4", "href="/wiki/Python8", "href="/wiki/Python5"',
        "https://ru.wikipedia.org/wiki/Python4": '"href="/wiki/Python1"',
        "https://ru.wikipedia.org/wiki/Python5": '"href="/wiki/Python6"',
        "https://ru.wikipedia.org/wiki/Python6": '"href="/wiki/Python7"',
        "https://ru.wikipedia.org/wiki/Python7": '"href="/wiki/Python11"',
        "https://ru.wikipedia.org/wiki/Python8": '"href="/wiki/Python9"',
        "https://ru.wikipedia.org/wiki/Python9": '"href="/wiki/Python10"',
        "https://ru.wikipedia.org/wiki/Python11": '"href="/wiki/Python12"',
        "https://ru.wikipedia.org/wiki/Python10": '"href="/wiki/Python13"',
        "https://ru.wikipedia.org/wiki/Python13": '"href="/wiki/Python6"',
    }
    return res[url]


class TestWikipediaScraper(unittest.TestCase):
    TEST_DB_NAME = "test_wiki_links.db"

    def setUp(self) -> None:
        self.db = WikiLinkDB(self.TEST_DB_NAME)

    def tearDown(self) -> None:
        self.db.close()
        if os.path.exists(self.TEST_DB_NAME):
            os.remove(self.TEST_DB_NAME)

    def test_find_links(self):
        wiki_parser.fetch_links = mock_test_1
        result = wiki_parser.find_links('https://ru.wikipedia.org/wiki/Python1')
        print(result)
        self.assertEqual(result, ["https://ru.wikipedia.org/wiki/Python2"])

    def test_get_links(self):
        wiki_parser.fetch_links = mock_test_1
        result = wiki_parser.get_links('https://ru.wikipedia.org/wiki/Python1', 6)
        print(result)
        self.assertEqual(result[2], (3, "https://ru.wikipedia.org/wiki/Python4"))

    def test_find_several_links(self):
        wiki_parser.fetch_links = mock_test_2
        result = wiki_parser.find_links('https://ru.wikipedia.org/wiki/Python3')
        print(result)
        self.assertEqual(result, ["https://ru.wikipedia.org/wiki/Python4", "https://ru.wikipedia.org/wiki/Python8", "https://ru.wikipedia.org/wiki/Python5"])

    def test_get_several_links(self):
        wiki_parser.fetch_links = mock_test_2
        result = wiki_parser.get_links("https://ru.wikipedia.org/wiki/Python1", 6)
        print(result)
        self.assertEqual(len(result), 13)

if __name__ == "__main__":
    unittest.main()
