# fetch-pdf

Download and extract text from a PDF URL using curl and a PDF text extraction tool.

## Usage

```bash
# Download PDF
curl -L -o document.pdf "URL"

# Extract all text from PDF (requires pdftotext from poppler-utils)
pdftotext document.pdf output.txt

# Or use Python's pdfplumber for better text extraction
python3 -c "import pdfplumber; pdf = pdfplumber.open('document.pdf'); text = '\n\n'.join([page.extract_text() for page in pdf.pages]); print(text)"
```

## Installation

### macOS
```bash
brew install poppler  # for pdftotext
# or
pip install pdfplumber  # for Python approach
```

### Linux
```bash
sudo apt-get install poppler-utils  # for pdftotext
# or
pip install pdfplumber  # for Python approach
```

## Example

```bash
# Download a PDF
curl -L -o document.pdf "https://example.gov/document.pdf"

# Extract all text
pdftotext document.pdf document.txt

# View the extracted text
cat document.txt
```
