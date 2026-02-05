import streamlit as st
from dotenv import load_dotenv
import os
from extractor import extract_text_from_image
from embeddings import get_text_embedding
from dbclient import MongoVectorClient
from retriever import retrieve_and_answer

load_dotenv()
st.set_page_config(page_title="Dual-DB Ingestor", layout="wide")
st.title("Invoice Processor: Mongo (Vector) + MySQL (Structured)")

# Sidebar for Credentials
st.sidebar.header("MongoDB Atlas Connection")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
cluster_name = st.sidebar.text_input("Cluster Name")
cluster_id = st.sidebar.text_input("Cluster ID")
db_name = st.sidebar.text_input("DB Name")
col_name = st.sidebar.text_input("Collection Name")
v_index = st.sidebar.text_input("Vector Index Name")

mongo_client = None
if all([username, password, cluster_name, cluster_id, db_name, col_name, v_index]):
    try:
        mongo_client = MongoVectorClient(username, password, cluster_name, cluster_id, db_name, col_name, v_index)
        st.sidebar.success("Connected to MongoDB!")
    except Exception as e:
        st.sidebar.error(str(e))

# Ingestion
st.header("1. Ingest Invoices")
uploaded_files = st.file_uploader("Upload Invoices", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
meta_title = st.text_input("Project/Customer Title")

# --- INGESTION LOGIC ---
if st.button("Ingest Images to Database"):
    if not uploaded_files or not mongo_client:
        st.error("Missing files or MongoDB connection.")
    else:
        success_count = 0
        for f in uploaded_files:
            img_bytes = f.read()
            st.write(f"Processing: {f.name}")

            with st.spinner("Extracting & Structuring..."):
                try:
                    # 1. Get raw text and the cleaned JSON
                    raw_extracted, structured_json = extract_text_from_image(img_bytes)
                    
                    # 2. FIX ISSUE 1: Combine Title + Raw Text for the 'text' field
                    doc_title = meta_title or f.name
                    combined_text = f"Document Title: {doc_title}\n\n{raw_extracted}"
                    
                    # 3. Generate embedding on the COMBINED text
                    emb = get_text_embedding(combined_text)
                    
                    # 4. Insert Document
                    mongo_client.insert_document({
                        "title": doc_title,
                        "source": f.name,
                        "raw_text": combined_text,  # Combined text goes here
                        "contents": structured_json, # Strictly validated 4 fields
                        "embedding": emb,
                        "is_synced": False
                    })
                    success_count += 1
                except Exception as e:
                    st.error(f"Error processing {f.name}: {e}")
                    # import traceback
                    # st.expander("Show Traceback").code(traceback.format_exc())

        if success_count > 0:
            st.success(f"Successfully ingested {success_count} file(s).")

# Query
st.header("2. Semantic Search")
query_text = st.text_input("Ask a question")
if st.button("Search") and query_text:
    res = retrieve_and_answer(mongo_client.client, db_name, col_name, query_text)
    st.write(res["answer"])
