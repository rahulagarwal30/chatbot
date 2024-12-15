from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

mapping = {
    "mappings": {
        "properties": {
            "url": {"type": "keyword"},
            "content": {"type": "text"},
            "content_vector": {
                "type": "dense_vector",
                "dims": 384,  # Dimension of all-MiniLM-L6-v2 embeddings
                "index": True,
                "similarity": "cosine"
            }
        }
    }
}

# Create the index with the mapping
es.indices.create(index="url_content", body=mapping) 