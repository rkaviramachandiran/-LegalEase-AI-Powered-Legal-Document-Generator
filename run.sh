#!/bin/bash
set -e

echo "Starting LegalEase FastAPI backend..."
uvicorn legalEaseAPI.main:app --reload &
BACKEND_PID=$!

trap "kill $BACKEND_PID" EXIT

echo "Starting LegalEase Streamlit frontend..."
streamlit run frontend/app.py
