# LaTeX Setup Instructions

To generate the PDF documentation, you need LaTeX with the required packages.

## Installation Instructions

### Recommended: Install Full MacTeX (includes all packages)

If you have BasicTeX installed, you'll need to remove it first:

```bash
# Remove BasicTeX if installed
brew uninstall --cask basictex

# Install full MacTeX (~4GB)
brew install --cask mactex

# Activate the new PATH
eval "$(/usr/libexec/path_helper)"
```

### Alternative: Install Individual Packages with BasicTeX

If you prefer to keep BasicTeX (~100MB) and just install missing packages:

```bash
# For TeX Live 2024, use the frozen repository
sudo tlmgr option repository https://ftp.math.utah.edu/pub/tex/historic/systems/texlive/2024/tlnet-final
sudo tlmgr install enumitem fancyhdr
```

## Required Packages
- `enumitem` - For customizing lists
- `fancyhdr` - For custom headers and footers

## Verification

After installation, verify the packages are available:
```bash
make documentation-install-latex
```

Then generate the documentation:
```bash
make documentation
```

The PDF will be generated at `docs/policy/policyengine_us_policy_rules.pdf`