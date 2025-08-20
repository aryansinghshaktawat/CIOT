# CIOT Development Guide

## Project Structure

The CIOT project follows professional Python application structure:

```
CIOT-Toolkit/
├── src/                    # Source code
│   ├── core/              # Core application modules
│   ├── gui/               # User interface components
│   ├── services/          # External service integrations
│   └── utils/             # Utility modules
├── data/                  # Investigation data storage
├── config/                # Configuration files
├── logs/                  # Audit and application logs
├── tests/                 # Test modules
└── docs/                  # Documentation
```

## Development Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git for version control

### Environment Setup
```bash
# Clone the repository
git clone https://github.com/ciot-toolkit/ciot.git
cd ciot

# Create virtual environment
python -m venv ciot-env
source ciot-env/bin/activate  # On Windows: ciot-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8
```

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_core/test_config_manager.py

# Run with coverage
python -m pytest --cov=src tests/
```

### Code Style
The project follows PEP 8 style guidelines:

```bash
# Format code with black
black src/ tests/

# Check style with flake8
flake8 src/ tests/
```

## Architecture Overview

### Core Modules
- **application.py**: Main application class and GUI setup
- **config_manager.py**: Handles all application configuration
- **audit_logger.py**: Professional audit logging system
- **case_management.py**: Investigation case creation and management

### GUI Modules
- **surface_web_tab.py**: Surface web OSINT investigations
- **image_analysis_tab.py**: Image analysis and forensics
- **darkweb_tab.py**: Dark web investigation tools
- **ai_assistant_tab.py**: AI-powered investigation assistance

### Service Modules
- **image_hosting.py**: Integration with image hosting services
- **search_engines.py**: Search engine API integrations
- **forensic_tools.py**: External forensic tool integrations

### Utility Modules
- **validators.py**: Data validation and sanitization
- **osint_utils.py**: OSINT-specific utility functions
- **report_generator.py**: Professional HTML report generation

## Adding New Features

### Creating a New Tab
1. Create new file in `src/gui/tabs/`
2. Inherit from `ctk.CTkFrame`
3. Implement required methods
4. Add to main application in `src/core/application.py`

### Adding New Services
1. Create new file in `src/services/`
2. Implement service class with proper error handling
3. Add configuration options if needed
4. Write tests for the service

### Adding New Utilities
1. Create new file in `src/utils/`
2. Implement utility functions
3. Add proper documentation
4. Write comprehensive tests

## Testing Guidelines

### Test Structure
- Unit tests for individual functions
- Integration tests for service interactions
- GUI tests for user interface components

### Test Naming
- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<functionality>`

### Test Coverage
Maintain minimum 80% test coverage for all modules.

## Contributing

### Pull Request Process
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Ensure all tests pass
5. Submit pull request

### Code Review Checklist
- [ ] Code follows PEP 8 style guidelines
- [ ] All tests pass
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] No security vulnerabilities introduced

## Security Considerations

### Data Handling
- All user data stored locally only
- No transmission to external services without consent
- Proper sanitization of all inputs

### Dependencies
- Regular security audits of dependencies
- Use only well-maintained packages
- Pin dependency versions for stability

### Privacy
- Anonymous operation modes
- No tracking or telemetry
- Secure deletion of temporary files