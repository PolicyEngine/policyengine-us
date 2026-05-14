# Quarto docs prototype

A prototype for migrating PolicyEngine US documentation from Jupyter Book 2 to Quarto.

## Why

- **One source for docs and papers.** Quarto renders the same `.qmd` file to HTML (docs site) and PDF (working paper) from the same source. Methodology pages get reused as paper chapters; numeric results come from the same live simulation.
- **Jupyter Book 2 drift.** The main Jupyter Book maintainer migrated the project to Quarto; JB2 has slower development and less academic adoption now.
- **Reference auto-generation.** Quarto's computational blocks can call PolicyEngine US's metadata API to regenerate the variable catalog on each build.

## Layout

```
docs-quarto/
├── _quarto.yml
├── index.qmd
├── references.bib
├── methodology/
│   ├── index.qmd
│   └── moop-decomposition.qmd
├── programs/
│   ├── index.qmd
│   └── chip.qmd
├── reference/
│   └── index.qmd
└── assets/
    └── custom.scss
```

## Build

```bash
cd docs-quarto
quarto render
open _site/index.html
```

## Status

This is a prototype — only two substantive content pages (MOOP decomposition, CHIP). The existing `docs/` Jupyter Book content has not been migrated. If this approach is approved, the next steps are:

1. Migrate remaining methodology pages.
2. Port program pages from `docs/gov/**`.
3. Wire up the reference auto-generator.
4. Add a paper output format (`--to pdf`) with journal template.
5. Retire `docs/` and update CI.
