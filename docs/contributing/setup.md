# Development Setup

This guide will help you set up your development environment for contributing to PolicyEngine US.

## Prerequisites

- Python 3.10-3.13 (check `pyproject.toml` for current versions)
- Git
- A GitHub account
- A code editor (we recommend VS Code)

## Installation Methods

### Using uv (Recommended) 🚀

[uv](https://github.com/astral-sh/uv) is a fast Python package manager written in Rust that significantly speeds up dependency installation.

#### Install uv

:::::{tab-set}
::::{tab-item} macOS/Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
::::

::::{tab-item} Windows
```powershell
# Run PowerShell as Administrator
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```
::::
:::::

#### Set up the project

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/policyengine-us.git
cd policyengine-us

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e ".[dev]"
```

### Using pip (Traditional)

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/policyengine-us.git
cd policyengine-us

# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]" --config-settings editable_mode=compat
```

### Using GitHub Codespaces

For a zero-setup option:

1. Fork the repository
2. Click "Code" → "Codespaces" → "Create codespace on master"
3. Wait for environment setup
4. In the terminal:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source $HOME/.cargo/env
   uv venv
   source .venv/bin/activate
   uv pip install -e ".[dev]"
   ```

## Verify Installation

Run the test suite to ensure everything is working:

```bash
make test
```

You should see tests running and passing. Some tests may be slow on first run as they download data.

## VS Code Setup

### Recommended Extensions

- **Python** - Microsoft's official Python extension
- **Pylance** - Fast Python language server
- **Black Formatter** - Code formatting
- **GitHub Pull Requests** - PR management
- **GitLens** - Enhanced Git integration

### Settings

Add to your `.vscode/settings.json`:

```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "79"],
    "editor.formatOnSave": true,
    "editor.rulers": [79]
}
```

## Common Issues

### Import Errors

If you see import errors, ensure you:
1. Activated your virtual environment
2. Installed with `-e` (editable mode)
3. Are in the project root directory

### Memory Issues

Large test suites may require more memory:
```bash
# Run specific test file
pytest policyengine_us/tests/policy/baseline/gov/states/ny/tax/income/credits/test_ny_eitc.py

# Run with less parallelism
pytest -n 2  # Instead of auto
```

### uv Specific Issues

If uv fails:
```bash
# Clear cache and retry
uv cache clean
uv pip install -e ".[dev]" --force-reinstall

# Or fall back to pip
pip install -e ".[dev]"
```

## Next Steps

Now that your environment is set up:
1. Read our [Development Workflow](workflow.md)
2. Understand our [Testing Guidelines](testing.md)
3. Review the [Style Guide](style-guide.md)
4. Find an issue to work on