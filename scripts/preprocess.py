import re
import os
import sys
import pickle
from bs4.element import NavigableString
from tqdm import tqdm

from bs4 import BeautifulSoup
from bs4.filter import SoupStrainer

from langchain.docstore.document import Document

CACHE_FILE = "docs.pkl"
DOCS_DIR = "docs"
BASE_URL = "https://aajonus.net"
CONCURRENCY = 20


if __name__ == "__main__":
    if not os.path.exists(DOCS_DIR):
        print("Scraping docs...")
        sys.exit(1)

    docs = []
    only_body = SoupStrainer(class_=["content"])
    print("Cleaning data...")
    for i, file in enumerate(tqdm(sorted(os.listdir(DOCS_DIR)))):
        with open(os.path.join(DOCS_DIR, file), "r") as f:
            id, category, name = file.split("_")
            category = category.replace("-", "/")
            name = name.replace(".html", "")

            soup = BeautifulSoup(f.read(), "html.parser", parse_only=only_body)

            tag_to_clean = ("a", "p", "li", "blockquote")
            for node in soup.find_all(string=True):
                if isinstance(node, NavigableString) and node.parent.name in tag_to_clean:
                    if node.strip() == "":
                        _ = node.extract()
                        continue

                    newString = re.sub(r'\s+', " ", node.strip())
                    next_p = node.parent.find_next_sibling()
                    next_sibling = node.next_sibling

                    if (next_p and next_p.name == 'p' and not next_sibling) \
                    or (node.parent.name == 'a' and not node.parent.next_sibling):
                        newString += "\n\n"

                    _ = node.replace_with(newString)

            _ = soup.div.unwrap()
            for p in soup.find_all("p"):
                _ = p.unwrap()

            for node in soup.find_all(string=True):
                if isinstance(node, NavigableString) and node.strip() == "":
                    _ = node.extract()

            doc = Document(page_content=str(soup), metadata={
                "id": id,
                "name": name,
                "category": category,
            })
            docs.append(doc)

    with open(CACHE_FILE, "wb") as f:
        pickle.dump(docs, f)
