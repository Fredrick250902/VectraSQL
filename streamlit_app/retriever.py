import os
from groq import Groq
from embeddings import get_text_embedding

def retrieve_and_answer(mongo_client, db_name, collection_name, query_text, top_k=4):
    db = mongo_client[db_name]
    collection = db[collection_name]
    query_embedding = get_text_embedding(query_text)
    
    pipeline = [
        {"$vectorSearch": {
            "index": "vector_index",
            "path": "embedding",
            "queryVector": query_embedding,
            "limit": top_k,
            "exact": True
        }},
        {"$project": {"_id": 0, "raw_text": 1, "score": {"$meta": "vectorSearchScore"}}}
    ]
    
    results = list(collection.aggregate(pipeline))
    context = "\n\n".join([doc.get("raw_text", "") for doc in results])
    
    client = Groq()
    prompt = f"Context: {context}\n\nQuestion: {query_text}"
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return {"documents": results, "answer": completion.choices[0].message.content}