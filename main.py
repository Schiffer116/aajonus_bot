from langchain import hub
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict

from langchain_ollama import OllamaLLM

from scripts.embed import load_store

print("Loading components...")
llm = OllamaLLM(model="gemma3:1b")
vector_store = load_store()

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
