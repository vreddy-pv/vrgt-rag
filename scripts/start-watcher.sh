#!/bin/bash
# Starts the RAG file watcher service.

echo "Starting RAG file watcher..."
python -m src.watcher --docs-path ../documents --archive-path ../archive --error-path ../error
