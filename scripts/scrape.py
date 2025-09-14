import asyncio
import aiohttp
import aiofiles
import os
from tqdm.asyncio import tqdm_asyncio

from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin


CACHE_FILE = "docs.pkl"
DOCS_DIR = "docs"
BASE_URL = "https://aajonus.net"
CONCURRENCY = 20

async def fetch_and_save(
    session: aiohttp.ClientSession,
    sem: asyncio.Semaphore,
    url: str,
    i: int,
    category: str,
    name: str
):
    async with sem:
        async with session.get(url) as resp:
            html = await resp.text()
            category = category.replace("/", "-")
            filename = os.path.join(DOCS_DIR, f"{i:03d}_{category}_{name}.html")
            async with aiofiles.open(filename, "w") as f:  # async file write
                _ = await f.write(html)


async def scrape(urls: list[str], categories: list[str], names: list[str]):
    os.makedirs(DOCS_DIR, exist_ok=True)
    sem = asyncio.Semaphore(CONCURRENCY)

    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_and_save(session, sem, url, i, categories[i], names[i])
            for i, url in enumerate(urls)
        ]

        for f in tqdm_asyncio.as_completed(tasks, total=len(tasks)):
            await f


if __name__ == "__main__":
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)

    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, "html.parser")

    categories = list(map(lambda a: a.text, soup.select("span.category")))
    names = list(map(lambda a: a.text, soup.select("a.read-more")))
    urls = list(map(lambda a: urljoin(BASE_URL, str(a["href"])), soup.select("a.read-more")))

    asyncio.run(scrape(urls, categories, names))
