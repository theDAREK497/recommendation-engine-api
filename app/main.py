from fastapi import FastAPI
from app.qdrant_utils import init_qdrant, search_properties, model
from app.healthcheck import wait_for_qdrant
import os

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    wait_for_qdrant()
    init_qdrant()

@app.get("/recommend")
async def recommend(query: str):
    vector = model.encode(query).tolist()
    search_result = search_properties(vector)
    
    return {
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