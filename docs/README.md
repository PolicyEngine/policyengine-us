# PolicyEngine US Documentation

This directory contains the documentation for PolicyEngine US, built using Jupyter Book 2.0 (MyST).

## Quick Start

### Building the Documentation

```bash
make documentation
```

This command will:
1. Generate parameter documentation
2. Generate variable documentation  
3. Build the HTML site using MyST
4. Add Plotly support
5. Generate a LaTeX/PDF version

### Viewing the Documentation

After building, you have several options to view the documentation:

#### Option 1: MyST Development Server (Recommended)

```bash
cd docs
myst start
```

Then open http://localhost:3001 in your browser.

**Note**: The server runs in the foreground. To keep it running while you work, either:
- Open a new terminal tab/window for other work
- Run it in the background: `myst start &`
- Use a terminal multiplexer like tmux or screen

#### Option 2: View the Static Build

The static HTML files are built with hashed filenames in `docs/_build/site/public/`. To find and open the main page:

```bash
# Find the main HTML file
find docs/_build/site/public -name "*.html" -exec grep -l "PolicyEngine US" {} \; | head -1 | xargs open
```

#### Option 3: Simple HTTP Server

Although the files are hashed, you can browse them with:

```bash
cd docs/_build/site/public
python -m http.server 8000
```

Then navigate to http://localhost:8000 and click on the HTML files.

### Viewing the PDF Documentation

```bash
open docs/_build/latex/policyengine_us_policy_rules.pdf
```

## Documentation Structure

- **Policy Reference** - Comprehensive rules and parameters for all programs
- **Program Demonstrations** - Interactive notebooks showing how select programs work
- **Variables Reference** - Technical documentation of all variables
- **Parameters Reference** - Technical documentation of all parameters
- **API Documentation** - Programming interface reference
- **Contributing** - Developer guidelines

## Development

### Live Preview While Editing

For development with live reload:

```bash
cd docs
myst start --watch
```

This will automatically rebuild when you make changes to the documentation files.

### Running in Background

To run the server in the background and continue using your terminal:

```bash
cd docs
nohup myst start > myst.log 2>&1 &
echo $! > myst.pid
```

To stop the background server:

```bash
kill $(cat myst.pid)
rm myst.pid
```

### Using tmux (Recommended for Development)

```bash
# Start a new tmux session
tmux new -s docs

# Inside tmux, start the server
cd docs
myst start

# Detach from tmux (Ctrl+B, then D)
# The server keeps running in the background

# To reattach later
tmux attach -t docs

# To kill the session when done
tmux kill-session -t docs
```

## Requirements

- Python 3.10+
- MyST (`mystmd` package)
- LaTeX (for PDF generation) - specifically `enumitem` and `fancyhdr` packages

## Troubleshooting

### "Module not found" errors in notebooks
The notebooks use the PolicyEngine US API. Make sure you have installed the package:
```bash
pip install -e .
```

### LaTeX errors
If you get LaTeX package errors, see [LATEX_SETUP.md](LATEX_SETUP.md) for installation instructions.

### Port already in use
If port 3001 is already in use, you can specify a different port:
```bash
myst start --port 3002
```

## Configuration

- `myst.yml` - MyST configuration
- `_toc.yml` - Table of contents structure
- `_config.yml` - Legacy Jupyter Book config (kept for compatibility)