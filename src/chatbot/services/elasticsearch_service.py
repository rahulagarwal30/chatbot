from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from src.config.config import ELASTICSEARCH_URL
import os

es_client = Elasticsearch(
    os.getenv('ELASTICSEARCH_URL', 'http://localhost:9200')
)

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def perform_vector_search(query):
    query_vector = model.encode(query)
    #print for debugging query vector
    #print(f"Query is: {query} ")

    results = es_client.search(index="url_content", body={
        "query": {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": """
                    double dotProduct = 0.0;
                    double magnitudeQuery = 0.0;
                    double magnitudeDoc = 0.0;
                    
                    for (int i = 0; i < params.query_vector.length; i++) {
                        dotProduct += params.query_vector[i] * doc['content_vector'][i];
                        magnitudeQuery += params.query_vector[i] * params.query_vector[i];
                        magnitudeDoc += doc['content_vector'][i] * doc['content_vector'][i];
                    }
                    
                    double magnitude = Math.sqrt(magnitudeQuery) * Math.sqrt(magnitudeDoc);
                    double cosine_similarity = magnitude != 0 ? dotProduct / magnitude : 0;
                    
                    return (cosine_similarity + 1.0) / 2.0;
                    """,
                    "params": {"query_vector": query_vector.tolist()}
                }
            }
        }
    })
    
    return results['hits']['hits'][:2] 

__all__ = ['perform_vector_search', 'es_client'] 