import pickle
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from chat import load_store

import warnings

warnings.filterwarnings("ignore", message="Relevance scores must be between 0 and 1")

app = FastAPI()
docs = pickle.load(open("docs.pkl", "rb"))
vector_store = load_store()


app.mount("/imgs", StaticFiles(directory="public/imgs"), name="public_imgs")

@app.get("/api/documents")
def get_articles(query: str | None = None) -> list[dict[str, str | int]]:
    if query is None:
        all_docs = list(map(lambda doc: {
            "id": int(doc.metadata["id"]),
            "name": str(doc.metadata["name"]),
            "category": str(doc.metadata["category"]),
        }, docs))

        return all_docs

    result = vector_store.similarity_search_with_relevance_scores(
        query,
        k=2**10,
        score_threshold=0.2
    )
    if not result:
        return []

    matches, _ = zip(*result)
    matches = list(map(lambda doc: {
        "id": int(doc.metadata["id"]),
        "name": str(doc.metadata["name"]),
        "category": str(doc.metadata["category"]),
        "chunk": str(doc.page_content),
    }, matches))

    return matches


@app.get("/api/documents/{id}")
def get_articles_content(id: int) -> dict[str, str]:
    return {
        "name": str(docs[id].metadata["name"]),
        "content": str(docs[id].page_content),
    }
