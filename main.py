#!/usr/bin/env python3
"""
CIOT Toolkit - Main Application Launcher
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    from core.application import main
    main()