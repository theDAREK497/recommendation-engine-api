from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import json
import os

QDRANT_URL = "http://qdrant:6333"
COLLECTION_NAME = "real_estate"
client = QdrantClient(host="qdrant", port=6333)

def init_qdrant():
    # Создаем коллекцию если нужно
    try:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
        load_sample_data()
    except Exception:
        pass  # Коллекция уже существует

def load_sample_data():
    # Тестовые данные
    properties = [
        {"id": 1, "description": "2-комн. квартира в Москве", "price": 15000000},
        {"id": 2, "description": "3-комн. квартира в новостройке", "price": 20000000},
        {"id": 3, "description": "1-комн. квартира у метро", "price": 9000000}
    ]
    
    # Добавляем в Qdrant
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            {
                "id": prop["id"],
                "vector": model.encode(prop["description"]).tolist(),
                "payload": prop
            } for prop in properties
        ]
    )

def search_properties(vector, limit=3):
    search_result = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=vector,
        limit=limit
    )
    return [hit.payload for hit in search_result]