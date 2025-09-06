import pickle
import os

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS

DOCS_CACHE = "docs.pkl"
STORE_CACHE = "faiss_store.pkl"

def build_store():
    with open(DOCS_CACHE, "rb") as f:
        docs = pickle.load(f)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=200,
        )
        all_splits = text_splitter.split_documents(docs)
        embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        vector_store = FAISS.from_documents(all_splits, embeddings)

        with open(STORE_CACHE, "wb") as f:
            pickle.dump(vector_store, f)

        print(f"✅ Cached FAISS store with {len(all_splits)} chunks at {STORE_CACHE}")
        return vector_store


def load_store():
    if os.path.exists(STORE_CACHE):
        with open(STORE_CACHE, "rb") as f:
            vector_store = pickle.load(f)
        print(f"✅ Loaded FAISS store from {STORE_CACHE}")
        return vector_store
    else:
        return build_store()

if __name__ == "__main__":
    store = load_store()
