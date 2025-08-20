# 🛡️ Cyber Investigation OSINT Toolkit (CIOT)

**Professional Open Source Intelligence & Digital Forensics Platform**

[![Version](https://img.shields.io/badge/version-3.0-blue.svg)](https://github.com/yourusername/ciot-toolkit)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/yourusername/ciot-toolkit)

## 🎯 Overview

The Cyber Investigation OSINT Toolkit (CIOT) is a comprehensive, professional-grade platform designed for digital investigators, cybersecurity professionals, researchers, and law enforcement agencies. Built entirely with free and open-source technologies, CIOT provides enterprise-level capabilities without proprietary dependencies.

## ✨ Key Features

### 🔍 **Multi-Domain Investigation**
- **Enhanced Surface Web OSINT**: Comprehensive profile analysis with advanced phone investigation
- **Image Analysis & Forensics**: Advanced reverse image search and metadata analysis
- **Dark Web Investigation**: Specialized tools for deep web analysis
- **AI-Powered Assistant**: Intelligent investigation guidance and automation
- **Additional OSINT Tools**: Extended toolkit for comprehensive investigations
- **Identity Verification**: Aadhaar and other identity validation tools

### 📱 **Enhanced Phone Investigation Features**
- **Multi-Format Support**: Accepts any common phone number format automatically
- **Country-Specific Parsing**: 10+ countries with specialized validation rules
- **Google libphonenumber Integration**: Professional-grade parsing and validation
- **Comprehensive Intelligence**: Technical, security, social, and business analysis
- **Real-Time Validation**: Instant format checking with helpful error messages
- **Interactive Help System**: Contextual tooltips and inline guidance panels

### 🏢 **Professional Features**
- **Case Management**: Professional case creation, tracking, and organization
- **Evidence Chain**: Cryptographic integrity verification and chain of custody
- **Audit Logging**: Comprehensive audit trails for legal compliance
- **Professional Reporting**: Court-admissible HTML reports with detailed analysis
- **Auto-Save System**: Automatic session saving with configurable intervals
- **Privacy Protection**: Anonymous operation modes and secure data handling

### 🛡️ **Security & Compliance**
- **100% Open Source**: Complete transparency with no proprietary dependencies
- **Privacy-First Design**: Anonymous operations and local data storage
- **Evidence Integrity**: SHA-256 hash verification for all evidence items
- **Legal Compliance**: Designed for professional and legal investigation use
- **Secure Configuration**: Encrypted configuration and secure data handling

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Internet connection for OSINT services

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ciot-toolkit.git
   cd ciot-toolkit
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv ciot-env
   source ciot-env/bin/activate  # On Windows: ciot-env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python ciot.py
   ```

### First Launch
1. The application will create necessary directories automatically
2. Configure settings through the Settings dialog (⚙️ button)
3. Create your first investigation case (📁 New Case button)
4. Begin your investigation using the various OSINT tabs

## 📋 Investigation Workflow

### 1. **Case Creation**
- Create new investigation cases with detailed metadata
- Set priority levels and investigation types
- Track case progress and status

### 2. **Evidence Collection**
- Use multiple OSINT tabs for comprehensive data gathering
- Automatic evidence integrity verification
- Maintain proper chain of custody

### 3. **Analysis & Investigation**
- **Surface Web**: Profile analysis, social media investigation
- **Image Analysis**: Reverse image search, EXIF metadata extraction
- **Dark Web**: Specialized deep web investigation tools
- **AI Assistant**: Intelligent guidance and automation

### 4. **Documentation & Reporting**
- Generate professional HTML reports
- Include evidence chain and audit trails
- Export for legal proceedings or further analysis

## 🏗️ Architecture

### Professional Directory Structure
```
CIOT-Toolkit/
├── ciot.py                 # Main application entry point
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

### Core Components
- **Application Core**: Main application logic and GUI management
- **Case Management**: Professional case creation and tracking
- **Audit Logger**: Comprehensive audit trail system
- **Report Generator**: Professional investigation reports
- **Configuration Manager**: Secure configuration handling

## 🔧 Technical Specifications

### Built With
- **Python 3.8+**: Core application framework
- **CustomTkinter**: Modern, professional GUI framework
- **Requests**: HTTP client for web service integration
- **Pillow**: Advanced image processing and analysis
- **BeautifulSoup4**: Web scraping and HTML parsing
- **FPDF2**: Professional PDF report generation

### Free Services Integration
- **Catbox.moe**: Anonymous image hosting
- **Google Images**: Reverse image search
- **Yandex Images**: Advanced facial recognition
- **TinEye**: Image tracking and modification detection
- **Bing Visual Search**: Product and object identification
- **Forensically**: Advanced image forensics
- **FotoForensics**: Error level analysis

## 📊 Investigation Capabilities

### Surface Web OSINT
- **Enhanced Phone Investigation**: Multi-format support with Google libphonenumber integration
- **Email Analysis**: Address validation, breach checking, and social media discovery
- **IP Intelligence**: Geolocation, threat analysis, and network information
- **Name Investigation**: Social media profiles and professional network analysis
- **Interactive Help System**: Contextual tooltips, inline guidance, and country-specific help
- **Professional PDF Reporting**: Court-admissible documentation with comprehensive analysis

### Image Analysis & Forensics
- Multi-platform reverse image search (5+ engines)
- EXIF metadata extraction and analysis
- Cryptographic hash generation (MD5, SHA-1, SHA-256)
- Professional forensic tool integration
- Privacy risk assessment
- Evidence integrity verification

### Dark Web Investigation
- .onion URL analysis and scanning
- Dark web marketplace investigation
- Cryptocurrency transaction analysis
- Breach database searching
- Anonymous network analysis

### AI-Powered Assistance
- Intelligent investigation guidance
- OSINT methodology recommendations
- Automated research suggestions
- Investigation workflow optimization

## 🛡️ Security & Privacy

### Privacy Protection
- **Anonymous Mode**: All operations can be performed anonymously
- **Local Storage**: No cloud dependencies or data transmission
- **Secure Deletion**: Automatic cleanup of temporary files
- **Privacy Assessment**: Built-in privacy risk evaluation

### Evidence Integrity
- **Cryptographic Hashing**: SHA-256 verification for all evidence
- **Chain of Custody**: Professional evidence tracking
- **Audit Trails**: Comprehensive logging for legal compliance
- **Tamper Detection**: Integrity verification throughout investigation

### Legal Compliance
- **Open Source Transparency**: Complete code visibility
- **Professional Standards**: Follows industry investigation methodologies
- **Court-Admissible Reports**: Professional documentation standards
- **Ethical Guidelines**: Built-in ethical investigation practices

## 📚 Documentation

- **[User Guide](docs/user_guide.md)**: Comprehensive usage instructions
- **[Development Guide](docs/development_guide.md)**: Contribution guidelines
- **[Project Structure](PROJECT_STRUCTURE.md)**: Detailed architecture documentation

## 🧪 Testing

Run the test suite to ensure everything is working correctly:

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=src tests/

# Run specific test file
python -m pytest tests/test_core/test_config_manager.py
```

## 🤝 Contributing

We welcome contributions from the cybersecurity and OSINT community!

### How to Contribute
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Clone your fork
git clone https://github.com/yourusername/ciot-toolkit.git
cd ciot-toolkit

# Create virtual environment
python -m venv ciot-env
source ciot-env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8

# Run tests
python -m pytest tests/

# Run the application
python ciot.py
```

## ⚖️ Legal & Ethical Use

### Important Notice
The Cyber Investigation OSINT Toolkit is designed for **legitimate investigation purposes only**. Users must:

- ✅ Comply with all applicable laws and regulations
- ✅ Respect privacy rights and data protection laws
- ✅ Obtain proper authorization before investigating individuals
- ✅ Use the toolkit ethically and responsibly
- ✅ Follow professional investigation standards

### Prohibited Uses
- ❌ Stalking, harassment, or invasion of privacy
- ❌ Unauthorized access to systems or data
- ❌ Illegal surveillance or monitoring
- ❌ Malicious or harmful activities
- ❌ Violation of terms of service of investigated platforms

## 📞 Support & Community

### Getting Help
- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/yourusername/ciot-toolkit/issues)
- **Discussions**: Join community discussions on [GitHub Discussions](https://github.com/yourusername/ciot-toolkit/discussions)
- **Documentation**: Comprehensive guides in the `docs/` directory
- **Wiki**: Community-maintained wiki with tips and tutorials

### Professional Support
For enterprise deployments and professional support:
- Custom training and implementation
- Extended feature development
- Integration with existing security infrastructure
- Compliance and legal guidance

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Open Source Community**: For providing excellent free tools and libraries
- **OSINT Community**: For methodologies and best practices
- **Cybersecurity Professionals**: For feedback and feature requests
- **Digital Forensics Experts**: For forensic analysis techniques
- **Privacy Advocates**: For privacy-first design principles

## 🔮 Roadmap

### Upcoming Features
- **Advanced AI Integration**: Enhanced machine learning capabilities
- **Blockchain Analysis**: Cryptocurrency investigation tools
- **Mobile Device Analysis**: Smartphone and tablet investigation
- **Network Analysis**: Advanced network forensics
- **Collaborative Features**: Multi-investigator case sharing
- **API Integration**: RESTful API for automation

## 📈 Project Stats

![GitHub stars](https://img.shields.io/github/stars/yourusername/ciot-toolkit?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/ciot-toolkit?style=social)
![GitHub issues](https://img.shields.io/github/issues/yourusername/ciot-toolkit)
![GitHub pull requests](https://img.shields.io/github/issues-pr/yourusername/ciot-toolkit)

---

**🛡️ Cyber Investigation OSINT Toolkit - Professional OSINT Made Accessible**

*Empowering investigators with professional-grade tools while maintaining complete transparency and ethical standards.*# CIOT
