import os
import time
import requests
from qdrant_client import QdrantClient

def wait_for_qdrant():
    host = os.getenv("QDRANT_HOST", "qdrant")
    port = int(os.getenv("QDRANT_PORT", 6333))
    url = f"http://{host}:{port}"

    attempts = 0
    max_attempts = 10
    
    while attempts < max_attempts:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print("Qdrant is ready!")
                return True
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            pass
        
        print(f"Waiting for Qdrant... ({attempts+1}/{max_attempts})")
        time.sleep(5)
        attempts += 1
    
    raise RuntimeError("Qdrant did not become ready in time")