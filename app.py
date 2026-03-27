
import os
import sys
import io
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Force stdout to use UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Define paths
VECTOR_STORE_PATH = os.path.join(os.path.dirname(__file__), 'vector_store')

app = FastAPI()

# --- RAG Chain Initialization ---
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def get_rag_chain():
    """Loads the vector store and returns a runnable RAG chain."""
    print("Loading vector store and creating RAG chain...")
    ollama_embeddings = OllamaEmbeddings(model="mxbai-embed-large")
    if not os.path.exists(VECTOR_STORE_PATH):
        raise FileNotFoundError(f"Vector store not found at {VECTOR_STORE_PATH}. Please run the ingestion script first.")

    vector_store = FAISS.load_local(VECTOR_STORE_PATH, ollama_embeddings, allow_dangerous_deserialization=True)
    retriever = vector_store.as_retriever()

    prompt = ChatPromptTemplate.from_template("""
    Answer the question based only on the following context:

    {context}

    Question: {question}
    """)

    llm = ChatOllama(model="gpt-oss:20b-cloud")

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    print("RAG chain created successfully.")
    return rag_chain

rag_chain = get_rag_chain()

# --- API Endpoint ---
class QueryRequest(BaseModel):
    question: str

@app.post("/query/")
async def query_rag(request: QueryRequest):
    """Receives a question, queries the RAG chain, and returns the answer."""
    print(f"Received query: {request.question}")
    answer = rag_chain.invoke(request.question)
    print(f"Generated answer: {answer}")
    return {"answer": answer}

@app.get("/")
def read_root():
    return {"message": "RAG API is running. POST to /query/ with a 'question' to get an answer."}
