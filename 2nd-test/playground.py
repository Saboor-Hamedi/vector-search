import json
from tabnanny import check
import numpy as np
from sentence_transformers import util
import warnings
from db_connection import get_db_connection
from helper_functions import go_back, check_if_empty_input
from models import ai_model
from rich_console import display_results

warnings.filterwarnings("ignore", category=FutureWarning)
DEFAULT_TOP_K = 3
DEFAULT_THRESHOLD = 0.3
# Connect to DB
conn = get_db_connection()

cursor = conn.cursor()


# load model
model = ai_model("paraphrase-multilingual-MiniLM-L12-v2")


def insert_document(content):
    if check_if_empty_input(content):
        print("\033[31mInput cannot be empty.\033[0m")
        return False

    emb = model.encode(content).tolist()
    cursor.execute("INSERT INTO document (content) VALUES (%s)", (content,))
    doc_id = cursor.lastrowid
    cursor.execute(
        "INSERT INTO document_embedding (doc_id, embedding) VALUES (%s, %s)",
        (doc_id, json.dumps(emb)),
    )
    conn.commit()

    if cursor.rowcount >= 1:
        print("\033[32mSuccessfully inserted a new document.\033[0m")
        return True
    print("\033[31mFailed to insert the document.\033[0m")
    return []


def search(query, top_k=DEFAULT_TOP_K, threshold=DEFAULT_THRESHOLD):
    if check_if_empty_input(query):
        print("\033[31mInput cannot be empty.\033[0m")
        return []

    query_vec = model.encode(query).tolist()
    cursor.execute("""
        SELECT d.id, d.content, e.embedding
        FROM document d
        JOIN document_embedding e ON d.id = e.doc_id
        ORDER BY d.created_at DESC
    """)
    rows = cursor.fetchall()
    results = []
    for doc_id, content, emb_json in rows:
        emb = np.array(json.loads(emb_json), dtype=np.float32)
        score = util.cos_sim(query_vec, emb).item()
        if score >= threshold:
            results.append((doc_id, content, score))

    results.sort(key=lambda x: x[2], reverse=True)

    # Check if there are any results
    if not results:
        print("\033No relevant results found.\033[0m")
        return []

    display_results(results[:top_k])
    return results[:top_k]


# Playground for testing

while True:
    action = input("\nChoose: [i]nsert, [s]earch, [q]uit: ").strip().lower()
    if action == "i":
        text = input("Enter document text: ").strip()
        if go_back(text):
            continue
        insert_document(text)
    elif action == "s":
        query = input("Enter search query: ").strip()
        if go_back(query):
            continue
        print(f"Top results for '{query}': \n_________________________")
        search(query)
    elif action == "q":
        break
