import aiohttp
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import re
import asyncio

class Searcher():
    """Sorry gak pake requests soalnya uah terbiasa sama aiohttp :)"""
    def __init__(self, query, page: int = 1) -> None:
        self.query = query
        self.base_url = "https://modulgame.com"
        self.page = page
        self.headers = {
            'User-Agent': UserAgent().random
        }
        self.RED = "\033[31m"
        self.GREEN = "\033[32m"
        self.RESET = "\033[0m"

    def _reset_useragent(self):
        self.headers['User-Agent'] = UserAgent().random

    async def fetch_page(self, session, page):
        url = f"{self.base_url}/page/{page}/?s={self.query}" if page > 1 else f"{self.base_url}/?s={self.query}"
        async with session.get(url, headers=self.headers) as response:
            self._reset_useragent()
            return await response.text()

    async def parse_page(self, html_response):
        soup = BeautifulSoup(html_response, 'html.parser')
        post_listing = soup.find('div', class_='post-listing archive-box')
        if not post_listing:
            return None, []

        articles = post_listing.find_all('article', class_='item-list')
        results = []
        for article in articles:
            title_tag = article.find('h2', class_='post-box-title')
            title = title_tag.text.strip() if title_tag else "No title"

            url_tag = title_tag.find('a') if title_tag else None
            post_url = url_tag['href'] if url_tag else "No URL"

            categories = article.find('span', class_='post-cats')
            category_links = categories.find_all('a') if categories else []
            category_list = [cat.text.strip() for cat in category_links]

            description_tag = article.find('div', class_='entry')
            description = description_tag.find('p').text.strip() if description_tag else "No description"

            results.append({
                "title": title,
                "url": post_url,
                "categories": category_list,
                "description": description
            })

        pagination = soup.find('div', class_='pagination')
        total_pages = 1
        if pagination:
            pages_text = pagination.find('span', class_='pages').text
            match = re.search(r'Page \d+ of (\d+)', pages_text)
            if match:
                total_pages = int(match.group(1))

        return total_pages, results

    async def search(self):
        async with aiohttp.ClientSession() as session:
            current_page = 1
            total_pages = 1
            all_results = []
            print("─" * 50 + " Bjorki199 " + "─" * 50)
            while current_page <= total_pages:
                print(f"{self.GREEN}Fetching page {current_page}...{self.RESET}")
                html_response = await self.fetch_page(session, current_page)
                total_pages, results = await self.parse_page(html_response)

                if not results:
                    print(f"{self.RED}No results found for query: {self.query}{self.RESET}")
                    break

                all_results.extend(results)
                current_page += 1
            print(f"{self.GREEN}Num of result: {len(all_results)}{self.RESET}")
            print("─" * 50 + " jorki199 " + "─" * 50)

            for result in all_results:
                print(f"{self.GREEN}Title: {self.RESET}{result['title']}")
                print(f"{self.GREEN}URL: {self.RESET}{result['url']}")
                print(f"{self.GREEN}Categories: {self.RESET}{', '.join(result['categories'])}")
                print(f"{self.GREEN}Description: {self.RESET}{result['description']}\n")
            print("─" * 50 + " Bjorki199 " + "─" * 50)
searcher = Searcher('resident evil')
asyncio.run(searcher.search())