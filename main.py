import pickle

import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain import hub
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict

from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_community.vectorstores import FAISS

print("Loading components...")
llm = OllamaLLM(model="gemma3:1b")
embeddings = OllamaEmbeddings(model="nomic-embed-text")

index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))

vector_store = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)

CACHE_FILE = "docs.pkl"

with open(CACHE_FILE, "rb") as f:
    print("Loading from cache...")
    docs = pickle.load(f)
    print("Splitting...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=200)
    all_splits = text_splitter.split_documents(docs)
    print("Adding to vector store...")
    _ = vector_store.add_documents(documents=all_splits[:1000])

print("Pulling prompt...")
prompt = hub.pull("rlm/rag-prompt")

class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}

def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response}

graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

response = graph.invoke({"question": "Are parasites dangerous ?"}) # type: ignore
print(f"Context: {response['context']}\n\n")
print(f"Answer: {response['answer']}")
print(response["answer"])
