import mysql.connector
import json
import numpy as np
from sentence_transformers import SentenceTransformer, util
import warnings
import configparser

warnings.filterwarnings("ignore", category=FutureWarning)


config = configparser.ConfigParser()
config.read("db_config.ini")
# 1. Connect to DB
conn = mysql.connector.connect(
    host=config["mysql"]["host"],
    user=config["mysql"]["user"],
    password=config["mysql"]["password"],
    database=config["mysql"]["database"],
    port=config["mysql"]["port"],
    collation=config["mysql"]["collation"],
)
cursor = conn.cursor()

# 2. Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# 3. User query
query = "machine learning in hospitals"
query_vec = model.encode(query)

# 4. Fetch documents + embeddings
cursor.execute("""
    SELECT d.id, d.content, e.embedding 
    FROM document d 
    JOIN document_embeddings e ON d.id = e.doc_id
    group by d.content
""")
rows = cursor.fetchall()

# 5. Compare similarity
results = []
for doc_id, content, emb_json in rows:
    emb = np.array(json.loads(emb_json), dtype=np.float32)
    score = util.cos_sim(query_vec, emb).item()
    results.append((doc_id, content, score))

# 6. Sort by similarity
results.sort(key=lambda x: x[2], reverse=True)

# 7. Print top results
for doc_id, content, score in results[:3]:
    print(f"{score:.3f} → {content}")
