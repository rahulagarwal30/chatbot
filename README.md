# Minimalistic AI-powered Chatbot

A robust web crawler and chatbot system that processes sitemaps, extracts content, indexes it in Elasticsearch, and provides AI-powered responses through a chat interface.

## Features

- Sitemap crawling and content extraction
- HTML content cleaning and processing
- Elasticsearch integration for vector search
- OpenAI integration for intelligent responses
- Real-time chat updates via Pusher
- Web interface for chat interactions

## Components

- **Crawler Module**: Handles sitemap processing and content extraction
- **Chatbot Module**: Manages the chat interface and AI responses
- **Elasticsearch**: Stores and indexes content with vector search capabilities
- **OpenAI Integration**: Provides intelligent responses to user queries
- **Pusher**: Enables real-time chat updates

## Architecture

```mermaid
graph TB
    subgraph CrawlerSystem[Crawler System]
        C[Crawler] --> HC[HTML Cleaner]
        HC --> FO[File Operations]
    end

    subgraph Storage
        FO --> ES[(Elasticsearch)]
    end

    subgraph ChatSystem[Chat System]
        UI[Web Interface] --> WS[Web Server]
        WS --> P[Pusher]
        P  --> UI
        WS --> ESS[Elasticsearch Service]
        WS --> OS[OpenAI Service]
        ESS --> ES
        OS --> GPT[OpenAI GPT]
    end

    classDef storageStyle fill:#e3f2fd,stroke:#2196f3,stroke-width:2px;
    classDef crawlerStyle fill:#f1f8e9,stroke:#689f38,stroke-width:2px;
    classDef chatStyle fill:#fff3e0,stroke:#ff9800,stroke-width:2px;

    class Storage storageStyle;
    class Crawler crawlerStyle;
    class ChatSystem chatStyle;
```

### User Chat Flow Sequence

```mermaid
sequenceDiagram
    actor EndUser
    participant ChatbotService
    participant Elasticsearch
    participant OpenAI
    participant Pusher

    EndUser->>ChatbotService: 1. Send query
    ChatbotService-->>EndUser: 2. Acknowledge query
    ChatbotService->>Elasticsearch: 3. Fetch top results for query
    Elasticsearch-->>ChatbotService: 4. Return top results
    ChatbotService->>OpenAI: 5. Send results to generate response
    OpenAI-->>ChatbotService: 6. Return generated response
    ChatbotService->>Pusher: 7. Send response to Pusher
    Pusher-->>EndUser: 8. Deliver response
```

### Crawler Flow Sequence

```mermaid
sequenceDiagram
    participant CronTrigger
    participant PlivoCrawler
    participant FileStorage
    participant Elasticsearch
    participant plivo.com

    CronTrigger->>PlivoCrawler: 1. Trigger crawl process
    PlivoCrawler->>plivo.com: 2. Fetch sitemap.xml
    plivo.com-->>PlivoCrawler: 3. Return sitemap.xml
    PlivoCrawler->>PlivoCrawler: 4. Filter out unnecessary URLs
    PlivoCrawler->>plivo.com: 5. Fetch website content for filtered URLs
    plivo.com-->>PlivoCrawler: 6. Return HTML content
    PlivoCrawler->>FileStorage: 7. Store cleaned and extracted data in files
    FileStorage-->>PlivoCrawler: 8. Confirm data stored
    PlivoCrawler->>Elasticsearch: 9. Index cleaned data (converted to vectors)
    Elasticsearch-->>PlivoCrawler: 10. Confirm data indexed
```
## Features

- Sitemap crawling and content extraction
- HTML content cleaning and processing
- Elasticsearch integration for vector search
- OpenAI integration for intelligent responses
- Real-time chat updates via Pusher
- Web interface for chat interactions

## Project Structure

```
src/
├── chatbot/                          # Chatbot module
│   ├── services/                     # Service integrations
│   │   ├── elasticsearch_service.py  # Vector search implementation
│   │   ├── openai_service.py        # GPT integration for responses
│   │   └── pusher_service.py        # Real-time messaging
│   └── static/                      # Web interface assets
│       ├── css/
│       │   └── styles.css           # Chat UI styling
│       ├── js/
│       │   └── chat.js             # Chat frontend logic
│       └── index.html              # Chat interface HTML
├── config/
│   └── config.py                   # Environment and app configuration
├── crawler/                        # Web crawler module
│   ├── file_operations.py         # Content storage and indexing
│   ├── html_cleaner.py           # HTML content extraction
│   ├── run_crawler.py            # Crawler entry point
│   ├── sitemap_crawler.py        # Sitemap XML processing
│   └── url_processor.py          # URL filtering and processing
├── create_es_index.py            # Elasticsearch index setup
└── main.py                       # Main Flask application
```

## Prerequisites

- Python 3.11+
- Elasticsearch 7.17+
- OpenAI API key
- Pusher account credentials

## Setup and Installation

1. Clone the repository:
```bash
git clone git@github.com:rahulagarwal30/chatbot.git
cd chatbot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy and configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Configuration

Configure the following in your `.env` file:
```
ELASTICSEARCH_URL=http://localhost:9200
OPENAI_API_KEY=your_openai_api_key
PUSHER_APP_ID=your_app_id
PUSHER_KEY=your_key
PUSHER_SECRET=your_secret
PUSHER_CLUSTER=your_cluster
```

## Running the Application

1. Start Elasticsearch locally

2. Create the index:
```bash
python src/create_es_index.py
```

3. Run the crawler to populate the index:
```bash
python src/crawler/run_crawler.py
```

4. Start the web server:
```bash
python src/main.py
```

5. Access the chat interface:
```
http://localhost:5001
```

## Environment Variables

- `ELASTICSEARCH_URL`: Elasticsearch connection URL
- `OPENAI_API_KEY`: OpenAI API key for GPT integration
- `PUSHER_APP_ID`: Pusher application ID
- `PUSHER_KEY`: Pusher key
- `PUSHER_SECRET`: Pusher secret key
- `PUSHER_CLUSTER`: Pusher cluster region

## Additional Configuration

- `FILE_AGE_DAYS`: Number of days before re-fetching URL content (default: 2)
- `MAX_URLS_TO_PROCESS`: Limit the number of URLs to process (-1 for all)

