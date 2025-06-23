#!/usr/bin/env python3
"""
Test script for Locust AI Agent CLI
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Locust_AI_Agent.utils.cli import main

if __name__ == "__main__":
    main() 