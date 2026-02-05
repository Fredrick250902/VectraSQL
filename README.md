## VectraSQL
VectraSQL is an intelligent invoice processing system that leverages a dual-database architecture to handle both unstructured and structured data efficiently. It combines MongoDB Atlas for vector-based semantic search (using embeddings for natural language queries) and MySQL for structured, relational data storage. The system uses Large Language Models (LLMs) for OCR text extraction from images, data structuring, and semantic retrieval, orchestrated via Apache Airflow for automated data synchronization.
This project uses:
- MongoDB Atlas for vector storage and semantic search
- MySQL for structured data warehousing
- Hugging Face embeddings (BAAI/bge-large-en-v1.5)
- Groq-hosted LLMs (LLaMA models) for OCR and generation
- Streamlit for the UI
- Apache Airflow for automated data synchronization
- Docker Compose for containerized deployment
___
🏗️ Project Structure
```text
vectraSQL/
│
├── dags/
│   └── atlas_to_mysql_sync.py  # Airflow DAG for MongoDB to MySQL sync
├── streamlit_app/
│   ├── app.py                  # Streamlit invoice processor UI
│   ├── dbclient.py             # MongoDB client utilities
│   ├── embeddings.py           # Hugging Face embedding generation
│   ├── extractor.py            # LLM-based text extraction from images
│   └── retriever.py            # Semantic search and answer generation
├── logs/                       # Airflow logs (generated)
├── myenv/                      # Virtual environment (optional)
├── docker-compose.yml          # Services for Airflow, MySQL, PostgreSQL
├── init.sql                    # MySQL table initialization
├── requirements.txt            # Python dependencies
├── .env                        # API keys and URIs (not committed)
```
___
🧠 Architecture Overview
```mermaid
graph TD;
    User([User]) --> UI[Streamlit UI];
    UI -->|Invoice Images| Extract[LLM OCR & Structuring];
    Extract -->|Raw Text + JSON| Embed[Hugging Face Embeddings];
    Embed -->|Vectors + Metadata| Mongo[(MongoDB Atlas)];
    Mongo -->|Unsynced Docs| Airflow[Airflow DAG];
    Airflow -->|Structured Data| MySQL[(MySQL)];
    UI -->|Query| Retrieve[Vector Search];
    Retrieve -->|Context| LLM[Groq LLaMA 3.3 70B];
    LLM -->|Answer| UI;
```
___
⚙️ Prerequisites
Make sure you have the following installed:
- Python 3.8+
- Docker & Docker Compose
- MongoDB Atlas account (with vector index configured)
- Hugging Face API key
- Groq API key
___
🔐 Environment Variables
Create a .env file in the project root:
- HF_API_KEY = your_huggingface_api_key
- GROQ_API_KEY = your_groq_api_key
