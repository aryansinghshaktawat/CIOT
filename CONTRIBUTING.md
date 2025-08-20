# Contributing to CIOT

We love your input! We want to make contributing to the Cyber Investigation OSINT Toolkit as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

## Pull Requests

Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Any contributions you make will be under the MIT Software License

In short, when you submit code changes, your submissions are understood to be under the same [MIT License](LICENSE) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using GitHub's [issue tracker](https://github.com/yourusername/ciot-toolkit/issues)

We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/yourusername/ciot-toolkit/issues/new).

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## Development Setup

1. Fork and clone the repository
2. Create a virtual environment: `python -m venv ciot-env`
3. Activate it: `source ciot-env/bin/activate` (Linux/Mac) or `ciot-env\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Install development dependencies: `pip install pytest black flake8`

## Code Style

We use Python's PEP 8 style guide. Please ensure your code follows these conventions:

- Use 4 spaces for indentation
- Line length should not exceed 88 characters
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Use type hints where appropriate

### Formatting

We use `black` for code formatting:

```bash
black src/ tests/
```

### Linting

We use `flake8` for linting:

```bash
flake8 src/ tests/
```

## Testing

Please write tests for any new functionality. We use `pytest` for testing:

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=src tests/

# Run specific test file
python -m pytest tests/test_core/test_config_manager.py
```

## Documentation

- Update the README.md if you change functionality
- Add docstrings to new functions and classes
- Update the user guide if you add user-facing features
- Update the development guide if you change development processes

## Security

If you discover a security vulnerability, please send an email to [security@example.com] instead of using the issue tracker. All security vulnerabilities will be promptly addressed.

## Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

Examples of behavior that contributes to creating a positive environment include:

- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

### Enforcement

Project maintainers are responsible for clarifying the standards of acceptable behavior and are expected to take appropriate and fair corrective action in response to any instances of unacceptable behavior.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## References

This document was adapted from the open-source contribution guidelines for [Facebook's Draft](https://github.com/facebook/draft-js/blob/a9316a723f9e918afde44dea68b5f9f39b7d9b00/CONTRIBUTING.md).