def normalize_content(text):
    # Trim whitespace, but keep the original case and characters.
    normalized_text = " ".join(text.strip().split())
    # You can add a simple lowercase step if you want, but be aware it
    normalized_text = normalized_text.lower()
    return normalized_text


# استفاده
