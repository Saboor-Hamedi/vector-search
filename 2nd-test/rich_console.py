from rich.console import Console
from rich.table import Table
import arabic_reshaper
from bidi.algorithm import get_display

console = Console()


def fix_arabic_text(text):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text


def display_results(results):
    table = Table(title="Search Results")

    table.add_column("Doc ID", style="cyan", no_wrap=True)
    table.add_column("Score", style="magenta")
    table.add_column("Content", style="green")

    for doc_id, content, score in results:
        content_display = fix_arabic_text(content)
        table.add_row(
            str(doc_id),
            f"{score:.2f}",
            content_display[:80] + ("..." if len(content_display) > 80 else ""),
        )

    console.print(table)
