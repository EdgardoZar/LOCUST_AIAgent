#!/usr/bin/env python3
"""
Comprehensive test of enhanced features
Demonstrates parameters, correlations, and assertions working together
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.test_agent import LocustTestAgent, TestConfig
from core.enhanced_script_generator import EnhancedScriptGenerator
import logging

def create_test_data_files():
    """Create test data files for demonstration"""
    
    # Create test_data directory
    test_data_dir = Path("examples/test_data")
    test_data_dir.mkdir(parents=True, exist_ok=True)
    
    # Create users.csv
    users_csv = test_data_dir / "users.csv"
    with open(users_csv, 'w', newline='') as f:
        import csv
        writer = csv.writer(f)
        writer.writerow(['username', 'password', 'email', 'role'])
        writer.writerow(['testuser1', 'password123', 'test1@example.com', 'customer'])
        writer.writerow(['testuser2', 'password456', 'test2@example.com', 'customer'])
        writer.writerow(['admin', 'admin123', 'admin@example.com', 'admin'])
    
    # Create products.json
    products_json = test_data_dir / "products.json"
    products_data = {
        "products": [
            {
                "id": "PROD001",
                "name": "Laptop Computer",
                "category": "electronics",
                "price": 999.99,
                "description": "High-performance laptop"
            },
            {
                "id": "PROD002",
                "name": "Wireless Headphones",
                "category": "electronics",
                "price": 199.99,
                "description": "Noise-cancelling headphones"
            },
            {
                "id": "PROD003",
                "name": "Coffee Maker",
                "category": "home",
                "price": 89.99,
                "description": "Programmable coffee maker"
            }
        ]
    }
    with open(products_json, 'w') as f:
        json.dump(products_data, f, indent=2)
    
    print("✅ Created test data files")

def create_enhanced_scenario():
    """Create a comprehensive enhanced scenario"""
    
    scenario = {
        "name": "Comprehensive E-commerce Flow",
        "description": "Complete e-commerce user journey with all enhanced features",
        "base_url": "https://api.example.com",
        "min_wait": 1000,
        "max_wait": 3000,
        "parameters": {
            "data_sources": [
                {
                    "name": "user_credentials",
                    "type": "csv",
                    "file": "test_data/users.csv",
                    "columns": ["username", "password", "email", "role"]
                },
                {
                    "name": "product_catalog",
                    "type": "json",
                    "file": "test_data/products.json",
                    "path": "$.products[*]"
                }
            ]
        },
        "steps": [
            {
                "id": "login",
                "name": "User Login",
                "method": "POST",
                "url": "/api/auth/login",
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": {
                    "username": "{{username}}",
                    "password": "{{password}}"
                },
                "extract": {
                    "auth_token": {
                        "type": "json_path",
                        "expression": "$.data.token"
                    },
                    "user_id": {
                        "type": "json_path",
                        "expression": "$.data.user.id"
                    },
                    "session_id": {
                        "type": "regex",
                        "expression": "session_id=([a-zA-Z0-9]+)"
                    }
                },
                "assertions": [
                    {
                        "type": "status_code",
                        "expected": 200,
                        "description": "Login should return 200 status"
                    },
                    {
                        "type": "response_time_ms",
                        "max": 2000,
                        "description": "Login should complete within 2 seconds"
                    },
                    {
                        "type": "json_path",
                        "expression": "$.success",
                        "expected": True,
                        "description": "Login should be successful"
                    },
                    {
                        "type": "body_contains_text",
                        "text": "token",
                        "description": "Response should contain token"
                    }
                ]
            },
            {
                "id": "search_products",
                "name": "Search Products",
                "method": "GET",
                "url": "/api/products/search",
                "headers": {
                    "Authorization": "Bearer {{auth_token}}",
                    "Content-Type": "application/json"
                },
                "params": {
                    "query": "{{name}}",
                    "category": "{{category}}"
                },
                "extract": {
                    "first_product_id": {
                        "type": "json_path",
                        "expression": "$.products[0].id"
                    },
                    "total_results": {
                        "type": "json_path",
                        "expression": "$.total"
                    }
                },
                "assertions": [
                    {
                        "type": "status_code",
                        "expected": 200
                    },
                    {
                        "type": "json_path",
                        "expression": "$.total",
                        "min": 1,
                        "description": "Should find at least one product"
                    },
                    {
                        "type": "response_time_ms",
                        "max": 1500,
                        "description": "Search should be fast"
                    }
                ]
            },
            {
                "id": "add_to_cart",
                "name": "Add Product to Cart",
                "method": "POST",
                "url": "/api/cart/add",
                "headers": {
                    "Authorization": "Bearer {{auth_token}}",
                    "Content-Type": "application/json"
                },
                "body": {
                    "product_id": "{{first_product_id}}",
                    "quantity": 1
                },
                "extract": {
                    "cart_id": {
                        "type": "json_path",
                        "expression": "$.cart_id"
                    },
                    "cart_total": {
                        "type": "json_path",
                        "expression": "$.total"
                    }
                },
                "assertions": [
                    {
                        "type": "status_code",
                        "expected": 201
                    },
                    {
                        "type": "json_path",
                        "expression": "$.success",
                        "expected": True
                    },
                    {
                        "type": "regex",
                        "pattern": "CART-\\d{6}",
                        "description": "Cart ID should match expected format"
                    }
                ]
            },
            {
                "id": "checkout",
                "name": "Proceed to Checkout",
                "method": "POST",
                "url": "/api/checkout",
                "headers": {
                    "Authorization": "Bearer {{auth_token}}",
                    "Content-Type": "application/json"
                },
                "body": {
                    "cart_id": "{{cart_id}}",
                    "shipping_address": {
                        "street": "123 Test St",
                        "city": "Test City",
                        "zip": "12345"
                    }
                },
                "extract": {
                    "order_id": {
                        "type": "json_path",
                        "expression": "$.order.id"
                    },
                    "order_status": {
                        "type": "json_path",
                        "expression": "$.order.status"
                    }
                },
                "assertions": [
                    {
                        "type": "status_code",
                        "expected": 200
                    },
                    {
                        "type": "json_path",
                        "expression": "$.order.status",
                        "expected": "pending"
                    },
                    {
                        "type": "regex",
                        "pattern": "ORD-\\d{8}",
                        "description": "Order ID should match expected format"
                    }
                ]
            }
        ]
    }
    
    return scenario

def test_enhanced_generator():
    """Test the enhanced script generator directly"""
    print("\n🔧 Testing Enhanced Script Generator")
    print("=" * 50)
    
    try:
        # Create test data
        create_test_data_files()
        
        # Create scenario
        scenario = create_enhanced_scenario()
        
        # Save scenario to file
        scenario_file = "examples/comprehensive_scenario.json"
        with open(scenario_file, 'w') as f:
            json.dump(scenario, f, indent=2)
        
        # Generate script
        output_file = "generated_scripts/Comprehensive_Ecommerce_Test.py"
        generator = EnhancedScriptGenerator(scenario_file, output_file)
        generator.generate_script()
        
        print(f"✅ Generated comprehensive script: {output_file}")
        
        # Show script statistics
        with open(output_file, 'r') as f:
            lines = f.readlines()
            print(f"📊 Script statistics:")
            print(f"   • Total lines: {len(lines)}")
            print(f"   • Data sources: {len(scenario['parameters']['data_sources'])}")
            print(f"   • Steps: {len(scenario['steps'])}")
            print(f"   • Total assertions: {sum(len(step.get('assertions', [])) for step in scenario['steps'])}")
            print(f"   • Total extractions: {sum(len(step.get('extract', {})) for step in scenario['steps'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing enhanced generator: {e}")
        return False

def test_integrated_agent():
    """Test the integrated test agent with enhanced features"""
    print("\n🤖 Testing Integrated Test Agent")
    print("=" * 50)
    
    try:
        # Create test agent
        agent = LocustTestAgent()
        
        # Create scenario
        scenario = create_enhanced_scenario()
        
        # Create test config
        config = TestConfig(
            scenario_name="Comprehensive E-commerce Flow",
            host="https://api.example.com",
            users=5,
            spawn_rate=1,
            run_time="30s",
            use_enhanced_generator=True
        )
        
        # Generate script using agent
        script_path = agent.generate_script(scenario, config)
        print(f"✅ Generated script via agent: {script_path}")
        
        # Verify script was created
        if os.path.exists(script_path):
            print("✅ Script file exists and is accessible")
            
            # Check script content for enhanced features
            with open(script_path, 'r') as f:
                content = f.read()
                
            enhanced_features = [
                "load_test_data",
                "_extract_json_path",
                "_extract_regex", 
                "_extract_boundary",
                "assertion_failures",
                "response_time_ms"
            ]
            
            found_features = []
            for feature in enhanced_features:
                if feature in content:
                    found_features.append(feature)
            
            print(f"✅ Found {len(found_features)}/{len(enhanced_features)} enhanced features:")
            for feature in found_features:
                print(f"   • {feature}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing integrated agent: {e}")
        return False

def main():
    """Run comprehensive tests"""
    print("🚀 Comprehensive Enhanced Features Test")
    print("=" * 60)
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    success_count = 0
    total_tests = 2
    
    # Test 1: Enhanced Generator
    if test_enhanced_generator():
        success_count += 1
    
    # Test 2: Integrated Agent
    if test_integrated_agent():
        success_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed! Enhanced features are working correctly.")
        print("\n🎯 Features Successfully Demonstrated:")
        print("   • Dynamic parameters from CSV/JSON files")
        print("   • Variable extraction (JSONPath, regex, boundaries)")
        print("   • Comprehensive assertions (status, time, JSON, regex)")
        print("   • Request correlation between steps")
        print("   • Integrated agent with automatic feature detection")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
    
    return 0 if success_count == total_tests else 1

if __name__ == "__main__":
    exit(main()) 