"""
Locust AI Agent - Automated Performance Testing with AI Analysis

A comprehensive solution for automating Locust performance testing in CI/CD pipelines
with intelligent analysis using LLM APIs.

Author: AI Assistant
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "AI Assistant"

from .core.test_agent import LocustTestAgent, TestConfig, TestResult
from .analysis.llm_analyzer import LLMAnalyzer, MockLLMAnalyzer
from .utils.cli import main

__all__ = [
    'LocustTestAgent',
    'TestConfig', 
    'TestResult',
    'LLMAnalyzer',
    'MockLLMAnalyzer',
    'main'
] 