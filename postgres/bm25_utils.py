from rank_bm25 import BM25Okapi
from ColorScheme import ColorScheme

cs = ColorScheme()
bm25_corpus = []
bm25_index = None


def update_bm25_index(cursor, normalize_content):
    global bm25_index, bm25_corpus
    cursor.execute("SELECT id, content FROM document")
    rows = cursor.fetchall()
    bm25_corpus = [(row[0], normalize_content(row[1])) for row in rows]
    tokenized = [content.split() for _, content in bm25_corpus if content.strip()]
    valid_tokenized = list(filter(lambda x: len(x) > 0, tokenized))

    # Filter out empty documents
    valid_tokenized = [tokens for tokens in tokenized if tokens]

    if not valid_tokenized:
        bm25_index = None
        bm25_corpus = []
        return
    bm25_index = BM25Okapi(valid_tokenized)
    print(f"BM25 index updated with {cs.BOLD}{len(bm25_corpus)}{cs.NORMAL} documents")
