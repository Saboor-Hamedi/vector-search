from rich.console import Console
from rich.table import Table
import arabic_reshaper
from bidi.algorithm import get_display
from datetime import datetime
import re

console = Console()


def fix_arabic_text(text):
    """
    Fixes the visual display of Arabic/Persian text for a left-to-right console.
    This function should be called ONLY for display purposes, after all
    string manipulation and highlighting has been completed.
    """
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)


def highlight_query(content, query):
    """
    Highlights a query term within a content string.
    This function operates on the logical, original string before visual
    reordering for Arabic/Persian display.
    """
    query_terms = query.split()
    highlighted_content = content

    # Iterate through each term in the query.
    for term in query_terms:
        # Use regex to find the term. re.escape() handles special characters.
        # The (?i) flag is for case-insensitive matching in Latin scripts.
        # For Persian, the normalization of the query and content is more important.
        try:
            highlighted_content = re.sub(
                re.escape(term),
                f"[bold yellow]{term}[/bold yellow]",
                highlighted_content,
                flags=re.IGNORECASE,
            )
        except Exception as e:
            # If highlighting fails, return the original content to prevent
            # the program from crashing.
            print(f"Error highlighting term '{term}': {e}")
            return content

    return highlighted_content


def truncate_at_word(text, max_length=80):
    """
    Truncates a string at a word boundary to a maximum length.
    """
    if len(text) <= max_length:
        return text
    truncated = text[:max_length].rsplit(" ", 1)[0]
    return truncated + "..." if len(truncated) < len(text) else text


def display_results(results, query=""):
    """
    Prints the search results in a well-formatted rich table.
    """
    table = Table(title="Search Results", show_header=True, header_style="bold magenta")
    table.add_column("Doc ID", style="cyan", width=8)
    table.add_column("Score", style="magenta", width=10)
    table.add_column("Content", style="white", width=50, overflow="fold")
    table.add_column("Language", style="green", width=12)
    table.add_column("Created At", style="blue", width=12)

    lang_map = {"en": "English", "fa": "Persian", "id": "Indonesian", None: "Unknown"}

    for doc_id, content, score, language, created_at in results:
        # 1. Highlight the content first on the logical string
        content_display = highlight_query(content, query)
        # 2. Fix the Arabic/Persian text for visual display
        content_display = fix_arabic_text(content_display)
        # 3. Truncate the text for display purposes
        content_display = truncate_at_word(content_display, 80)

        score_style = "green" if score > 0.7 else "yellow" if score > 0.4 else "red"
        language_display = lang_map.get(language, language or "Unknown").capitalize()
        created_at_str = (
            created_at.strftime("%Y-%m-%d")
            if isinstance(created_at, datetime)
            else str(created_at)
        )
        table.add_row(
            str(doc_id),
            f"[{score_style}]{score:.3f}[/{score_style}]",
            content_display,
            language_display,
            created_at_str,
        )

    console.print(table)
