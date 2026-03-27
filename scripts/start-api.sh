#!/bin/bash
# Starts the RAG backend API server.

echo "Starting RAG API server..."
uvicorn app:app --reload
