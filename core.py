
import os
import sys
import io
import shutil
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

# Force stdout to use UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Define paths
VECTOR_STORE_PATH = os.path.join(os.path.dirname(__file__), 'vector_store')

def load_document(file_path):
    """Loads a single document using the appropriate loader."""
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith(".docx"):
        loader = Docx2txtLoader(file_path)
    elif file_path.endswith(".txt"):
        loader = TextLoader(file_path, encoding='utf-8')
    else:
        print(f"Unsupported file type: {file_path}")
        return None
    return loader.load()

def split_documents_into_chunks(documents):
    """Splits a list of documents into smaller chunks."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return text_splitter.split_documents(documents)

def update_vector_store(chunks):
    """Updates the FAISS vector store with new document chunks."""
    ollama_embeddings = OllamaEmbeddings(model="mxbai-embed-large")

    if os.path.exists(VECTOR_STORE_PATH) and os.path.exists(os.path.join(VECTOR_STORE_PATH, "index.faiss")):
        print("Loading existing vector store...")
        vector_store = FAISS.load_local(VECTOR_STORE_PATH, ollama_embeddings, allow_dangerous_deserialization=True)
        print(f"Adding {len(chunks)} new chunks...")
        vector_store.add_documents(chunks)
    else:
        print("Creating new vector store...")
        if not os.path.exists(VECTOR_STORE_PATH):
            os.makedirs(VECTOR_STORE_PATH)
        vector_store = FAISS.from_documents(chunks, ollama_embeddings)

    vector_store.save_local(VECTOR_STORE_PATH)
    print(f"Vector store updated and saved at: {VECTOR_STORE_PATH}")

def process_file(file_path):
    """Orchestrates the loading, splitting, and storing of a single file."""
    try:
        print(f"--- Processing file: {os.path.basename(file_path)} ---")
        documents = load_document(file_path)
        if not documents:
            return False

        chunks = split_documents_into_chunks(documents)
        if not chunks:
            print("Failed to split document into chunks.")
            return False

        update_vector_store(chunks)
        print("--- File processing complete ---")
        return True
    except Exception as e:
        print(f"An error occurred while processing {os.path.basename(file_path)}: {e}")
        return False
