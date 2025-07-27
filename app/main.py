from fastapi import FastAPI
from sentence_transformers import SentenceTransformer
from app.qdrant_utils import init_qdrant, search_properties

app = FastAPI()
model = SentenceTransformer('all-MiniLM-L6-v2')  # Легкая модель для эмбеддингов

# Инициализация при старте
@app.on_event("startup")
async def startup_event():
    init_qdrant()

@app.get("/recommend")
async def recommend(query: str):
    # Преобразуем запрос в вектор
    vector = model.encode(query).tolist()
    
    # Ищем похожие объекты
    results = search_properties(vector)
    return {"query": query, "results": results}