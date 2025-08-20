#!/usr/bin/env python3
"""
Legal Compliance Manager for CIOT
Handles legal and ethical usage warnings and compliance guidance
"""

import json
from pathlib import Path
from datetime import datetime
import logging

class LegalComplianceManager:
    """Manages legal compliance and ethical usage guidance"""
    
    def __init__(self, config_dir="config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.compliance_file = self.config_dir / "legal_compliance.json"
        self.logger = logging.getLogger('CIOT_Legal')
        
        # Load compliance configuration
        self.compliance_config = self._load_compliance_config()
    
    def _load_compliance_config(self):
        """Load legal compliance configuration"""
        default_config = {
            "warnings": {
                "show_startup_warning": True,
                "show_investigation_warning": True,
                "require_acknowledgment": True,
                "warning_frequency_days": 30
            },
            "jurisdictions": {
                "default": "international",
                "supported": [
                    "international",
                    "united_states",
                    "european_union",
                    "united_kingdom",
                    "canada",
                    "australia",
                    "india"
                ]
            },
            "compliance_requirements": {
                "international": {
                    "name": "International Best Practices",
                    "key_points": [
                        "Obtain proper authorization before conducting investigations",
                        "Respect privacy rights and data protection laws",
                        "Use information only for legitimate purposes",
                        "Do not engage in harassment or stalking",
                        "Comply with terms of service of external platforms"
                    ],
                    "prohibited_activities": [
                        "Unauthorized surveillance",
                        "Identity theft or impersonation",
                        "Harassment or stalking",
                        "Accessing private accounts without permission",
                        "Violating platform terms of service"
                    ]
                },
                "united_states": {
                    "name": "United States Compliance",
                    "key_points": [
                        "Comply with Federal Trade Commission (FTC) guidelines",
                        "Respect Fair Credit Reporting Act (FCRA) requirements",
                        "Follow state privacy laws (CCPA, etc.)",
                        "Obtain proper licensing for professional investigations",
                        "Respect First Amendment and privacy rights"
                    ],
                    "prohibited_activities": [
                        "Pretexting for financial information",
                        "Unauthorized access to computer systems",
                        "Violating state private investigator licensing laws",
                        "Collecting information for discriminatory purposes",
                        "Bypassing platform security measures"
                    ]
                },
                "european_union": {
                    "name": "European Union (GDPR) Compliance",
                    "key_points": [
                        "Ensure lawful basis for data processing under GDPR",
                        "Respect data subject rights (access, rectification, erasure)",
                        "Implement data protection by design and default",
                        "Conduct Data Protection Impact Assessments when required",
                        "Report data breaches within 72 hours"
                    ],
                    "prohibited_activities": [
                        "Processing personal data without lawful basis",
                        "Transferring data outside EU without adequate protection",
                        "Ignoring data subject requests",
                        "Profiling for discriminatory purposes",
                        "Collecting excessive personal data"
                    ]
                },
                "united_kingdom": {
                    "name": "United Kingdom (UK GDPR) Compliance",
                    "key_points": [
                        "Follow UK GDPR and Data Protection Act 2018",
                        "Respect individual rights under UK data protection law",
                        "Ensure legitimate interests or other lawful basis",
                        "Register with ICO if required",
                        "Implement appropriate technical and organizational measures"
                    ],
                    "prohibited_activities": [
                        "Processing without lawful basis under UK GDPR",
                        "Ignoring individual rights requests",
                        "Failing to implement appropriate security measures",
                        "Using data for incompatible purposes",
                        "Excessive data collection or retention"
                    ]
                },
                "canada": {
                    "name": "Canada (PIPEDA) Compliance",
                    "key_points": [
                        "Follow Personal Information Protection and Electronic Documents Act",
                        "Obtain meaningful consent for personal information collection",
                        "Limit collection to identified purposes",
                        "Protect personal information with appropriate safeguards",
                        "Provide access to personal information upon request"
                    ],
                    "prohibited_activities": [
                        "Collecting personal information without consent",
                        "Using information for purposes not consented to",
                        "Inadequate protection of personal information",
                        "Refusing legitimate access requests",
                        "Retaining information longer than necessary"
                    ]
                },
                "australia": {
                    "name": "Australia (Privacy Act) Compliance",
                    "key_points": [
                        "Follow Australian Privacy Principles (APPs)",
                        "Ensure collection is lawful and necessary",
                        "Provide privacy notices and obtain consent",
                        "Implement reasonable security measures",
                        "Handle privacy complaints appropriately"
                    ],
                    "prohibited_activities": [
                        "Collecting personal information unlawfully",
                        "Using information for secondary purposes without consent",
                        "Inadequate security measures",
                        "Disclosing information without authorization",
                        "Ignoring privacy complaints"
                    ]
                },
                "india": {
                    "name": "India (Digital Personal Data Protection Act) Compliance",
                    "key_points": [
                        "Follow Digital Personal Data Protection Act 2023",
                        "Obtain valid consent for personal data processing",
                        "Respect data principal rights",
                        "Implement appropriate security safeguards",
                        "Report personal data breaches"
                    ],
                    "prohibited_activities": [
                        "Processing personal data without valid consent",
                        "Retaining data beyond necessary period",
                        "Transferring data outside India without safeguards",
                        "Ignoring data principal rights",
                        "Inadequate security measures"
                    ]
                }
            },
            "ethical_guidelines": {
                "core_principles": [
                    "Respect for persons and their privacy",
                    "Beneficence - do no harm",
                    "Justice and fairness in investigations",
                    "Transparency about capabilities and limitations",
                    "Accountability for actions and consequences"
                ],
                "best_practices": [
                    "Verify information from multiple sources",
                    "Consider the impact on investigated individuals",
                    "Use the least intrusive methods necessary",
                    "Protect confidentiality of investigation details",
                    "Document methodology and sources"
                ],
                "red_flags": [
                    "Requests for information about minors",
                    "Investigations for harassment purposes",
                    "Attempts to bypass security measures",
                    "Requests for illegal activities",
                    "Discrimination-based investigations"
                ]
            }
        }
        
        try:
            if self.compliance_file.exists():
                with open(self.compliance_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            else:
                self._save_compliance_config(default_config)
                return default_config
                
        except Exception as e:
            self.logger.error(f"Error loading compliance config: {e}")
            return default_config
    
    def _save_compliance_config(self, config=None):
        """Save compliance configuration"""
        if config is None:
            config = self.compliance_config
        
        try:
            with open(self.compliance_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving compliance config: {e}")
    
    def get_startup_warning(self, jurisdiction="international"):
        """Get startup legal warning for display"""
        if not self.compliance_config["warnings"]["show_startup_warning"]:
            return None
        
        compliance_info = self.compliance_config["compliance_requirements"].get(
            jurisdiction, 
            self.compliance_config["compliance_requirements"]["international"]
        )
        
        warning = {
            "title": "Legal and Ethical Usage Notice",
            "jurisdiction": compliance_info["name"],
            "message": """
IMPORTANT LEGAL NOTICE

This OSINT (Open Source Intelligence) tool is designed for legitimate investigative purposes only. 
By using this software, you acknowledge and agree to the following:

1. LEGAL COMPLIANCE: You will comply with all applicable laws and regulations in your jurisdiction.

2. ETHICAL USE: You will use this tool ethically and responsibly, respecting privacy rights and human dignity.

3. AUTHORIZED USE ONLY: You will only investigate information you are legally authorized to investigate.

4. NO HARASSMENT: You will not use this tool for harassment, stalking, or any malicious purposes.

5. PROFESSIONAL RESPONSIBILITY: If you are a professional investigator, you will comply with your professional standards and licensing requirements.

DISCLAIMER: This tool provides information from publicly available sources. The accuracy and completeness of information cannot be guaranteed. Users are responsible for verifying information and complying with all applicable laws.
            """,
            "key_points": compliance_info["key_points"],
            "prohibited_activities": compliance_info["prohibited_activities"],
            "requires_acknowledgment": self.compliance_config["warnings"]["require_acknowledgment"],
            "timestamp": datetime.now().isoformat()
        }
        
        return warning
    
    def get_investigation_warning(self, investigation_type="phone", jurisdiction="international"):
        """Get investigation-specific warning"""
        if not self.compliance_config["warnings"]["show_investigation_warning"]:
            return None
        
        warnings = {
            "phone": {
                "title": "Phone Number Investigation Warning",
                "message": """
Before proceeding with phone number investigation:

• Ensure you have legal authority or legitimate interest to investigate this number
• Consider privacy implications and data protection laws
• Do not use results for harassment, stalking, or malicious purposes
• Verify information from multiple sources before taking action
• Be aware that phone numbers may be recycled or ported between users

This investigation may collect personal information. Ensure compliance with applicable privacy laws.
                """,
                "specific_risks": [
                    "Phone numbers may belong to different people over time",
                    "Information may be outdated or inaccurate",
                    "Social media searches may reveal private information",
                    "Breach data may contain sensitive personal information"
                ]
            },
            "social_media": {
                "title": "Social Media Investigation Warning",
                "message": """
Social media investigation involves accessing publicly available information, but consider:

• Respect platform terms of service
• Do not attempt to access private or protected content
• Be aware of privacy settings and user expectations
• Consider the impact on individuals whose information you're viewing
• Document your methodology for accountability

Remember that social media information can be misleading or manipulated.
                """,
                "specific_risks": [
                    "Information may be fake or misleading",
                    "Profiles may be impersonation attempts",
                    "Privacy settings may change over time",
                    "Platform terms of service may restrict certain uses"
                ]
            },
            "breach_data": {
                "title": "Data Breach Investigation Warning",
                "message": """
Searching breach databases involves sensitive personal information:

• Only search for legitimate investigative purposes
• Do not access or use exposed credentials
• Be aware of legal restrictions on breach data use
• Consider notification requirements if you discover relevant breaches
• Protect any sensitive information you encounter

Breach data searches may reveal highly sensitive personal information.
                """,
                "specific_risks": [
                    "Breach data may contain passwords and sensitive information",
                    "Legal restrictions may apply to breach data use",
                    "Information may be highly sensitive or embarrassing",
                    "Notification requirements may apply in some jurisdictions"
                ]
            }
        }
        
        base_warning = warnings.get(investigation_type, warnings["phone"])
        
        # Add jurisdiction-specific information
        compliance_info = self.compliance_config["compliance_requirements"].get(
            jurisdiction,
            self.compliance_config["compliance_requirements"]["international"]
        )
        
        base_warning["jurisdiction"] = compliance_info["name"]
        base_warning["key_legal_points"] = compliance_info["key_points"][:3]  # Top 3 most relevant
        base_warning["timestamp"] = datetime.now().isoformat()
        
        return base_warning
    
    def check_ethical_concerns(self, investigation_request):
        """Check for potential ethical concerns in investigation request"""
        concerns = []
        red_flags = self.compliance_config["ethical_guidelines"]["red_flags"]
        
        # Check for common red flags
        request_lower = investigation_request.lower()
        
        if any(term in request_lower for term in ["child", "minor", "kid", "teenager"]):
            concerns.append({
                "level": "high",
                "type": "minor_investigation",
                "message": "Investigation may involve a minor. Special legal protections apply.",
                "guidance": "Ensure you have proper authority and consider child protection laws."
            })
        
        if any(term in request_lower for term in ["ex-", "former", "revenge", "get back"]):
            concerns.append({
                "level": "high",
                "type": "potential_harassment",
                "message": "Request may be motivated by personal conflict.",
                "guidance": "Ensure investigation is for legitimate purposes, not harassment."
            })
        
        if any(term in request_lower for term in ["hack", "break", "bypass", "crack"]):
            concerns.append({
                "level": "critical",
                "type": "illegal_activity",
                "message": "Request may involve illegal activities.",
                "guidance": "Do not attempt to bypass security measures or access private systems."
            })
        
        return concerns
    
    def log_compliance_acknowledgment(self, user_id, warning_type, jurisdiction):
        """Log user acknowledgment of compliance warnings"""
        acknowledgment = {
            "user_id": user_id,
            "warning_type": warning_type,
            "jurisdiction": jurisdiction,
            "timestamp": datetime.now().isoformat(),
            "ip_hash": "anonymized"  # In real implementation, hash the IP
        }
        
        self.logger.info(f"Compliance acknowledgment: {warning_type} for {jurisdiction}")
        return acknowledgment
    
    def get_jurisdiction_guidance(self, jurisdiction):
        """Get detailed guidance for a specific jurisdiction"""
        return self.compliance_config["compliance_requirements"].get(
            jurisdiction,
            self.compliance_config["compliance_requirements"]["international"]
        )
    
    def get_ethical_guidelines(self):
        """Get ethical guidelines for investigations"""
        return self.compliance_config["ethical_guidelines"]
    
    def should_show_warning(self, warning_type, last_shown=None):
        """Determine if warning should be shown based on frequency settings"""
        if not last_shown:
            return True
        
        frequency_days = self.compliance_config["warnings"]["warning_frequency_days"]
        if frequency_days <= 0:
            return False  # Warnings disabled
        
        try:
            last_shown_date = datetime.fromisoformat(last_shown)
            days_since = (datetime.now() - last_shown_date).days
            return days_since >= frequency_days
        except:
            return True  # Show warning if we can't parse the date
    
    def generate_compliance_report(self):
        """Generate compliance report for audit purposes"""
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "compliance_configuration": {
                "warnings_enabled": self.compliance_config["warnings"]["show_startup_warning"],
                "acknowledgment_required": self.compliance_config["warnings"]["require_acknowledgment"],
                "default_jurisdiction": self.compliance_config["jurisdictions"]["default"]
            },
            "supported_jurisdictions": self.compliance_config["jurisdictions"]["supported"],
            "ethical_guidelines_configured": bool(self.compliance_config["ethical_guidelines"]),
            "red_flag_detection_enabled": bool(self.compliance_config["ethical_guidelines"]["red_flags"])
        }
        
        return report