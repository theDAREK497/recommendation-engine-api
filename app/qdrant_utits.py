from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from sentence_transformers import SentenceTransformer
import json

QDRANT_URL = "http://qdrant:6333"
COLLECTION_NAME = "real_estate"
client = QdrantClient(host="qdrant", port=6333)
model = SentenceTransformer('all-MiniLM-L6-v2')  # Модель для эмбеддингов

def init_qdrant():
    # Создаем коллекцию если нужно
    collections = client.get_collections().collections
    collection_names = [c.name for c in collections]
    
    if COLLECTION_NAME not in collection_names:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
        load_sample_data()
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists")

def load_sample_data():
    # Путь к файлу с данными
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample_data.json')
    
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            properties = json.load(f)
    except FileNotFoundError:
        print("Sample data file not found, using fallback data")
        properties = [
            {"id": 1, "description": "2-комн. квартира в Москве", "price": 15000000},
            {"id": 2, "description": "3-комн. квартира в новостройке", "price": 20000000}
        ]
    
    # Преобразуем описания в векторы
    points = []
    for prop in properties:
        # Используем title + description для более точных эмбеддингов
        text = f"{prop['title']} {prop['description']}"
        vector = model.encode(text).tolist()
        
        points.append({
            "id": prop["id"],
            "vector": vector,
            "payload": prop  # сохраняем все данные в payload
        })
    
    # Добавляем в Qdrant
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    print(f"Loaded {len(points)} sample properties")

def search_properties(vector, limit=3):
    search_result = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=vector,
        limit=limit
    )
    return [hit.payload for hit in search_result]