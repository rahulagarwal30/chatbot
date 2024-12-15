#!/bin/bash

# Wait for Elasticsearch to be ready
echo "Waiting for Elasticsearch..."
until curl -s http://elasticsearch:9200 > /dev/null; do
    sleep 1
done
echo "Elasticsearch is ready!"

# Create Elasticsearch index
echo "Creating Elasticsearch index..."
python create_es_index.py
if [ $? -ne 0 ]; then
    echo "Failed to create Elasticsearch index"
    exit 1
fi

# Run crawler to populate index
echo "Running crawler to populate Elasticsearch..."
python crawler/run_crawler.py
if [ $? -ne 0 ]; then
    echo "Failed to run crawler"
    exit 1
fi

# Start the web server
echo "Starting web server..."
gunicorn --bind 0.0.0.0:5000 main:app