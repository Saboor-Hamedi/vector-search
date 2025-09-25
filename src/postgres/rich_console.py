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


def highlight_query(content: str, query: str) -> str:
    """
    Highlight query terms in content. Works for multilingual text.
    """
    if not query:
        return content

    terms = [t for t in query.split() if t.strip()]
    if not terms:
        return content

    # Sort terms by length in descending order to match longer terms first
    terms = sorted(set(terms), key=len, reverse=True)

    out = content
    for term in terms:
        # Use regex to find the term. The (?i) flag is for case-insensitive matching.
        pattern = re.compile(re.escape(term), re.IGNORECASE)

        # Replace using a lambda function to preserve case and formatting of the matched text
        out = pattern.sub(lambda m: f"[bold yellow]{m.group(0)}[/bold yellow]", out)
    return out


def truncate_at_word(text: str, max_length: int) -> str:
    """
    Truncates a rich-formatted string at a word boundary to a maximum length.
    Preserves rich markup tags while counting characters.
    """
    plain_text_len = 0
    truncated_text = ""
    in_tag = False

    for i, char in enumerate(text):
        if char == "[" and not in_tag:
            # Found start of a tag
            in_tag = True
            truncated_text += char
        elif char == "]" and in_tag:
            # Found end of a tag
            in_tag = False
            truncated_text += char
        elif not in_tag:
            # Regular character
            if plain_text_len >= max_length:
                # Truncation point reached. Find the last space.
                last_space = truncated_text.rfind(" ")
                if last_space != -1:
                    # Truncate at the last space and add ellipsis
                    return truncated_text[:last_space] + "..."
                else:
                    # No space found, truncate directly
                    return truncated_text + "..."

            truncated_text += char
            plain_text_len += 1
        else:
            # Inside a tag, just append character
            truncated_text += char

    # If the whole string fits, return it as is
    return truncated_text


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
        # Step 1: Highlight the content on the logical string
        content_display = highlight_query(content, query)

        # Step 2: Truncate the text, correctly preserving markup
        content_display = truncate_at_word(content_display, 100)

        # Step 3: Fix the Arabic/Persian text for visual display.
        # This must be the last step to avoid corrupting rich markup.
        if language == "fa":  # Only for Persian
            content_display = fix_arabic_text(content_display)

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
