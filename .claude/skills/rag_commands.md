---
name: RAG Application Commands
description: Commands for interacting with the RAG application.
type: reference
---

This skill provides the commands to interact with the RAG application in the `vrgt-rag` directory.

## Commands

- **Ingest Documents**: `python vrgt-rag/main.py --ingest`
  - This command processes the documents in the `documents` directory and creates/updates the vector store.

- **Query Documents**: `python vrgt-rag/main.py --query "Your question here"`
  - This command takes a question as a string and returns an answer based on the ingested documents.

- **Start Chat UI & API**: `uvicorn vrgt-rag.app:app --reload` and `streamlit run vrgt-rag/ui.py`
  - These commands start the backend API and the frontend UI for the interactive chat application.
