import pickle

from bs4 import Tag, BeautifulSoup
from bs4.filter import SoupStrainer
import requests
from urllib.parse import urljoin

from langchain_community.document_loaders import WebBaseLoader

CACHE_FILE = "docs.pkl"

BASE_URL = "https://aajonus.net"
response = requests.get(BASE_URL)
soup = BeautifulSoup(response.text, "html.parser")

urls = []
for a in soup.find_all("a"):
    if isinstance(a, Tag):
        urls.append(urljoin(BASE_URL, str(a["href"])))

loader = WebBaseLoader(
    web_paths=urls,
    bs_kwargs=dict(
        parse_only=SoupStrainer(
            class_=("content", "title")
        )
    ),
)
loader.requests_per_second = 5
docs = loader.aload()

with open(CACHE_FILE, "wb") as f:
    pickle.dump(docs, f)
