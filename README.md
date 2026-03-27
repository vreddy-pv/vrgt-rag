# VRGT-RAG: A Local RAG Application

This project is a complete, locally-run Retrieval-Augmented Generation (RAG) application built using Python and Ollama.

It can ingest a directory of documents (PDFs, DOCX, TXT) and create a searchable vector database. Users can then ask questions, and the application will retrieve relevant information from the documents and use a local Large Language Model (LLM) to generate a comprehensive answer.

## Key Technologies

- **Backend**: Python
- **LLM/Embeddings**: Ollama (using `mxbai-embed-large` for embeddings and `gpt-oss:20b-cloud` for generation)
- **Orchestration**: LangChain
- **Vector Store**: FAISS

## How to Use

1.  **Place Documents**: Add your `.pdf`, `.docx`, or `.txt` files into the `../documents` directory.

2.  **Ingest Documents**: Run the ingestion pipeline to build the vector store. This must be done anytime new documents are added.
    ```bash
    .venv/Scripts/python.exe main.py --ingest
    ```

3.  **Query the System**: Ask questions about your documents.
    ```bash
    .venv/Scripts/python.exe main.py --query "Your question here"
    ```
