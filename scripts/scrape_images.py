import os
import requests
import bs4
import asyncio
import aiohttp
from tqdm.asyncio import tqdm_asyncio

BASE_URL = "https://aajonus.net/imgs"
IMG_DIR = "public/imgs"
CONCURRENCY = 20

async def download_img(session: aiohttp.ClientSession, sem: asyncio.Semaphore, img: str):
    async with sem:
        async with session.get(f"{BASE_URL}/{img}") as resp:
            with open(os.path.join(IMG_DIR, img), "wb") as f:
                _ = f.write(await resp.content.read())

async def main():
    if not os.path.exists(IMG_DIR):
        os.makedirs(IMG_DIR)

    body = requests.get(BASE_URL).text
    imgs = []
    for a in bs4.BeautifulSoup(body, "html.parser").table.find_all("a"):
        if img := a.get("href"):
            ext = ("png", "jpg")
            if img.split(".")[-1] in ext:
                imgs.append(img)

    sem = asyncio.Semaphore(CONCURRENCY)
    async with aiohttp.ClientSession() as session:
        tasks = [
            asyncio.create_task(download_img(session, sem, img))
            for img in imgs
        ]

        for f in tqdm_asyncio.as_completed(tasks, total=len(tasks)):
            await f

if __name__ == "__main__":
    asyncio.run(main())
