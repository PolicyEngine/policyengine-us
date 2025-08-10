#! /usr/bin/env bash

git tag `uv run python -c "import toml; print(toml.load('pyproject.toml')['project']['version'])"`
git push --tags || true  # update the repository version
