---
name: RAG Application Scripts
description: Scripts to run the RAG application components.
type: reference
---

This skill provides scripts to run the different parts of the RAG application.

## Scripts

- **Start RAG API**: `sh scripts/start-rag-api.sh`
  - Starts the backend FastAPI server.

- **Start RAG UI**: `sh scripts/start-rag-ui.sh`
  - Starts the frontend Streamlit UI.

- **Start RAG Watcher**: `sh scripts/start-rag-watcher.sh`
  - Starts the file watcher service for automated document ingestion.
