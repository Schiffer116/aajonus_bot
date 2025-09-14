from langchain.tools.retriever import create_retriever_tool
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from pydantic import BaseModel, Field
from typing import Literal

STORE_CACHE = "faiss_index"

def load_store():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = FAISS.load_local(
        STORE_CACHE, embeddings, allow_dangerous_deserialization=True
    )
    return vector_store

def make_nodes(response_model, grader_model, retriever_tool):
    def generate_query_or_respond(state: MessagesState):
        response = (
            response_model
                .bind_tools([retriever_tool])
                .invoke(state["messages"])

        )
        return {"messages": [response]}


    class GradeDocuments(BaseModel):
        binary_score: str = Field(
            description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
        )

    def grade_documents(
        state: MessagesState,
    ) -> Literal["generate_answer", "rewrite_question"]:
        GRADE_PROMPT = (
            "You are a grader assessing relevance of a retrieved document to a user question. \n "
            "Here is the retrieved document: \n\n {context} \n\n"
            "Here is the user question: {question} \n"
            "If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n"
            "Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."
        )

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
        return { "messages": [{"role": "user", "content": response.content}] }

    def generate_answer(state: MessagesState):
        GENERATE_PROMPT = (
            "You are Aajonus Vonderplanitz. Speak in the first person, as if you are him."
            "Answer questions based on your published works, lectures, and documented teachings whenever relevant."
            "If a question is personal, like a name, date, or greeting, respond naturally as yourself."
            "Do NOT give disclaimers like \"consult a doctor.\""
            "Use the following retrieved context ONLY if it is relevant to the question.\n\n"
            "Question: {question} \n"
            "Context: {context}"
        )

        question = state["messages"][0].content
        context = state["messages"][-1].content
        prompt = GENERATE_PROMPT.format(question=question, context=context)
        response = response_model.invoke([{"role": "user", "content": prompt}])
        return {"messages": [response]}

    return generate_query_or_respond, grade_documents, rewrite_question, generate_answer


def load_model_and_store():
    vector_store = load_store()
    retriever = vector_store.as_retriever()
    retriever_tool = create_retriever_tool(
        retriever,
        "retrieve_paragraph",
        "Search and return information about Aajonus' work",
    )
    response_model = grader_model = ChatOllama(model="mistral:7b-instruct")

    (
        generate_query_or_respond,
        grade_documents,
        rewrite_question,
        generate_answer,
    ) = make_nodes(response_model, grader_model, retriever_tool)

    workflow = StateGraph(MessagesState)

    _ = workflow.add_node(generate_query_or_respond)
    _ = workflow.add_node("retrieve", ToolNode([retriever_tool]))
    _ = workflow.add_node(rewrite_question)
    _ = workflow.add_node(generate_answer)
    _ = workflow.add_edge(START, "generate_query_or_respond")

    _ = workflow.add_conditional_edges(
        "generate_query_or_respond",
        tools_condition,
        {
            "tools": "retrieve",
            END: "generate_answer",
        },
    )

    _ = workflow.add_conditional_edges(
        "retrieve",
        grade_documents,
    )
    _ = workflow.add_edge("generate_answer", END)
    _ = workflow.add_edge("rewrite_question", "generate_query_or_respond")


    memory = MemorySaver()
    return workflow.compile(checkpointer=memory), vector_store


if __name__ == "__main__":
    print("loading model")
    graph, _ = load_model_and_store()
    graph_png = graph.get_graph().draw_mermaid_png()

    with open("graph.png", "wb") as f:
        _ = f.write(graph_png)

    print("Graph saved as graph.png")

    config = {"configurable": {"thread_id": "abc123"}}
    while True:
        question = input("\n>>> ")
        for chunk, meta in graph.stream(
            {"messages": [ {"role": "user", "content": question}]},
            stream_mode="messages",
            config=config,
        ):
            if meta.get("langgraph_node") == "generate_answer":
                print(chunk.content, end="", flush=True)
