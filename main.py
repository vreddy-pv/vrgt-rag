
import os
import sys
import io
import argparse
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Force stdout to use UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Define paths
DOCUMENTS_PATH = os.path.join(os.path.dirname(__file__), '..', 'documents')
VECTOR_STORE_PATH = os.path.join(os.path.dirname(__file__), 'vector_store')

# --- Data Ingestion and Processing Functions ---
def load_documents_from_directory(directory_path):
    # This function is correct and remains unchanged.
    documents = []
    print(f"Searching for documents in: {os.path.abspath(directory_path)}")
    if not os.path.exists(directory_path):
        print(f"Error: Directory not found at {os.path.abspath(directory_path)}")
        return []
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        try:
            if filename.endswith(".pdf"): loader = PyPDFLoader(file_path)
            elif filename.endswith(".docx"): loader = Docx2txtLoader(file_path)
            elif filename.endswith(".txt"): loader = TextLoader(file_path, encoding='utf-8')
            else: continue
            documents.extend(loader.load())
        except Exception as e: print(f"Failed to load {filename}: {e}")
    return documents

def split_documents_into_chunks(documents):
    # This function is correct and remains unchanged.
    print("\nSplitting documents...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    document_chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(document_chunks)} chunks.")
    return document_chunks

def create_and_save_vector_store(chunks):
    # This function is correct and remains unchanged.
    print("\nCreating embeddings with 'nomic-embed-text' and building vector store...")
    ollama_embeddings = OllamaEmbeddings(model="mxbai-embed-large")
    vector_store = FAISS.from_documents(chunks, ollama_embeddings)
    if not os.path.exists(VECTOR_STORE_PATH): os.makedirs(VECTOR_STORE_PATH)
    vector_store.save_local(VECTOR_STORE_PATH)
    print(f"Saved vector store at: {VECTOR_STORE_PATH}")

# --- RAG Query Functions ---
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def main():
    parser = argparse.ArgumentParser(description="RAG Application: Ingest documents or ask questions.")
    parser.add_argument("--ingest", action="store_true", help="Ingest documents and create the vector store.")
    parser.add_argument("--query", type=str, help="Ask a question to the RAG system.")
    args = parser.parse_args()

    if args.ingest:
        print("--- Starting Document Ingestion Pipeline ---")
        loaded_docs = load_documents_from_directory(DOCUMENTS_PATH)
        if loaded_docs:
            doc_chunks = split_documents_into_chunks(loaded_docs)
            create_and_save_vector_store(doc_chunks)
            print("\n--- Ingestion Complete! ---")
        else:
            print("\nNo documents found to ingest.")

    elif args.query:
        print(f"--- Querying RAG System with: '{args.query}' ---")
        if not os.path.exists(VECTOR_STORE_PATH):
            print("Error: Vector store not found. Please run with --ingest first.")
            return

        # Load the vector store and create the RAG chain
        print("Loading vector store...")
        ollama_embeddings = OllamaEmbeddings(model="mxbai-embed-large")
        vector_store = FAISS.load_local(VECTOR_STORE_PATH, ollama_embeddings, allow_dangerous_deserialization=True)
        retriever = vector_store.as_retriever()

        # Define the prompt template
        prompt = ChatPromptTemplate.from_template("""
        Answer the question based only on the following context:

        {context}

        Question: {question}
        """)

        # Initialize the Ollama model for generation
        llm = ChatOllama(model="gpt-oss:20b-cloud")

        # Manually construct the chain
        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        print("RAG chain created. Invoking...")
        answer = rag_chain.invoke(args.query)

        print("\n--- Answer ---")
        print(answer)

    else:
        print("No action specified. Use --ingest to process documents or --query 'Your question' to ask a question.")

if __name__ == "__main__":
    main()
