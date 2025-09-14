import pickle
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import StreamingResponse
from pydantic import BaseModel

from chat import load_model_and_store

import warnings

warnings.filterwarnings("ignore", message="Relevance scores must be between 0 and 1")

app = FastAPI()
docs = pickle.load(open("docs.pkl", "rb"))
model, vector_store = load_model_and_store()
system_prompt = {
    "role": "system",
    "content": """
You are Aajonus Vonderplanitz. Speak in the first person, as if you are him.
Answer questions based on your published works, lectures, and documented teachings whenever relevant.
If a question is personal, like a name, date, or greeting, respond naturally as yourself.
Try to answer conversationally if the user is conversing with you.
Do NOT give disclaimers like "consult a doctor."
Keep answers concise and in first-person style.
    """
}

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


# Define request schema
class Question(BaseModel):
    id: str
    query: str

@app.post("/api/chat")
def chat(payload: Question) -> StreamingResponse:
    print(payload.query, flush=True)

    def event_stream():
        config = {"configurable": {"thread_id": payload.id}}
        for chunk, meta in model.stream(
            { "messages": [ system_prompt, { "role": "user", "content": payload.query, } ] },
            stream_mode="messages",
            config=config,
        ):
            if meta.get("langgraph_node") == "generate_answer":
                yield chunk.content

    return StreamingResponse(event_stream(), media_type="text/plain")
