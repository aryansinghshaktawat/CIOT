# 🛡️ CIOT Quick Reference Guide

## 🚀 Quick Start
```bash
python3 ciot.py
```

## 📋 Tab Overview

| Tab | Purpose | Example Input | Key Features |
|-----|---------|---------------|--------------|
| 📊 Dashboard | Case management & overview | N/A | Case tracking, reports, system status |
| 🔍 Surface Web OSINT | Primary investigation tool | `john@example.com` | Email, phone, IP, name investigation |
| 🖼️ Image Analysis | Image forensics & reverse search | Upload image file | EXIF data, reverse search, hashes |
| 🕵️ Dark Web | .onion & crypto investigation | `3g2upl4pq6kufc4m.onion` | Onion scanner, crypto tracker |
| 🤖 AI Assistant | Investigation guidance | "How to investigate emails?" | Methodology, best practices |
| 🛠️ Additional Tools | Network & technical analysis | `google.com` | Port scan, DNS, traceroute |
| 🆔 Aadhaar Validator | Indian ID validation | `2234 5678 9012` | Verhoeff algorithm validation |

## 🔍 Surface Web OSINT Examples

### Enhanced Phone Investigation Features
- **Multi-Format Support**: `9876543210`, `+91 9876543210`, `(+91) 98765-43210` all work
- **Country Selection**: 10+ countries with specific validation rules
- **Interactive Help**: Tooltips, inline help panels, country-specific guidance
- **Error Handling**: Clear messages with format suggestions and correction tips
- **Comprehensive Analysis**: Technical, security, social, business, and pattern intelligence

### Email Investigation
```
Input: suspicious@example.com
Results: Validation, breach check, social media links, OSINT resources
```

### Enhanced Phone Investigation  
```
Input: +1 (555) 123-4567 (or any format: 5551234567, (555) 123-4567, etc.)
Country: Auto-detected or manually selected from 10+ countries
Results: 
• Technical intelligence (libphonenumber analysis)
• Security intelligence (spam/breach checking)
• Social intelligence (social media presence)
• Business intelligence (domain associations)
• Pattern intelligence (related numbers)
• Historical intelligence (change tracking)
• Confidence assessment (reliability scoring)
```

### IP Investigation
```
Input: 8.8.8.8
Results: Geolocation, ISP, threat intel, network analysis
```

### Name Investigation
```
Input: John Smith
Results: Social media, professional networks, public records
```

## 🖼️ Image Analysis Workflow

1. **Upload Image** → File analysis (size, format, dimensions)
2. **Full Analysis** → EXIF data, GPS, camera info, hashes
3. **Reverse Search** → Opens 5+ search engines automatically
4. **Forensic Tools** → Manipulation detection, error analysis

## 🛠️ Additional Tools Quick Commands

| Tool | Input Example | Purpose |
|------|---------------|---------|
| Port Scanner | `scanme.nmap.org` | Find open ports and services |
| DNS Lookup | `google.com` | Domain resolution and analysis |
| Traceroute | `8.8.8.8` | Network path analysis |
| Crypto Tracker | Bitcoin address | Transaction analysis |

## 🤖 AI Assistant Sample Questions

```
"How do I investigate a suspicious email address?"
"What tools should I use for social media investigation?"
"How can I verify if an image has been manipulated?"
"What's the best approach for phone number investigation?"
"How do I trace cryptocurrency transactions?"
```

## 📊 Professional Features

### Export Options
- **Surface Web**: PDF reports with legal disclaimers
- **Image Analysis**: Comprehensive forensic reports
- **All Tabs**: Professional documentation

### Status Indicators
- **Ready** - System ready for input
- **🔄 Processing** - Analysis in progress  
- **✅ Complete** - Analysis finished
- **❌ Error** - Issue encountered

### Global Info Button
- Click **"ℹ️ Tab Info"** for context-sensitive help
- Changes based on active tab
- Provides detailed usage instructions

## ⚖️ Legal & Ethical Guidelines

### ✅ Permitted Uses
- Authorized investigations
- Security research
- Academic purposes
- Legal compliance verification

### ❌ Prohibited Uses
- Stalking or harassment
- Unauthorized surveillance
- Privacy violations
- Malicious activities

## 🔒 Security Best Practices

1. **Verify Authorization** - Ensure legal right to investigate
2. **Document Everything** - Maintain professional records
3. **Cross-Reference** - Verify findings through multiple sources
4. **Respect Privacy** - Follow data protection laws
5. **Use Anonymously** - Enable privacy modes when appropriate

## 🚨 Emergency Procedures

### If Investigation Reveals Illegal Activity
1. **Stop Investigation** - Don't contaminate evidence
2. **Document Findings** - Export professional reports
3. **Contact Authorities** - Report through proper channels
4. **Preserve Evidence** - Maintain chain of custody

### If System Issues Occur
1. **Check Status Bar** - Look for error messages
2. **Review Logs** - Check `logs/` directory
3. **Restart Application** - Close and reopen if needed
4. **Verify Internet** - Ensure connectivity for OSINT tools

## 📞 Support Resources

- **Built-in Help**: ℹ️ Tab Info button
- **Documentation**: `docs/` directory
- **User Guide**: `COMPLETE_USER_GUIDE.md`
- **Project Structure**: `PROJECT_STRUCTURE.md`

---

**Remember**: CIOT is designed for legitimate investigation purposes only. Always ensure proper authorization and follow legal/ethical guidelines.