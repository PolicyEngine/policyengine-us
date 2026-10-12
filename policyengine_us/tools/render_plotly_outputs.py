"""Give stored Plotly outputs an HTML rendering the Jupyter Book can show.

The book renders the outputs stored in each notebook (docs/_config.yml sets
execute_notebooks: off). Most Plotly outputs were saved with only the
application/vnd.plotly.v1+json MIME type, which myst-nb skips, and the rest
carry notebook-mode HTML that loads plotly.js through require.js. This
replaces the HTML of every output that has the Plotly figure with a plain
rendering of that figure that draws with the page's global Plotly object,
which add_plotly_to_book.py loads on every page with a chart.

It rewrites notebooks in place. The Documentation workflow runs it on a
throwaway checkout; to preview locally, run it on a copy of docs/ or discard
the changes afterwards (git checkout docs).
"""

import argparse
import json
from pathlib import Path

import plotly.io as pio

PLOTLY_MIME = "application/vnd.plotly.v1+json"


def render_book(book_path: Path) -> int:
    rendered = 0
    for path in sorted(book_path.rglob("*.ipynb")):
        if "_build" in path.parts or ".ipynb_checkpoints" in path.parts:
            continue
        notebook = json.loads(path.read_text())
        changed = False
        for cell in notebook.get("cells", []):
            for output in cell.get("outputs", []):
                data = output.get("data", {})
                if PLOTLY_MIME in data:
                    data["text/html"] = pio.to_html(
                        data[PLOTLY_MIME],
                        include_plotlyjs=False,
                        full_html=False,
                        validate=False,
                    )
                    changed = True
                    rendered += 1
        if changed:
            path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n")
    return rendered


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("book_path", help="Path to the Jupyter Book source.")
    args = parser.parse_args()
    count = render_book(Path(args.book_path))
    print(f"Rendered {count} stored Plotly outputs as HTML.")
