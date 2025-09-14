from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from langchain_ollama import ChatOllama
from langchain.tools.retriever import create_retriever_tool
from langgraph.graph import MessagesState

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition

from generate import generate_answer
from grade import grade_documents
from rewrite import rewrite_question

STORE_CACHE = "faiss_index"

def load_store():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = FAISS.load_local(
        STORE_CACHE, embeddings, allow_dangerous_deserialization=True
    )
    return vector_store

def generate_query_or_respond(state: MessagesState):
    """Call the model to generate a response based on the current state. Given
    the question, it will decide to retrieve using the retriever tool, or simply respond to the user.
    """
    response = (
        response_model
        .bind_tools([retriever_tool]).invoke(state["messages"])
    )
    return {"messages": [response]}

GRADE_PROMPT = (
    "You are a grader assessing relevance of a retrieved document to a user question. \n "
    "Here is the retrieved document: \n\n {context} \n\n"
    "Here is the user question: {question} \n"
    "If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n"
    "Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."
)

class GradeDocuments(BaseModel):
    """Grade documents using a binary score for relevance check."""

    binary_score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )


grader_model = Ollama("gemma3:1b")

def grade_documents(
    state: MessagesState,
) -> Literal["generate_answer", "rewrite_question"]:
    """Determine whether the retrieved documents are relevant to the question."""
    question = state["messages"][0].content
    context = state["messages"][-1].content

    prompt = GRADE_PROMPT.format(question=question, context=context)
    response = (
        grader_model
        .with_structured_output(GradeDocuments).invoke(
            [{"role": "user", "content": prompt}]
        )
    )
    score = response.binary_score

    if score == "yes":
        return "generate_answer"
    else:
        return "rewrite_question"

def rewrite_question(state: MessagesState):
    REWRITE_PROMPT = (
        "Look at the input and try to reason about the underlying semantic intent / meaning.\n"
        "Here is the initial question:"
        "\n ------- \n"
        "{question}"
        "\n ------- \n"
        "Formulate an improved question:"
    )

    messages = state["messages"]
    question = messages[0].content
    prompt = REWRITE_PROMPT.format(question=question)
    response = response_model.invoke([{"role": "user", "content": prompt}])
    return {"messages": [{"role": "user", "content": response.content}]}

def generate_answer(state: MessagesState):
    GENERATE_PROMPT = (
        "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer the question. "
            "If you don't know the answer, just say that you don't know. "
            "Use three sentences maximum and keep the answer concise.\n"
            "Question: {question} \n"
            "Context: {context}"
    )

    question = state["messages"][0].content
    context = state["messages"][-1].content
    prompt = GENERATE_PROMPT.format(question=question, context=context)
    response = response_model.invoke([{"role": "user", "content": prompt}])
    return {"messages": [response]}



if __name__ == "__main__":
    print("Loading components...")
    response_model = ChatOllama(model="mistral:7b-instruct")

    vector_store = load_store()
    retriever = vector_store.as_retriever()
    retriever_tool = create_retriever_tool(
        retriever,
        "retrieve_paragraph",
        "Search and return information about Aajonus' work",
    )

    workflow = StateGraph(MessagesState)

# Define the nodes we will cycle between
    _ = workflow.add_node(generate_query_or_respond)
    _ = workflow.add_node("retrieve", ToolNode([retriever_tool]))
    _ = workflow.add_node(rewrite_question)
    _ = workflow.add_node(generate_answer)

    _ = workflow.add_edge(START, "generate_query_or_respond")

# Decide whether to retrieve
    _ = workflow.add_conditional_edges(
        "generate_query_or_respond",
        # Assess LLM decision (call `retriever_tool` tool or respond to the user)
        tools_condition,
        {
            # Translate the condition outputs to nodes in our graph
            "tools": "retrieve",
            END: END,
        },
    )

# Edges taken after the `action` node is called.
    _ = workflow.add_conditional_edges(
        "retrieve",
        # Assess agent decision
        grade_documents,
    )
    _ = workflow.add_edge("generate_answer", END)
    _ = workflow.add_edge("rewrite_question", "generate_query_or_respond")

    graph = workflow.compile()
