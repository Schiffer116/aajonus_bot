import pickle

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import  OllamaEmbeddings

EMBED_CACHE = "embeddings.pkl"
DOCS_CACHE = "docs.pkl"

with open(DOCS_CACHE, "rb") as f:
    docs = pickle.load(f)
    print(docs[:10])

    # text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=200)
    # all_splits = text_splitter.split_documents(docs)
    # embeddings = OllamaEmbeddings(model="mxbai-embed-large")
    #
    # vectors = embeddings.embed_documents([doc.page_content for doc in all_splits[:500]])
    # embedded_docs = list(zip(all_splits, vectors))
    # with open(EMBED_CACHE, "wb") as f:
    #     pickle.dump(embedded_docs, f)
    #
    #
