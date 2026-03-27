
import os
import sys
import io
import argparse
import shutil
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
ARCHIVE_PATH = os.path.join(os.path.dirname(__file__), '..', 'archive')

# --- Data Ingestion and Processing Functions ---
def load_and_archive_documents(directory_path):
    documents = []
    processed_files = []  # Keep track of files to move
    print(f"Searching for documents in: {os.path.abspath(directory_path)}")

    if not os.path.exists(directory_path):
        print(f"Error: Directory not found at {os.path.abspath(directory_path)}")
        return []

    if not os.path.exists(ARCHIVE_PATH):
        os.makedirs(ARCHIVE_PATH)

    # First, load all documents
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if not os.path.isfile(file_path):
            continue
        try:
            if filename.endswith(".pdf"): loader = PyPDFLoader(file_path)
            elif filename.endswith(".docx"): loader = Docx2txtLoader(file_path)
            elif filename.endswith(".txt"): loader = TextLoader(file_path, encoding='utf-8')
            else: continue

            documents.extend(loader.load())
            processed_files.append((file_path, filename))
            print(f"Successfully loaded {filename}")
        except Exception as e:
            print(f"Failed to load {filename}: {e}")

    # After loading, move the processed files
    for file_path, filename in processed_files:
        try:
            shutil.move(file_path, os.path.join(ARCHIVE_PATH, filename))
            print(f"Archived {filename}")
        except Exception as e:
            print(f"Failed to archive {filename}: {e}")

    return documents

def split_documents_into_chunks(documents):
    print("\nSplitting documents...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    document_chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(document_chunks)} chunks.")
    return document_chunks

def update_vector_store(chunks):
    print("\nUpdating vector store...")
    ollama_embeddings = OllamaEmbeddings(model="mxbai-embed-large")

    if os.path.exists(VECTOR_STORE_PATH) and os.path.exists(os.path.join(VECTOR_STORE_PATH, "index.faiss")):
        # Load existing vector store
        print("Loading existing vector store...")
        vector_store = FAISS.load_local(VECTOR_STORE_PATH, ollama_embeddings, allow_dangerous_deserialization=True)
        # Add new chunks to the existing store
        print(f"Adding {len(chunks)} new chunks to the vector store...")
        vector_store.add_documents(chunks)
    else:
        # Create a new vector store
        print("Creating a new vector store...")
        if not os.path.exists(VECTOR_STORE_PATH):
            os.makedirs(VECTOR_STORE_PATH)
        vector_store = FAISS.from_documents(chunks, ollama_embeddings)

    # Save the updated vector store
    vector_store.save_local(VECTOR_STORE_PATH)
    print(f"Saved vector store at: {VECTOR_STORE_PATH}")

# --- RAG Query Functions ---
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def get_rag_chain():
    """Loads the vector store and returns a runnable RAG chain."""
    print("Loading vector store and creating RAG chain...")
    ollama_embeddings = OllamaEmbeddings(model="mxbai-embed-large")
    vector_store = FAISS.load_local(VECTOR_STORE_PATH, ollama_embeddings, allow_dangerous_deserialization=True)
    retriever = vector_store.as_retriever()

    prompt = ChatPromptTemplate.from_template('''
    Answer the question based only on the following context:

    {context}

    Question: {question}
    ''')

    llm = ChatOllama(model="gpt-oss:20b-cloud")

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    print("RAG chain created successfully.")
    return rag_chain

def main():
    parser = argparse.ArgumentParser(description="RAG Application: Ingest documents or ask questions.")
    parser.add_argument("--ingest", action="store_true", help="Ingest documents and create the vector store.")
    parser.add_argument("--query", type=str, help="Ask a single question to the RAG system.")
    parser.add_argument("--chat", action="store_true", help="Start an interactive chat session with the RAG system.")
    args = parser.parse_args()

    if args.ingest:
        print("--- Starting Document Ingestion Pipeline ---")
        loaded_docs = load_and_archive_documents(DOCUMENTS_PATH)
        if loaded_docs:
            doc_chunks = split_documents_into_chunks(loaded_docs)
            update_vector_store(doc_chunks)
            print("\n--- Ingestion Complete! ---")
        else:
            print("\nNo new documents found to ingest.")

    elif args.query:
        print(f"--- Querying RAG System with: '{args.query}' ---")
        if not os.path.exists(VECTOR_STORE_PATH):
            print("Error: Vector store not found. Please run with --ingest first.")
            return

        rag_chain = get_rag_chain()
        print("Invoking chain...")
        answer = rag_chain.invoke(args.query)

        print("\n--- Answer ---")
        print(answer)

    elif args.chat:
        print("--- Starting Interactive Chat Session ---")
        if not os.path.exists(VECTOR_STORE_PATH):
            print("Error: Vector store not found. Please run with --ingest first.")
            return

        rag_chain = get_rag_chain()
        print("Enter 'exit' or 'quit' to end the session.")

        while True:
            try:
                question = input("\nQuestion: ")
                if question.lower() in ['exit', 'quit']:
                    break

                print("...thinking...")
                answer = rag_chain.invoke(question)
                print("\n--- Answer ---")
                print(answer)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                break
        print("\n--- Chat Session Ended ---")

    else:
        print("No action specified. Use --ingest, --query 'Your question', or --chat.")

if __name__ == "__main__":
    main()
