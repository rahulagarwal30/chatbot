# Minimalistic AI-powered chatbot

A robust web crawler designed to process sitemaps, extract content, and index it in Elasticsearch with additional AI-powered processing capabilities.

## Features

- Sitemap crawling and processing
- HTML content cleaning and extraction
- Elasticsearch integration for content indexing
- OpenAI integration for content processing
- Real-time updates via Pusher
- Dockerized deployment support

## Prerequisites

- Python 3.x
- Elasticsearch
- Docker (optional)
- OpenAI API access
- Pusher account

## Installation

1. Clone the repository:

git clone <repository-url>
cd chatbot

2. Create and activate a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

## Configuration

Configure the following environment variables in your `.env` file:

- `ELASTICSEARCH_HOST`: Your Elasticsearch host
- `ELASTICSEARCH_PORT`: Elasticsearch port
- `OPENAI_API_KEY`: Your OpenAI API key
- `PUSHER_APP_ID`: Pusher app ID
- `PUSHER_KEY`: Pusher key
- `PUSHER_SECRET`: Pusher secret
- `PUSHER_CLUSTER`: Pusher cluster

## Usage

1. Create Elasticsearch index:

```bash
python src/create_es_index.py
```

2. Run the crawler:

```bash
python src/run_crawler.py
```

## Docker Deployment

1. Build the Docker image:

```bash
docker build -t plivo-sitemap-crawler .
```

2. Run the container:

```bash
docker run --env-file .env plivo-sitemap-crawler
```

## Project Structure

```
├── src/
│   ├── config/
│   │   └── config.py         # Configuration management
│   ├── services/
│   │   ├── elasticsearch_service.py
│   │   ├── openai_service.py
│   │   └── pusher_service.py
│   ├── create_es_index.py    # Elasticsearch index creation
│   ├── file_operations.py    # File handling utilities
│   ├── html_cleaner.py      # HTML processing
│   ├── main.py              # Main application logic
│   ├── run_crawler.py       # Crawler entry point
│   ├── sitemap_crawler.py   # Sitemap processing
│   └── url_processor.py     # URL processing logic
├── .env.example
├── Dockerfile
├── requirements.txt
└── README.md
```

