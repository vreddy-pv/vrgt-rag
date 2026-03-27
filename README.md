# VRGT-RAG: A Local RAG Application

This project is a complete, locally-run Retrieval-Augmented Generation (RAG) application built using Python and Ollama.

It can ingest a directory of documents (PDFs, DOCX, TXT) and create a searchable vector database. Users can then ask questions through an interactive web UI or a command-line interface, and the application will retrieve relevant information from the documents to generate a comprehensive answer.

## Key Features

- **Web UI**: An intuitive, beautiful chat interface built with Streamlit.
- **Automated Ingestion**: A file watcher service that automatically processes new documents.
- **Incremental Updates**: New documents are added to the vector store without re-processing existing ones.
- **Error Handling**: Failed documents are automatically moved to an `error` directory.
- **Local & Private**: All processing happens locally, keeping your data secure.

## Key Technologies

- **Backend**: Python, FastAPI
- **Frontend**: Streamlit
- **File Watcher**: Watchdog
- **LLM/Embeddings**: Ollama (using `mxbai-embed-large` for embeddings and `gpt-oss:20b-cloud` for generation)
- **Orchestration**: LangChain
- **Vector Store**: FAISS

## How to Use

### 1. Automated Ingestion (Recommended)

The easiest way to use the application is with the automated file watcher.

1.  **Start the Watcher**:
    ```bash
    python watcher.py
    ```
2.  **Add Documents**: Simply drop your `.pdf`, `.docx`, or `.txt` files into the `../documents` directory. The watcher will automatically detect, process, and archive them.
    - Successfully processed files are moved to the `../archive` directory.
    - Failed files are moved to the `../error` directory.

### 2. Manual Ingestion

You can also process documents manually.

1.  **Place Documents**: Add your files to the `../documents` directory.
2.  **Run Ingestion**:
    ```bash
    python main.py --ingest
    ```

### 3. Chat with your Documents (Web UI)

1.  **Start the Backend API**:
    ```bash
    uvicorn app:app --reload
    ```
2.  **Start the Frontend UI** (in a separate terminal):
    ```bash
    streamlit run ui.py
    ```
    A browser window will open with the chat interface.

### 4. Query from the Command Line

- **Interactive Chat**:
  ```bash
  python main.py --chat
  ```
- **Single Question**:
  ```bash
  python main.py --query "Your question here"
  ```
