import unicodedata
import re

# def normalize_content(text):
#     normalized_text = unicodedata.normalize("NFKD", text)
#     # Convert to lowercase
#     results = normalized_text.lower().strip()

#     # print("Normalized text:", results)  # Debugging line
#     # Remove accents
#     return results


def normalize_content(text):
    # Normalize Unicode to NFKC (handles Persian/Arabic diacritics)
    text = unicodedata.normalize("NFKC", text)
    # Remove extra whitespace
    text = " ".join(text.strip().split())
    # Remove only specific punctuation, preserve Persian/Arabic (U+0600–U+06FF)
    text = re.sub(r"[^\w\s\u0600-\u06FF]", "", text)
    # print(f"Input: {text} -> Normalized: {text}")
    return text
