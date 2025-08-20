# Changelog

All notable changes to the Cyber Investigation OSINT Toolkit (CIOT) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2024-12-09

### Added
- **Professional Project Structure**: Complete reorganization into industry-standard directory layout
- **Modular Architecture**: Separated core, GUI, services, and utilities into distinct modules
- **Case Management System**: Professional investigation case creation and tracking
- **Audit Logging**: Comprehensive audit trails for legal compliance
- **Configuration Management**: Centralized configuration system with JSON storage
- **Professional Reporting**: HTML report generation with legal disclaimers
- **Evidence Chain Management**: Cryptographic integrity verification for evidence
- **Multi-Tab Interface**: Organized investigation workflows across specialized tabs
- **Surface Web OSINT**: Email, phone, IP, and name investigation capabilities
- **Image Analysis & Forensics**: Reverse image search and metadata extraction
- **Dark Web Investigation**: Specialized tools for .onion analysis
- **AI Assistant**: Intelligent investigation guidance
- **Additional OSINT Tools**: Extended toolkit for comprehensive investigations
- **Aadhaar Validator**: Identity verification tools
- **Dashboard**: Investigation overview and management
- **Privacy Protection**: Anonymous operation modes
- **Test Framework**: Professional testing structure with pytest
- **Comprehensive Documentation**: User guides and development documentation

### Changed
- **Complete Code Reorganization**: Moved from scattered files to professional structure
- **Import System**: Fixed all import paths for new modular structure
- **GUI Architecture**: Reorganized all tabs into `src/gui/tabs/` directory
- **Configuration System**: Moved from scattered config to centralized management
- **Data Storage**: Organized all data into `data/` directory with subdirectories

### Removed
- **Duplicate Files**: Eliminated all duplicate GUI and utility files
- **Unused Directories**: Removed empty and unnecessary directories
- **System Files**: Cleaned up cache files and system-specific files
- **Scattered Structure**: Removed old disorganized file layout

### Fixed
- **Import Errors**: Resolved all module import issues
- **Path Dependencies**: Fixed all file path references
- **Code Organization**: Eliminated circular dependencies
- **File Structure**: Proper Python package structure with `__init__.py` files

### Security
- **Local Data Storage**: All data remains local with no external transmission
- **Evidence Integrity**: SHA-256 hash verification for all evidence items
- **Audit Compliance**: Professional audit logging for legal requirements
- **Privacy First**: Anonymous operation modes and secure data handling

## [2.x.x] - Previous Versions

### Legacy Features
- Basic OSINT investigation capabilities
- Image analysis tools
- Dark web investigation features
- Various utility functions

*Note: Version 3.0.0 represents a complete rewrite and reorganization of the toolkit with professional standards and enterprise-grade features.*

---

## Version Numbering

- **Major version** (X.0.0): Incompatible API changes or major restructuring
- **Minor version** (X.Y.0): New functionality in a backwards compatible manner
- **Patch version** (X.Y.Z): Backwards compatible bug fixes

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.