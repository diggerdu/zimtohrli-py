# Contributing to Zimtohrli Python Binding

Thank you for your interest in contributing to the Zimtohrli Python binding! This document provides guidelines for contributing to the project.

## Development Setup

### Prerequisites

1. **System Dependencies**:
   ```bash
   # Ubuntu/Debian
   sudo apt install cmake pkg-config libflac-dev libvorbis-dev libogg-dev libopus-dev libsoxr-dev
   
   # macOS
   brew install cmake pkg-config flac libvorbis libogg opus sox
   
   # Conda (recommended)
   conda install -c conda-forge cmake pkg-config libflac libvorbis libogg libopus soxr
   ```

2. **Python Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .[dev]
   ```

### Building from Source

```bash
git clone https://github.com/diggerdu/zimtohrli-py.git
cd zimtohrli-py
pip install -e .
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=zimtohrli_py tests/

# Run specific test
pytest tests/test_core.py::TestCoreAPI::test_identical_signals
```

### Code Style

We use Black and isort for code formatting:

```bash
# Format code
black zimtohrli_py/ tests/
isort zimtohrli_py/ tests/

# Check formatting
black --check zimtohrli_py/ tests/
flake8 zimtohrli_py/ tests/
```

## Contributing Guidelines

### 1. Issues

- **Bug Reports**: Use the bug report template, include minimal reproduction example
- **Feature Requests**: Describe the use case and proposed API
- **Questions**: Use GitHub Discussions for general questions

### 2. Pull Requests

1. **Fork the repository** and create a feature branch
2. **Write tests** for new functionality
3. **Update documentation** as needed
4. **Follow code style** guidelines
5. **Ensure all tests pass**
6. **Write clear commit messages**

### 3. Commit Messages

Use conventional commit format:
```
type(scope): description

feat(core): add batch processing optimization
fix(audio): handle edge case in sample rate conversion
docs(readme): update installation instructions
test(core): add edge case tests for short audio
```

### 4. Testing

- Write tests for all new functionality
- Ensure backward compatibility
- Test on multiple Python versions (3.8+)
- Include performance regression tests for critical paths

### 5. Documentation

- Update README.md for new features
- Add docstrings for all public functions
- Include usage examples
- Update CHANGELOG.md

## Development Guidelines

### Code Structure

```
zimtohrli_py/
├── __init__.py          # Public API exports
├── core.py              # Core functionality
├── audio_utils.py       # Optional utilities
└── src/                 # C++ source code
    ├── CMakeLists.txt   # Build configuration
    └── *.cc, *.h        # C++ implementation
```

### Adding New Features

1. **C++ Extension**: Modify `pyohrli.cc` for new C++ functionality
2. **Python Wrapper**: Add high-level functions in `core.py`
3. **Tests**: Add comprehensive tests in `tests/`
4. **Documentation**: Update README and docstrings

### Performance Considerations

- Minimize Python-C++ boundary crossings
- Use numpy buffer protocol for efficient data transfer
- Profile performance-critical paths
- Consider memory usage for large audio files

### Error Handling

- Validate inputs at Python level when possible
- Provide clear error messages
- Handle edge cases gracefully
- Use appropriate exception types

## Release Process

1. **Update version** in `pyproject.toml` and `__init__.py`
2. **Update CHANGELOG.md** with new features and fixes
3. **Create release PR** with all changes
4. **Tag release** after merge: `git tag v1.x.x`
5. **Build and test** package: `python -m build`
6. **Upload to PyPI**: `twine upload dist/*`

## Getting Help

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community support
- **Email**: Contact maintainers for security issues

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/). Please be respectful and constructive in all interactions.

## License

By contributing to this project, you agree that your contributions will be licensed under the Apache License 2.0.

## Recognition

Contributors will be acknowledged in:
- CHANGELOG.md for significant contributions
- README.md contributors section
- Release notes

Thank you for contributing to Zimtohrli Python binding!