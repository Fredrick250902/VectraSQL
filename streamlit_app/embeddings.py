import os
import requests

def get_text_embedding(text: str):
    api_key = os.getenv("HF_API_KEY")
    if not api_key:
        raise ValueError("HF_API_KEY not found.")

    response = requests.post(
        "https://router.huggingface.co/hf-inference/models/BAAI/bge-large-en-v1.5/pipeline/feature-extraction",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"inputs": text}
    )
    embedding = response.json()
    if isinstance(embedding, list) and isinstance(embedding[0], list):
        embedding = embedding[0]
    return [float(x) for x in embedding]