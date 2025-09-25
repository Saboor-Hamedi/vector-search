from db_connection import db_connection
from models import ai_model
from helper_functions import go_back, check_if_empty_input
from rich_console import display_results
from text_properties import normalize_content
from languages import detect_language
from bm25_utils import update_bm25_index, bm25_index, bm25_corpus
import re
import sys
import os

from ColorScheme import ColorScheme

cs = ColorScheme()

# call the ColorScheme with re here
DEFAULT_TOP_K = 100
DEFAULT_THRESHOLD = 0.4
BM25_WEIGHT = 0.5
conn = db_connection()
cursor = conn.cursor()

print(f"{cs.RED} Connected to the database successfully.{cs.RESET}")

model = ai_model("paraphrase-multilingual-MiniLM-L12-v2")


def insert_document(content):
    if check_if_empty_input(content):
        print("\033[31mInput cannot be empty.\033[0m")
        return False

    nor_content = normalize_content(content)
    language = detect_language(nor_content)
    try:
        emb = model.encode(nor_content).tolist()
        cursor.execute(
            "INSERT INTO document (content, languages) VALUES (%s, %s) RETURNING id;",
            (nor_content, language),
        )
        doc_id = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO document_embedding (doc_id, embedding) VALUES (%s, %s)",
            (doc_id, emb),
        )
        conn.commit()
        update_bm25_index(cursor, normalize_content)  # Update BM25 index
        print(
            f"{cs.GREEN}Successfully inserted document (language: {language}).{cs.RESET}"
        )
    except Exception as e:
        print(f"{cs.RED}Error inserting document: {e}{cs.RESET}")
        conn.rollback()
        return False


def search(query, top_k=DEFAULT_TOP_K, threshold=DEFAULT_THRESHOLD, bm25_weight=0.5):
    if check_if_empty_input(query):
        print(f"{cs.RED}mInput cannot be empty.{cs.RESET}")
        return []
    nor_query = normalize_content(query)
    print(f"Input: {query} -> Normalized: {nor_query}")
    try:
        query_vec = model.encode(nor_query).tolist()
        vec_str = f"[{','.join(map(str, query_vec))}]"
        # print(vec_str)
        cursor.execute(
            """
            SELECT d.id, d.content, (1 - (e.embedding <=> %s::vector)) AS similarity, 
                   d.languages, d.created_at
            FROM document d
            JOIN document_embedding e ON d.id = e.doc_id
            WHERE (1 - (e.embedding <=> %s::vector)) >= %s
            ORDER BY e.embedding <=> %s::vector
            LIMIT %s
        """,
            (vec_str, vec_str, threshold, vec_str, top_k * 2),
        )
        rows = cursor.fetchall()
        semantic_results = [
            (row[0], row[1], float(row[2]), row[3], row[4]) for row in rows
        ]
        print(
            f"Semantic results:{cs.OKGREEN}{cs.BOLD}{len(semantic_results)}{cs.NORMAL}{cs.RESET} documents"
        )

        update_bm25_index(cursor, normalize_content)
        if bm25_index is None or not bm25_corpus:
            print(f"{cs.YELLOW}BM25 index empty, using semantic search only.{cs.RESET}")
            results = semantic_results
        else:
            bm25_scores = bm25_index.get_scores(nor_query.split())
            print(f"BM25 scores: {bm25_scores}")
            bm25_results = [
                (doc_id, content, bm25_scores[i])
                for i, (doc_id, content) in enumerate(bm25_corpus)
            ]

            # Combine scores
            combined_results = {}
            max_semantic = (
                max([r[2] for r in semantic_results] + [0.01])
                if semantic_results
                else 0.01
            )
            max_bm25 = (
                max([r[2] for r in bm25_results] + [0.01]) if bm25_results else 0.01
            )
            for doc_id, content, score, lang, created in semantic_results or []:
                combined_results[doc_id] = (
                    content,
                    score / max_semantic * bm25_weight,
                    lang,
                    created,
                )
            for doc_id, content, score in bm25_results or []:
                if doc_id in combined_results:
                    combined_results[doc_id] = (
                        content,
                        combined_results[doc_id][1]
                        + (score / max_bm25 * (1 - bm25_weight))
                        if max_bm25 > 0
                        else combined_results[doc_id][1],
                        combined_results[doc_id][2],
                        combined_results[doc_id][3],
                    )
                else:
                    combined_results[doc_id] = (
                        content,
                        score / max_bm25 * (1 - bm25_weight) if max_bm25 > 0 else 0,
                        None,
                        None,
                    )
            results = [
                (doc_id, content, score, lang, created)
                for doc_id, (content, score, lang, created) in combined_results.items()
            ]
            results.sort(key=lambda x: x[2], reverse=True)
    except Exception as e:
        print(f"{cs.RED}Error during search: {e}{cs.RESET}")
        return []
    if not results:
        print(f"{cs.RED}No relevant results found.{cs.RESET}")
        return []
    display_results(results[:top_k], query=nor_query)
    #  Print unique languages found
    langs = [lang for _, _, _, lang, _ in results[:top_k] if lang]
    label = "Language Found" if len(langs) == 1 else "Languages Found"
    print(f"{cs.YELLOW}{label}: {langs}{cs.RESET}\n")

    # Return top_k results
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
