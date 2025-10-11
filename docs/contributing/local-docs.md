# Running Documentation Locally

This guide shows how to build and view the PolicyEngine US documentation on your local machine.

## Prerequisites

1. **Python 3.13** (recommended) or 3.10-3.13
2. **Virtual environment** (recommended to avoid dependency conflicts)

## Quick Start

### 1. Set up your environment

```bash
# Create a virtual environment
python3.13 -m venv .venv-docs

# Activate it
source .venv-docs/bin/activate  # On macOS/Linux
# or
.venv-docs\Scripts\activate  # On Windows

# Install PolicyEngine with documentation dependencies
pip install -e ".[dev]"
```

### 2. Build the documentation

```bash
# From the repository root
make documentation
```

This command:
- Cleans previous builds
- Generates parameter documentation from YAML files
- Generates variable documentation from Python files  
- Builds the Jupyter Book HTML output
- Adds Plotly support for interactive charts

### 3. View the documentation

After building, open the documentation in your browser:

```bash
# macOS
open docs/_build/html/index.html

# Linux
xdg-open docs/_build/html/index.html

# Windows
start docs/_build/html/index.html
```

### 4. Serve locally with live reload (optional)

For a better development experience with automatic page refresh:

```bash
# Install a simple HTTP server
pip install livereload

# Serve the docs
cd docs/_build/html
python -m http.server 8000
```

Then visit http://localhost:8000 in your browser.

## Build Options

### Build specific formats

```bash
# HTML (default)
jupyter-book build docs --builder html

# PDF (requires LaTeX)
jupyter-book build docs --builder pdflatex

# Single-page HTML
jupyter-book build docs --builder singlehtml
```

### Clean build

```bash
# Remove all build artifacts
jupyter-book clean docs --all

# Just remove cached content
jupyter-book clean docs
```

## Troubleshooting

### Common Issues

1. **Import errors during variable/parameter generation**
   - Solution: Ensure you're in the virtual environment with all dependencies installed
   - Run: `pip install -e ".[dev]"`

2. **"command not found: jupyter-book"**
   - Solution: Install development dependencies
   - Run: `pip install jupyter-book`

3. **Build warnings about missing references**
   - These are usually harmless and relate to cross-references to pages that don't exist yet
   - Check the specific warning to see if it's a real issue

4. **Plotly charts not showing**
   - The `make documentation` command includes a step to add Plotly support
   - If running manually, ensure you run: `python policyengine_us/tools/add_plotly_to_book.py docs/_build`

### Environment Issues

If you encounter dependency conflicts:

```bash
# Start fresh
deactivate  # If in a virtual environment
rm -rf .venv-docs
python3.13 -m venv .venv-docs
source .venv-docs/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
```

## Development Workflow

When working on documentation:

1. **Make your changes** to the Markdown/RST files in `docs/`
2. **Rebuild**: Run `make documentation` 
3. **Refresh browser** to see changes
4. **Check for warnings/errors** in the build output

For faster iteration on content (without regenerating variable/parameter docs):

```bash
cd docs
jupyter-book build . --builder html
```

## Auto-generated Documentation

The documentation includes auto-generated content:

- **Variable Reference** (`docs/variables/`): Generated from Python variable files
- **Parameter Reference** (`docs/parameters/`): Generated from YAML parameter files

These are regenerated each time you run `make documentation`. To regenerate just these:

```bash
# Regenerate parameter docs only
python docs/scripts/generate_parameter_docs.py

# Regenerate variable docs only  
python docs/scripts/generate_variable_docs.py
```

## Documentation Structure

```
docs/
├── _build/              # Build output (git-ignored)
│   └── html/           # HTML output
├── _config.yml         # Jupyter Book configuration
├── _toc.yml           # Table of contents
├── index.md           # Home page
├── contributing/      # Contributing guides
├── policy/           # Policy documentation
├── api/             # API reference
├── variables/       # Auto-generated variable docs
├── parameters/      # Auto-generated parameter docs
└── scripts/         # Documentation generators
```

## Contributing to Documentation

See [Documentation Guidelines](documentation.md) for:
- Writing style guide
- Markdown/MyST syntax
- Adding new pages
- Working with notebooks