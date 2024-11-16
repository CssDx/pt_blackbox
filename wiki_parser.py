import argparse
import sqlite3
import re
from urllib.parse import urlparse, quote
from urllib.request import urlopen
from typing import List, Tuple


db_name = "wiki_links.db"


class WikiLinkDB:
    def __init__(self, db_name: str = db_name) -> None:
        self.connection = sqlite3.connect(db_name)
        self.drop_table()
        self.create_table()

    def drop_table(self) -> None:
        cursor = self.connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS links")
        self.connection.commit()

    def create_table(self) -> None:
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE
            )
        """)
        self.connection.commit()

    def add_link(self, url: str) -> None:
        cursor = self.connection.cursor()
        try:
            cursor.execute("INSERT INTO links (url) VALUES (?)", (url,))
            self.connection.commit()
        except sqlite3.IntegrityError:
            pass

    def get_all_links(self) -> List[Tuple[int, str]]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM links")
        return cursor.fetchall()

    def close(self) -> None:
        self.connection.close()


def encode_url(url: str) -> str:
    url_pars = urlparse(url)
    wiki_index = url_pars.path.index('wiki')
    url_for_decode = url_pars.path[wiki_index + 5:]
    final_link = f'{url_pars.scheme}://{url_pars.netloc}/wiki/{quote(url_for_decode)}'
    return final_link


def fetch_links(url: str) -> str:
    try:
        url_open = urlopen(url)
        html_bytes = url_open.read()
        html_text = html_bytes.decode("utf-8")
        return html_text
    except Exception as e:
        print(f"Error fetching links from {url}: {e}")
        return None


def find_links(url: str) -> List[str]:
    html_text = fetch_links(url)
    if not html_text:
        return []
    links = re.findall(r'href="(/wiki/[^":#]+)"', html_text)
    return [f'https://ru.wikipedia.org{links[i]}' for i in range(len(links))]


def recurs_scrape(url: str, max_depth: int, db: WikiLinkDB, current_deep: int = 1) -> None:
    if current_deep > max_depth:
        return

    links = find_links(url)
    for link in links:
        db.add_link(link)
        recurs_scrape(link, max_depth, db, current_deep + 1)


def get_links(start_url, deep) -> List[Tuple[int, str]]:
    db = WikiLinkDB()
    try:
        recurs_scrape(encode_url(start_url), deep, db)
        result = db.get_all_links()
    finally:
        db.close()
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Утилита для парса ссылок с wiki")
    parser.add_argument("url", type=str, help="Ссылка на статью wiki")
    parser.add_argument("deep", type=int, help="Глубина поиска")


    args = parser.parse_args()

    print(f"Начало парсинга по ссылке: {args.url} с глубиной {args.deep}")
    global db_name
    result = get_links(args.url, args.deep)
    print(f"Парсинг завершен. Сохраненные ссылки:")
    for link_id, url in result:
        print(f"{link_id}: {url}")


if __name__ == "__main__":
    main()
