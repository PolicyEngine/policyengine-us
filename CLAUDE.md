# PolicyEngine US - Development Guide

## Build/Test/Lint Commands
```bash
# Install dependencies
make install

# Format code
make format  # Runs black with line length 79 and fixes import ordering

# Run all tests
make test

# Run specific test file or directory
pytest policyengine_us/tests/path/to/test_file.py

# Run specific test function
pytest policyengine_us/tests/path/to/test_file.py::test_function_name

# Run YAML-specific tests
make test-yaml-structural
make test-yaml-no-structural

# Generate documentation
make documentation
```

## Code Style Guidelines
- **Imports**: Use absolute imports from policyengine_us.model_api for Variables
- **Formatting**: Line length 79 characters; use Black for formatting
- **Types**: Use type hints; import ArrayLike from numpy.typing
- **Variable Naming**: Use snake_case for variable names and function names
- **Error Handling**: Use np.divide with out/where parameters to avoid divide-by-zero errors
- **Documentation**: Add docstrings to classes and functions; include description, parameters, returns