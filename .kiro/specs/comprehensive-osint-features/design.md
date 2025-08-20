# Design Document

## Overview

The CIOT (Cyber Investigation & OSINT Toolkit) is a comprehensive desktop application built using CustomTkinter that provides professional-grade OSINT capabilities across four main functional areas. The application follows a modular tab-based architecture where each tab represents a specialized investigation domain. The design emphasizes user experience, professional reporting, and ethical compliance while providing powerful investigation tools for cybersecurity professionals, law enforcement, and authorized investigators.

## Architecture

### High-Level Architecture

The application follows a layered architecture pattern:

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐ │
│  │Surface Web  │ │ Dark Web    │ │AI Assistant │ │Add'l   │ │
│  │OSINT Tab    │ │ OSINT Tab   │ │Tab          │ │Tools   │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                     Service Layer                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐ │
│  │OSINT        │ │ Dark Web    │ │AI Response  │ │Network │ │
│  │Services     │ │ Tools       │ │Generator    │ │Tools   │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                     Data Layer                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐ │
│  │External     │ │ Local       │ │Config       │ │Report  │ │
│  │APIs         │ │ Tools       │ │Manager      │ │Export  │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

1. **Main Application (CIOTMainApp)**: Central controller managing the tabbed interface, configuration, and application lifecycle
2. **Tab Modules**: Independent modules for each investigation domain
3. **Service Layer**: Business logic and tool integration services
4. **Utility Layer**: Common functionality for API calls, file operations, and reporting

## Components and Interfaces

### 1. Surface Web OSINT Tab (EnhancedProfileLookupTab)

**Purpose**: Comprehensive surface web intelligence gathering for various target types

**Key Components**:
- `LookupTypeSelector`: Dropdown for selecting investigation type (Full Name, Phone, Email, IP)
- `TargetInputField`: Validated input field with type-specific formatting
- `OSINTSearchEngine`: Core search logic generator
- `ResultsDisplayPanel`: Professional results presentation
- `PDFExportManager`: Report generation system

**Interface Design**:
```python
class EnhancedProfileLookupTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs)
    def setup_lookup_controls(self)
    def setup_results_display(self)
    def perform_full_name_lookup(self, name: str) -> Dict
    def perform_phone_lookup(self, phone: str) -> Dict
    def perform_email_lookup(self, email: str) -> Dict
    def perform_ip_lookup(self, ip: str) -> Dict
    def generate_osint_links(self, target: str, lookup_type: str) -> List[str]
    def export_to_pdf(self, results: Dict) -> bool
```

**Data Flow**:
1. User selects lookup type and enters target
2. Input validation based on type (email format, IP format, etc.)
3. Generate comprehensive OSINT search links
4. Execute searches and aggregate results
5. Display formatted results with categorization
6. Provide export functionality

### 2. Dark Web OSINT Tab (DarkWebTab)

**Purpose**: Specialized dark web investigation using professional tools

**Key Components**:
- `ToolSelector`: Dropdown for selecting dark web tools (TorBot, h8mail, OnionScan, etc.)
- `ToolConfigurationPanel`: Dynamic options based on selected tool
- `TorServiceManager`: Tor connectivity and service management
- `DarkWebToolExecutor`: Tool execution and result processing
- `SecurityWarningSystem`: OPSEC guidance and warnings

**Interface Design**:
```python
class DarkWebTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs)
    def setup_tool_selection(self)
    def setup_dynamic_options(self, tool_name: str)
    def execute_torbot(self, url: str, options: Dict) -> Dict
    def execute_h8mail(self, email: str, options: Dict) -> Dict
    def execute_onionscan(self, url: str, options: Dict) -> Dict
    def execute_bitcoin_analysis(self, address: str, options: Dict) -> Dict
    def manage_tor_service(self) -> bool
    def export_results(self, format: str) -> bool
```

**Tool Integration Architecture**:
- Each tool has a dedicated executor class
- Standardized result format for consistent display
- Error handling and fallback mechanisms
- Progress tracking for long-running operations

### 3. AI Assistant Tab (AIAssistantTab)

**Purpose**: Intelligent OSINT guidance and methodology assistance

**Key Components**:
- `ServiceSelector`: AI service type selection (Free AI Chat, Offline Analysis, Web Search)
- `QuestionProcessor`: Natural language question analysis
- `ResponseGenerator`: Context-aware response generation
- `MethodologyDatabase`: OSINT best practices and techniques
- `LegalComplianceAdvisor`: Ethical and legal guidance system

**Interface Design**:
```python
class AIAssistantTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs)
    def setup_service_selection(self)
    def setup_question_interface(self)
    def process_question(self, question: str, service: str) -> str
    def generate_osint_response(self, question: str) -> str
    def perform_offline_analysis(self, question: str) -> Dict
    def generate_web_search_guidance(self, question: str) -> List[str]
    def provide_legal_guidance(self, topic: str) -> str
```

**Response Generation System**:
- Keyword-based topic detection
- Methodology templates for common scenarios
- Legal and ethical considerations integration
- Resource recommendation engine

### 4. Additional Tools Tab (AdditionalToolsTab)

**Purpose**: Specialized technical tools organized by category

**Key Components**:
- `NetworkToolsPanel`: Port scanner, DNS lookup, traceroute
- `SocialMediaToolsPanel`: Username search, social analyzer, profile scraper
- `CryptoToolsPanel`: Blockchain explorer, wallet analyzer, transaction tracker
- `ToolExecutionEngine`: Unified tool execution framework
- `ResultsAggregator`: Multi-tool result compilation

