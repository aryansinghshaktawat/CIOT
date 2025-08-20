# 🛠️ CIOT Troubleshooting Guide

## Common Issues and Solutions

### 📱 Enhanced Phone Investigation Issues

#### Issue: "Invalid phone format for [Country]"

**Symptoms:**
- Red error message appears after entering phone number
- Investigation doesn't start
- Format suggestions are shown

**Solutions:**
1. **Check Country Selection**
   - Ensure the selected country matches the phone number
   - Try "Auto-Detect" if unsure about the country

2. **Try Different Formats**
   ```
   ✅ Try these variations:
   • +91 9876543210 (with country code)
   • 9876543210 (local format)
   • 919876543210 (without plus sign)
   • 09876543210 (with leading zero)
   ```

3. **Remove Special Characters**
   - Remove spaces, dashes, brackets: `(+91) 987-654-3210` → `919876543210`
   - Keep only numbers and plus sign

4. **Use Help Resources**
   - Click the ❓ button for country-specific examples
   - Toggle the 💡 Help panel for quick tips
   - Check the format guidance text

#### Issue: "No investigation results" or "Limited data available"

**Symptoms:**
- Investigation completes but shows minimal information
- API calls fail or return empty results
- Low confidence scores

**Possible Causes:**
- Number is inactive or doesn't exist
- Privacy settings block information access
- Regional restrictions on data availability
- API rate limits or temporary service issues
- Network connectivity problems

**Solutions:**
1. **Verify Number Validity**
   - Confirm the number is active and correct
   - Try calling/texting the number (if appropriate and legal)
   - Check for typos in the input

2. **Check Network Connection**
   - Ensure stable internet connection
   - Try investigation at different times
   - Check if firewall is blocking API calls

3. **Review Privacy Considerations**
   - Some numbers have enhanced privacy settings
   - Business numbers may have more public information
   - Consider legal and ethical limitations

4. **Try Alternative Methods**
   - Use different investigation types (email, name)
   - Cross-reference with other OSINT tools
   - Manual verification through public directories

#### Issue: Country selection problems

**Symptoms:**
- Desired country not in dropdown list
- Parsing fails even with correct format
- Country-specific features not working

**Solutions:**
1. **Use Auto-Detect Mode**
   - Select "Auto-Detect" from country dropdown
   - Include full international format with country code

2. **Try Similar Countries**
   - Use neighboring countries with similar formats
   - Check if the number format matches available countries

3. **Manual Format Adjustment**
   - Research the correct international format
   - Use online phone number format guides
   - Include country code explicitly

### 🖼️ Image Analysis Issues

#### Issue: "Image upload failed" or "Analysis failed"

**Solutions:**
1. **Check File Format**
   - Supported: JPG, PNG, GIF, BMP, TIFF
   - Avoid corrupted or unusual formats

2. **File Size Limits**
   - Keep images under 10MB
   - Compress large images if necessary

3. **Network Issues**
   - Check internet connection for reverse search
   - Try uploading smaller images first

#### Issue: "No reverse search results"

**Solutions:**
1. **Image Quality**
   - Use high-quality, clear images
   - Avoid heavily edited or filtered images

2. **Try Different Search Engines**
   - Results vary between Google, Yandex, TinEye
   - Some engines work better for specific image types

### 🕵️ Dark Web Investigation Issues

#### Issue: ".onion URL not accessible"

**Solutions:**
1. **Tor Browser Required**
   - Install Tor browser for .onion access
   - Ensure Tor is running properly

2. **Service Availability**
   - .onion services may be temporarily down
   - Try accessing at different times

3. **URL Verification**
   - Double-check .onion URL spelling
   - Ensure URL is still active

### 🤖 AI Assistant Issues

#### Issue: "No AI response" or "Service unavailable"

**Solutions:**
1. **Try Different Service Types**
   - Switch between Free AI Chat, Offline Analysis, Web Search
   - Each service has different capabilities

2. **Check Question Format**
   - Use clear, specific questions
   - Avoid overly complex or ambiguous queries

3. **Network Connectivity**
   - Ensure internet connection for online services
   - Offline Analysis works without internet

