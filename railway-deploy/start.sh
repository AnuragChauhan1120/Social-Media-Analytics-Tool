#!/bin/bash
echo "Starting FastAPI backend..."
uvicorn scraper_api:app --host 0.0.0.0 --port 8000 &

sleep 2

echo "Starting Streamlit frontend..."
streamlit run app.py --server.address 0.0.0.0 --server.port 8080
