import mysql.connector
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

# 1. Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="admin",
    password="saboor123",
    database="search",
    port=3307,
    collation="utf8mb4_unicode_ci",
)
cursor = conn.cursor()

# 2. Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# 3. Fetch documents
cursor.execute("SELECT id, content FROM document")
docs = cursor.fetchall()

# 4. Generate and store embeddings
for doc_id, content in docs:
    embedding = model.encode(content).tolist()  # convert to list
    cursor.execute(
        "INSERT INTO document_embeddings (doc_id, embedding) VALUES (%s, %s)",
        (doc_id, json.dumps(embedding)),
    )

conn.commit()
