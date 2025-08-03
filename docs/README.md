# PolicyEngine US Documentation

This directory contains comprehensive documentation for PolicyEngine US, including policy reference materials, API documentation, and contributing guides.

## Viewing Documentation

### Option 1: Build and View Locally

1. **Set up environment** (Python 3.13 recommended):
   ```bash
   python3.13 -m venv .venv-docs
   source .venv-docs/bin/activate
   pip install -e ".[dev]"
   ```

2. **Build documentation**:
   ```bash
   make documentation
   ```
   
   This will:
   - Generate parameter documentation from YAML files
   - Generate variable documentation from Python files
   - Build the Jupyter Book HTML
   - Generate a LaTeX/PDF journal paper

3. **View in browser**:
   ```bash
   # macOS
   open docs/_build/html/index.html
   
   # Linux  
   xdg-open docs/_build/html/index.html
   
   # Windows
   start docs/_build/html/index.html
   ```

### Option 2: View on GitHub Pages

Once changes are pushed and merged, documentation is automatically built and published to:
https://policyengine.github.io/policyengine-us/

## Documentation Structure

```
docs/
├── _build/                    # Build output (git-ignored)
│   ├── html/                 # HTML documentation
│   └── latex/                # LaTeX/PDF output
├── policy/                   # Policy reference documentation
│   ├── federal/              # Federal programs
│   │   ├── taxation/         # Tax credits and deductions
│   │   └── transfers/        # Benefit programs
│   └── state/                # State programs
├── api/                      # API reference
├── contributing/             # Contributing guides
├── variables/                # Auto-generated variable reference
├── parameters/               # Auto-generated parameter reference
└── scripts/                  # Documentation generators
```

## Key Features

### 1. Policy Documentation
Comprehensive documentation of tax and benefit programs in Atlanta Fed Policy Rules Database style:
- Detailed eligibility criteria
- Benefit calculation formulas
- Legislative citations
- Program interactions
- State variations

### 2. Auto-Generated References
- **Variables**: All ~5000+ variables with metadata, units, and references
- **Parameters**: All policy parameters with current values and history

### 3. Academic Output
The documentation can be compiled into a journal-quality PDF paper:
```bash
# After building docs
cat docs/_build/latex/policyengine_us_policy_rules.tex
```

To compile to PDF (requires LaTeX):
```bash
cd docs/_build/latex
pdflatex policyengine_us_policy_rules.tex
```

## Contributing to Documentation

See [Contributing Guide](contributing/documentation.md) for:
- Writing style guidelines
- Adding new policy documentation
- Updating parameters
- Building and testing locally

## Quick Links

- [Local Build Instructions](contributing/local-docs.md)
- [Style Guide](contributing/style-guide.md)
- [Policy Reference](policy/index.md)
- [API Documentation](api/index.md)