### 🛠️ Additional Tools Issues

#### Issue: Port scanner or DNS lookup fails

**Solutions:**
1. **Target Accessibility**
   - Ensure target host is online and accessible
   - Check if target blocks scanning attempts

2. **Network Configuration**
   - Check firewall settings
   - Ensure network allows outbound connections

3. **Rate Limiting**
   - Wait between scans to avoid rate limits
   - Use different targets for testing

### 🆔 Aadhaar Validator Issues

#### Issue: "Invalid Aadhaar number" for valid numbers

**Solutions:**
1. **Format Check**
   - Use 12-digit format: 1234 5678 9012
   - Remove spaces and special characters if needed

2. **Validation Algorithm**
   - System uses official Verhoeff algorithm
   - Some test numbers may not pass validation

## General Troubleshooting Steps

### 1. Basic Diagnostics

**Check System Requirements:**
- Python 3.8+ installed
- All dependencies from requirements.txt
- Stable internet connection
- Sufficient disk space

**Restart Application:**
```bash
# Close application completely
# Restart with:
python ciot.py
```

### 2. Clear Cache and Temporary Files

**Clear Browser Cache:**
- Close all browser windows opened by CIOT
- Clear browser cache and cookies
- Restart browser

**Clear Application Cache:**
```bash
# Remove temporary files (if any)
rm -rf temp/
rm -rf cache/
```

### 3. Check Logs

**Application Logs:**
- Check `logs/` directory for error messages
- Look for recent timestamps matching your issue
- Note any API errors or connection failures

**Error Message Analysis:**
- Copy exact error messages
- Note when the error occurs
- Document steps to reproduce

### 4. Network Diagnostics

**Test Internet Connection:**
```bash
# Test basic connectivity
ping google.com

# Test DNS resolution
nslookup google.com
```

**Check API Accessibility:**
- Try accessing API endpoints manually
- Check if corporate firewall blocks requests
- Test from different network if possible

### 5. Update and Reinstall

**Update Dependencies:**
```bash
pip install --upgrade -r requirements.txt
```

**Reinstall Application:**
```bash
# Backup your data first
cp -r data/ data_backup/

# Reinstall
git pull origin main
pip install -r requirements.txt
```

## Performance Optimization

### Improve Investigation Speed

1. **Network Optimization**
   - Use wired connection instead of WiFi
   - Close bandwidth-heavy applications
   - Investigate during off-peak hours

2. **System Resources**
   - Close unnecessary applications
   - Ensure sufficient RAM available
   - Use SSD storage if possible

3. **API Efficiency**
   - Avoid rapid successive investigations
   - Use specific country selection for phone numbers
   - Cache results when possible

### Reduce Error Rates

1. **Input Validation**
   - Double-check input formats
   - Use help resources for guidance
   - Validate inputs before investigation

2. **Systematic Approach**
   - Follow recommended workflows
   - Document successful methods
   - Learn from error patterns

## Getting Additional Help

### Built-in Help Resources

1. **Tab Info Button (ℹ️)**
   - Context-sensitive help for each tab
   - Updated information for current features

2. **Tooltips and Help Panels**
   - Hover over UI elements for quick tips
   - Use inline help panels for detailed guidance

3. **Documentation Files**
   - README.md: Installation and overview
   - COMPLETE_USER_GUIDE.md: Comprehensive usage guide
   - ENHANCED_PHONE_INVESTIGATION_USER_GUIDE.md: Phone investigation specifics
   - QUICK_REFERENCE.md: Quick command reference

### Reporting Issues

**Before Reporting:**
1. Check this troubleshooting guide
2. Try the suggested solutions
3. Document the exact steps to reproduce
4. Note your system configuration

**Information to Include:**
- Operating system and version
- Python version
- Exact error messages
- Steps to reproduce the issue
- Screenshots if helpful
- Log file excerpts (remove sensitive data)

### Community Resources

- Check existing issues and solutions
- Search documentation for similar problems
- Review example investigations and use cases
- Follow best practices and legal guidelines

---

**Remember**: Most issues can be resolved by following systematic troubleshooting steps. Always ensure you have proper authorization for any investigations and follow legal/ethical guidelines.