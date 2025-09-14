import pickle

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

DOCS_CACHE = "docs.pkl"
STORE_CACHE = "faiss_index"

with open(DOCS_CACHE, "rb") as f:
    docs = pickle.load(f)

    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n", ".", "!", "?"],
        keep_separator='end',
        chunk_size=500,
        chunk_overlap=100,
    )

    all_splits = text_splitter.split_documents(docs)
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        show_progress=True,
    )

    vector_store = FAISS.from_documents(all_splits, embeddings)
    vector_store.save_local(STORE_CACHE)
