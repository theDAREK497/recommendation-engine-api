from fastapi import FastAPI
from app.qdrant_utils import init_qdrant, search_properties, model
from app.healthcheck import wait_for_qdrant
from redis import Redis
import json
import os
from qdrant_client.models import Filter, FieldCondition, Range
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Инициализация Redis
redis = Redis(host=os.getenv("REDIS_HOST", "redis"), port=int(os.getenv("REDIS_PORT", 6379)), decode_responses=True)

@app.on_event("startup")
async def startup_event():
    wait_for_qdrant()
    init_qdrant()
    # Инструментируем приложение для сбора метрик Prometheus
    Instrumentator().instrument(app).expose(app)

@app.get("/recommend")
async def recommend(
    query: str,
    min_price: int = None,
    max_price: int = None,
    rooms: int = None
):
    # Проверяем кэш
    cache_key = f"recommend:{query}:{min_price}:{max_price}:{rooms}"
    cached = redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Преобразуем запрос в вектор
    vector = model.encode(query).tolist()
    
    # Создаем фильтр для Qdrant
    filter_conditions = []
    
    if min_price is not None or max_price is not None:
        filter_conditions.append(
            FieldCondition(
                key="payload.price",
                range=Range(
                    gte=min_price,
                    lte=max_price
                )
            )
        )
    
    if rooms is not None:
        filter_conditions.append(
            FieldCondition(
                key="payload.rooms",
                match={"value": rooms}
            )
        )
    
    qdrant_filter = Filter(must=filter_conditions) if filter_conditions else None
    
    # Выполняем поиск
    search_result = search_properties(vector, filter=qdrant_filter, limit=5)
    
    # Форматируем ответ
    response = {
        "query": query,
        "results": [
            {
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload
            }
            for hit in search_result
        ]
    }
    
    # Кэшируем на 5 минут
    redis.setex(cache_key, 300, json.dumps(response))
    return response