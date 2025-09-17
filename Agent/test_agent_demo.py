#!/usr/bin/env python3
"""
Demo script for the Locust Performance Testing Agent
Shows how to use the agent with different natural language requests
"""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Agent.locust_agent import LocustAgent

def demo_basic_usage():
    """Demo basic agent usage"""
    print("🚀 Demo: Basic Agent Usage")
    print("=" * 50)
    
    agent = LocustAgent()
    
    # Simple request
    request = "Test the Rick and Morty API with 10 users for 5 minutes"
    
    print(f"Request: {request}")
    result = agent.process_request(request)
    
    if result['success']:
        print(f"✅ Script generated: {result['script_path']}")
        print(f"📊 Parsed request: {result['parsed_request']}")
    else:
        print(f"❌ Error: {result['error']}")
    
    print()

def demo_advanced_usage():
    """Demo advanced agent usage with specific endpoints"""
    print("🚀 Demo: Advanced Agent Usage")
    print("=" * 50)
    
    agent = LocustAgent()
    
    # Advanced request with specific endpoints
    request = "Load test the e-commerce API with 20 users for 8 minutes, test /api/products and /api/orders endpoints, verify response time under 500ms"
    
    print(f"Request: {request}")
    result = agent.process_request(request)
    
    if result['success']:
        print(f"✅ Script generated: {result['script_path']}")
        print(f"📊 Parsed request: {result['parsed_request']}")
    else:
        print(f"❌ Error: {result['error']}")
    
    print()

def demo_authentication_testing():
    """Demo authentication testing"""
    print("🚀 Demo: Authentication Testing")
    print("=" * 50)
    
    agent = LocustAgent()
    
    # Authentication request
    request = "Test user login API with 15 users for 3 minutes, verify status code 200 and response time under 300ms"
    
    print(f"Request: {request}")
    result = agent.process_request(request)
    
    if result['success']:
        print(f"✅ Script generated: {result['script_path']}")
        print(f"📊 Parsed request: {result['parsed_request']}")
    else:
        print(f"❌ Error: {result['error']}")
    
    print()

def demo_stress_testing():
    """Demo stress testing"""
    print("🚀 Demo: Stress Testing")
    print("=" * 50)
    
    agent = LocustAgent()
    
    # Stress test request
    request = "Stress test the payment API with 50 users for 15 minutes, test order creation and payment processing"
    
    print(f"Request: {request}")
    result = agent.process_request(request)
    
    if result['success']:
        print(f"✅ Script generated: {result['script_path']}")
        print(f"📊 Parsed request: {result['parsed_request']}")
    else:
        print(f"❌ Error: {result['error']}")
    
    print()

def demo_custom_endpoints():
    """Demo custom endpoint testing"""
    print("🚀 Demo: Custom Endpoint Testing")
    print("=" * 50)
    
    agent = LocustAgent()
    
    # Custom endpoints request
    request = "Test specific endpoints /api/users and /api/products with 25 users for 6 minutes"
    
    print(f"Request: {request}")
    result = agent.process_request(request)
    
    if result['success']:
        print(f"✅ Script generated: {result['script_path']}")
        print(f"📊 Parsed request: {result['parsed_request']}")
    else:
        print(f"❌ Error: {result['error']}")
    
    print()

def demo_data_source_usage():
    """Demo data source usage"""
    print("🚀 Demo: Data Source Usage")
    print("=" * 50)
    
    agent = LocustAgent()
    
    # Request with data sources
    request = "Test user registration with 12 users for 4 minutes using users.csv data source"
    
    print(f"Request: {request}")
    result = agent.process_request(request)
    
    if result['success']:
        print(f"✅ Script generated: {result['script_path']}")
        print(f"📊 Parsed request: {result['parsed_request']}")
    else:
        print(f"❌ Error: {result['error']}")
    
    print()

def demo_error_handling():
    """Demo error handling"""
    print("🚀 Demo: Error Handling")
    print("=" * 50)
    
    agent = LocustAgent()
    
    # Invalid request
    request = "Test invalid endpoint with invalid parameters"
    
    print(f"Request: {request}")
    result = agent.process_request(request)
    
    if result['success']:
        print(f"✅ Script generated: {result['script_path']}")
    else:
        print(f"❌ Error handled gracefully: {result['error']}")
    
    print()

def show_available_data_sources():
    """Show available data sources"""
    print("📊 Available Data Sources")
    print("=" * 50)
    
    agent = LocustAgent()
    
    print("API Endpoints:")
    for endpoint in agent.data_sources.get('api_endpoints', [])[:5]:  # Show first 5
        print(f"  - {endpoint.get('endpoint', 'N/A')}: {endpoint.get('description', 'N/A')}")
    
    print("\nTest Scenarios:")
    for scenario in agent.data_sources.get('test_scenarios', [])[:5]:  # Show first 5
        print(f"  - {scenario.get('scenario_name', 'N/A')}: {scenario.get('description', 'N/A')}")
    
    print("\nLoad Profiles:")
    for profile in agent.data_sources.get('load_profiles', [])[:5]:  # Show first 5
        print(f"  - {profile.get('profile_name', 'N/A')}: {profile.get('description', 'N/A')}")
    
    print("\nAssertion Templates:")
    for assertion in agent.data_sources.get('assertion_templates', [])[:5]:  # Show first 5
        print(f"  - {assertion.get('assertion_type', 'N/A')}: {assertion.get('description', 'N/A')}")
    
    print()

def main():
    """Main demo function"""
    print("🎯 Locust Performance Testing Agent Demo")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Warning: OPENAI_API_KEY environment variable not set")
        print("   Set it with: export OPENAI_API_KEY='your-api-key'")
        print("   Some demos may fail without the API key")
        print()
    
    # Run demos
    try:
        show_available_data_sources()
        demo_basic_usage()
        demo_advanced_usage()
        demo_authentication_testing()
        demo_stress_testing()
        demo_custom_endpoints()
        demo_data_source_usage()
        demo_error_handling()
        
        print("✅ All demos completed successfully!")
        print("\n💡 Tips:")
        print("  - Check generated_scripts/ for created scripts")
        print("  - Review Agent/README.md for detailed usage")
        print("  - Customize data sources in Agent/*.csv files")
        print("  - Modify configurations in Agent/*.yaml files")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        print("   Check the troubleshooting section in README.md")

if __name__ == "__main__":
    main() 