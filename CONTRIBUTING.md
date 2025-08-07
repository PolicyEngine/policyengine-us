# Contributing to PolicyEngine US

Thank you for wanting to contribute to PolicyEngine! 🎉

## Quick Start

1. **Create or claim an issue** on our [issue tracker](https://github.com/PolicyEngine/policyengine-us/issues) (required!)
2. **Fork and clone** the repository
3. **Install dependencies** with `uv`:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh  # Install uv
   source $HOME/.cargo/env                          # Add to PATH
   uv venv && source .venv/bin/activate            # Create & activate venv
   uv pip install -e ".[dev]"                      # Install dependencies
   ```
4. **Make your changes** following our style guide
5. **Test** with `make format && make test`
6. **Submit a PR** linking to the issue with `Fixes #123` ([see GitHub docs](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue))

## Comprehensive Documentation

For detailed guides on:
- 📋 Development workflow and best practices
- 🧪 Writing tests and test-driven development
- 📝 Code style and conventions
- 🚀 Advanced topics and troubleshooting

**Visit our [Contributor Documentation](https://policyengine.github.io/policyengine-us/contributing/index.html)**

## Key Commands

```bash
make format          # Format code (required before commit!)
make test           # Run all tests
make documentation  # Build docs locally
```

## Community

- 💬 [GitHub Discussions](https://github.com/PolicyEngine/policyengine-us/discussions) for questions
- 🐛 [Issue Tracker](https://github.com/PolicyEngine/policyengine-us/issues) for bugs and features
- 📚 [Full Documentation](https://policyengine.github.io/policyengine-us/)