**Interface Design**:
```python
class AdditionalToolsTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs)
    def setup_tool_categories(self)
    def setup_network_tools(self)
    def setup_social_media_tools(self)
    def setup_crypto_tools(self)
    def execute_port_scan(self, target: str) -> Dict
    def execute_dns_lookup(self, domain: str) -> Dict
    def execute_traceroute(self, target: str) -> Dict
    def execute_username_search(self, username: str) -> Dict
    def execute_blockchain_analysis(self, address: str) -> Dict
```

## Data Models

### Investigation Session Model
```python
@dataclass
class InvestigationSession:
    session_id: str
    start_time: datetime
    investigator: str
    target_info: Dict[str, Any]
    tools_used: List[str]
    findings: List[Finding]
    status: SessionStatus
    legal_authorization: bool
```

### Finding Model
```python
@dataclass
class Finding:
    finding_id: str
    timestamp: datetime
    tool_used: str
    target: str
    result_type: str
    data: Dict[str, Any]
    confidence_level: float
    verified: bool
    notes: str
```

### Tool Configuration Model
```python
@dataclass
class ToolConfig:
    tool_name: str
    version: str
    options: Dict[str, Any]
    dependencies: List[str]
    security_level: SecurityLevel
    legal_requirements: List[str]
```

### Export Report Model
```python
@dataclass
class ExportReport:
    report_id: str
    session_id: str
    generation_time: datetime
    format: str  # PDF, JSON, HTML
    content: Dict[str, Any]
    metadata: ReportMetadata
    legal_disclaimers: List[str]
```

## Error Handling

### Error Categories
1. **Input Validation Errors**: Invalid formats, missing required fields
2. **Network Errors**: API failures, connectivity issues, timeouts
3. **Tool Execution Errors**: Missing dependencies, permission issues
4. **Export Errors**: File system issues, formatting problems
5. **Security Errors**: Unauthorized access attempts, suspicious activity

### Error Handling Strategy
```python
class ErrorHandler:
    def handle_validation_error(self, error: ValidationError) -> UserMessage
    def handle_network_error(self, error: NetworkError) -> UserMessage
    def handle_tool_error(self, error: ToolExecutionError) -> UserMessage
    def log_error(self, error: Exception, context: Dict) -> None
    def notify_user(self, message: UserMessage) -> None
```

### Graceful Degradation
- Fallback to alternative tools when primary tools fail
- Offline mode for tools that don't require internet connectivity
- Cached results for repeated queries
- Manual tool links when automated execution fails

## Testing Strategy

### Unit Testing
- Individual tool execution functions
- Input validation logic
- Data processing and formatting
- Export functionality

### Integration Testing
- Tab switching and state management
- Tool chain execution (multiple tools in sequence)
- API integration and error handling
- File system operations

### User Acceptance Testing
- Complete investigation workflows
- Professional use case scenarios
- Performance under realistic loads
- Accessibility and usability

### Security Testing
- Input sanitization and validation
- API key and credential handling
- Network security and proxy support
- Data privacy and retention

## Security Considerations

### Data Protection
- No persistent storage of sensitive investigation data
- Secure handling of API keys and credentials
- Memory cleanup after tool execution
- Encrypted configuration storage

### Network Security
- Proxy support for anonymized investigations
- TLS/SSL verification for all external connections
- Rate limiting to prevent service abuse
- User agent rotation for web scraping

### Operational Security (OPSEC)
- Security warnings for dark web tools
- VPN requirement notifications
- Tor service integration and management
- Evidence handling best practices

### Legal Compliance
- Built-in legal disclaimers and warnings
- Authorization requirement reminders
- Data retention policy guidance
- Jurisdiction-specific compliance notes

## Performance Optimization

### Asynchronous Operations
- Threading for long-running tool execution
- Progress indicators for user feedback
- Cancellation support for running operations
- Resource cleanup and memory management

### Caching Strategy
- DNS lookup result caching
- API response caching with TTL
- Tool configuration caching
- Recent search history (optional)

### Resource Management
- Connection pooling for HTTP requests
- Lazy loading of tab content
- Memory-efficient result storage
- Automatic cleanup of temporary files

## Deployment and Configuration

### Application Structure
```
CIOT-Toolkit/
├── main.py                 # Application entry point
├── gui/                    # GUI modules
│   ├── enhanced_profile_gui.py
│   ├── darkweb_tab.py
│   ├── ai_assistant_tab.py
│   └── additional_tools_tab.py
├── services/               # Business logic services
│   ├── osint_service.py
│   ├── darkweb_service.py
│   └── ai_service.py
├── utils/                  # Utility functions
│   ├── validators.py
│   ├── exporters.py
│   └── security.py
├── config/                 # Configuration files
│   └── ciot_config.json
├── reports/                # Generated reports
├── logs/                   # Application logs
└── requirements.txt        # Dependencies
```

### Configuration Management
- JSON-based configuration with validation
- Environment variable support for sensitive data
- User-specific settings and preferences
- Tool-specific configuration profiles

### Dependency Management
- Clear separation of required vs optional dependencies
- Graceful handling of missing optional tools
- Installation guidance for external tools
- Version compatibility checking

This design provides a robust, scalable, and maintainable foundation for implementing comprehensive OSINT capabilities while maintaining professional standards for security, legal compliance, and user experience.