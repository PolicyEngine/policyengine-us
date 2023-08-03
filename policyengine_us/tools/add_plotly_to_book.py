import argparse
from pathlib import Path

# This command-line tools enables Plotly charts to show in the HTML files for the Jupyter Book documentation.

parser = argparse.ArgumentParser()
parser.add_argument("book_path", help="Path to the Jupyter Book.")

args = parser.parse_args()

# Find every HTML file in the Jupyter Book. Then, add a script tag to the start of the <head> tag in each file, with the contents:
# <script src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.4/require.min.js"></script>

book_folder = Path(args.book_path)

for html_file in book_folder.glob("**/*.html"):
    with open(html_file, "r") as f:
        html = f.read()

    # Add the script tag to the start of the <head> tag.
    html = html.replace(
        "<head>",
        '<head><script src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.4/require.min.js"></script>',
    )

    with open(html_file, "w") as f:
        f.write(html)
