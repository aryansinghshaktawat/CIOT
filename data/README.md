# CIOT Data Directory

This directory contains all investigation data and is organized as follows:

## Structure

- **cases/**: Investigation case files and metadata
- **evidence/**: Evidence files with cryptographic verification
- **reports/**: Generated investigation reports (HTML, PDF)
- **exports/**: Exported data in various formats

## Security

All data in this directory is:
- Stored locally only
- Protected with file system permissions
- Includes cryptographic integrity verification
- Follows professional chain of custody standards

## Retention

Data retention follows the configured policy in the application settings.
Default retention period is 365 days for completed investigations.