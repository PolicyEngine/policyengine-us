import argparse
from pathlib import Path

from plotly.offline import get_plotlyjs_version

# This command-line tool enables Plotly charts to show in the HTML files for the Jupyter Book documentation.

parser = argparse.ArgumentParser()
parser.add_argument("book_path", help="Path to the Jupyter Book.")

args = parser.parse_args()

# Find every HTML file in the Jupyter Book that contains a Plotly chart, and
# load plotly.js at the start of its <head> tag, so the charts that
# render_plotly_outputs.py writes can draw with the global Plotly object as
# the page is parsed. The version matches the installed plotly package.

book_folder = Path(args.book_path)
plotly_script = (
    f'<script src="https://cdn.plot.ly/plotly-{get_plotlyjs_version()}.min.js"'
    ' charset="utf-8"></script>'
)

for html_file in book_folder.glob("**/*.html"):
    with open(html_file, "r") as f:
        html = f.read()

    if 'class="plotly-graph-div"' not in html or plotly_script in html:
        continue

    html = html.replace("<head>", "<head>" + plotly_script, 1)

    with open(html_file, "w") as f:
        f.write(html)
