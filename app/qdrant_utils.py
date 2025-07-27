from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, Filter
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import json
import os

load_dotenv()

QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "real_estate")
MODEL_NAME = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
model = SentenceTransformer(MODEL_NAME)

def init_qdrant():
    collections = client.get_collections().collections
    collection_names = [c.name for c in collections]
    
    if COLLECTION_NAME not in collection_names:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE),
        )
        print(f"Collection '{COLLECTION_NAME}' created")
        load_sample_data()
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists")

def load_sample_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, '..', 'data', 'sample_data.json')
    
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            properties = json.load(f)
        print(f"Loaded data from {data_path}")
    except FileNotFoundError:
        print("Sample data file not found, using fallback data")
        properties = [
            {
                "id": 1, 
                "title": "2-комн. квартира в Москве",
                "description": "Просторная квартира в новом ЖК",
                "price": 15000000,
                "rooms": 2
            },
            {
                "id": 2, 
                "title": "3-комн. квартира в новостройке",
                "description": "Сдача в 2024 году",
                "price": 20000000,
                "rooms": 3
            }
        ]
    
    points = []
    for prop in properties:
        title = prop.get("title", "")
        description = prop.get("description", "")
        text = f"{title} {description}".strip()
        
        if not text:
            print(f"Skipping property {prop['id']} - no text for embedding")
            continue
            
        vector = model.encode(text).tolist()
        
        points.append({
            "id": prop["id"],
            "vector": vector,
            "payload": prop
        })
    
    if points:
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        print(f"Loaded {len(points)} sample properties")
    else:
        print("No properties loaded")

def search_properties(vector, filter: Filter = None, limit: int = 3):
    return client.search(
        collection_name=COLLECTION_NAME,
        query_vector=vector,
        query_filter=filter,
        limit=limit
    )