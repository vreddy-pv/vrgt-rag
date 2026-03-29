import os
import sys
import io
import argparse
import shutil
from .core import process_file, VECTOR_STORE_PATH, PROJECT_ROOT
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


def ingest_and_archive_documents(docs_path, archive_path, error_path):
    """Processes all files in a directory and archives them."""
    print(f"Searching for documents in: {os.path.abspath(docs_path)}")
    if not os.path.exists(docs_path):
        print(f"Error: Documents directory not found at {os.path.abspath(docs_path)}")
        return

    if not os.path.exists(archive_path):
        os.makedirs(archive_path)
    if not os.path.exists(error_path):
        os.makedirs(error_path)

    for filename in os.listdir(docs_path):
        file_path = os.path.join(docs_path, filename)
        if not os.path.isfile(file_path):
            continue

        success = process_file(file_path)

        # Move the file after processing
        if success:
            destination = os.path.join(archive_path, filename)
            print(f"Archiving {filename} to {destination}")
            shutil.move(file_path, destination)
        else:
            destination = os.path.join(error_path, filename)
            print(f"Moving failed file {filename} to {destination}")
            shutil.move(file_path, destination)

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
    # Define the parent directory of the project root
    parent_dir = os.path.abspath(os.path.join(PROJECT_ROOT, os.pardir))

    parser = argparse.ArgumentParser(description="RAG Application: Ingest documents or ask questions.")
    parser.add_argument("--ingest", action="store_true", help="Ingest documents and create the vector store.")
    parser.add_argument("--query", type=str, help="Ask a single question to the RAG system.")
    parser.add_argument("--chat", action="store_true", help="Start an interactive chat session with the RAG system.")
    parser.add_argument("--docs-path", type=str, default=os.path.join(parent_dir, 'documents'), help="Path to the documents directory.")
    parser.add_argument("--archive-path", type=str, default=os.path.join(parent_dir, 'archive'), help="Path to the archive directory.")
    parser.add_argument("--error-path", type=str, default=os.path.join(parent_dir, 'error'), help="Path to the error directory.")

    args = parser.parse_args()

    if args.ingest:
        print("--- Starting Document Ingestion Pipeline ---")
        ingest_and_archive_documents(args.docs_path, args.archive_path, args.error_path)
        print("\n--- Ingestion Complete! ---")

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
