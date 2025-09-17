#!/usr/bin/env python3
"""
Enhanced Demo script for the Locust Performance Testing Agent
Shows multi-API sequences with correlation and transaction naming
"""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Agent.enhanced_locust_agent import EnhancedLocustAgent

def demo_authentication_flow():
    """Demo authentication flow with correlation"""
    print("🔐 Demo: Authentication Flow with Correlation")
    print("=" * 60)
    
    agent = EnhancedLocustAgent()
    
    # Complex authentication request with correlation
    request = """
    Create a HomePage transaction named "UserAuthentication" with 15 users for 3 minutes.
    First call POST /api/auth/login with username and password, extract the auth_token from response.
    Then call GET /api/user/profile using the auth_token in Authorization header.
    Finally call POST /api/auth/logout using the same auth_token.
    Verify status code 200 for all calls and response time under 500ms.
    """
    
    print(f"Request: {request}")
    result = agent.process_enhanced_request(request)
    
    if result['success']:
        print(f"✅ Enhanced script generated: {result['script_path']}")
        print(f"📊 Transaction name: {result['parsed_request'].transaction_name}")
        print(f"🔗 API sequence: {len(result['parsed_request'].api_sequence)} steps")
        for i, step in enumerate(result['parsed_request'].api_sequence):
            print(f"   Step {i+1}: {step.name} - {step.method} {step.url}")
    else:
        print(f"❌ Error: {result['error']}")
    
    print()

def demo_ecommerce_checkout():
    """Demo e-commerce checkout flow"""
    print("🛒 Demo: E-commerce Checkout Flow")
    print("=" * 60)
    
    agent = EnhancedLocustAgent()
    
    # E-commerce checkout request
    request = """
    Create a CheckoutFlow transaction named "EcommerceCheckout" with 20 users for 5 minutes.
    First call GET /api/products to browse products, extract product_id from first product.
    Then call POST /api/cart with the product_id to add to cart, extract cart_id from response.
    Then call GET /api/cart/{cart_id} to view cart.
    Then call POST /api/orders with cart_id and payment details, extract order_id.
    Finally call GET /api/orders/{order_id} to confirm order.
    Verify all calls return status 200 and response time under 1 second.
    """
    
    print(f"Request: {request}")
    result = agent.process_enhanced_request(request)
    
    if result['success']:
        print(f"✅ Enhanced script generated: {result['script_path']}")
        print(f"📊 Transaction name: {result['parsed_request'].transaction_name}")
        print(f"🔗 API sequence: {len(result['parsed_request'].api_sequence)} steps")
        for i, step in enumerate(result['parsed_request'].api_sequence):
            print(f"   Step {i+1}: {step.name} - {step.method} {step.url}")
    else:
        print(f"❌ Error: {result['error']}")
    
    print()

def demo_rick_and_morty_sequence():
    """Demo Rick and Morty API sequence"""
    print("🌌 Demo: Rick and Morty API Sequence")
    print("=" * 60)
    
    agent = EnhancedLocustAgent()
    
    # Rick and Morty API sequence
    request = """
    Create a GetCharacters transaction named "RickAndMortyAPI" with 10 users for 4 minutes.
    First call GET /api/character?page=1 to get characters list, extract total_pages from info.
    Then call GET /api/character/1 to get specific character, extract character_name.
    Then call GET /api/character?name={character_name} to search for that character.
    Finally call GET /api/location/1 to get location details.
    Verify all calls return status 200 and response time under 300ms.
    """
    
    print(f"Request: {request}")
    result = agent.process_enhanced_request(request)
    
    if result['success']:
        print(f"✅ Enhanced script generated: {result['script_path']}")
        print(f"📊 Transaction name: {result['parsed_request'].transaction_name}")
        print(f"🔗 API sequence: {len(result['parsed_request'].api_sequence)} steps")
        for i, step in enumerate(result['parsed_request'].api_sequence):
            print(f"   Step {i+1}: {step.name} - {step.method} {step.url}")
    else:
        print(f"❌ Error: {result['error']}")
    
    print()

def demo_user_registration_flow():
    """Demo user registration flow"""
    print("👤 Demo: User Registration Flow")
    print("=" * 60)
    
    agent = EnhancedLocustAgent()
    
    # User registration request
    request = """
    Create a UserRegistration transaction named "UserSignup" with 12 users for 3 minutes.
    First call POST /api/users/register with user details, extract user_id from response.
    Then call POST /api/auth/verify-email with user_id to verify email.
    Then call POST /api/auth/login with credentials, extract auth_token.
    Then call GET /api/user/profile using auth_token to get profile.
    Finally call POST /api/user/complete-profile with additional details.
    Verify registration returns 201, others return 200, all response times under 800ms.
    """
    
    print(f"Request: {request}")
    result = agent.process_enhanced_request(request)
    
    if result['success']:
        print(f"✅ Enhanced script generated: {result['script_path']}")
        print(f"📊 Transaction name: {result['parsed_request'].transaction_name}")
        print(f"🔗 API sequence: {len(result['parsed_request'].api_sequence)} steps")
        for i, step in enumerate(result['parsed_request'].api_sequence):
            print(f"   Step {i+1}: {step.name} - {step.method} {step.url}")
    else:
        print(f"❌ Error: {result['error']}")
    
    print()

def demo_payment_processing():
    """Demo payment processing flow"""
    print("💳 Demo: Payment Processing Flow")
    print("=" * 60)
    
    agent = EnhancedLocustAgent()
    
    # Payment processing request
    request = """
    Create a PaymentProcessing transaction named "PaymentFlow" with 8 users for 6 minutes.
    First call GET /api/payment/methods to get available payment methods.
    Then call POST /api/payment/create-intent with order details, extract payment_intent_id.
    Then call POST /api/payment/confirm with payment_intent_id and payment method.
    Then call GET /api/payment/status/{payment_intent_id} to check payment status.
    Finally call POST /api/orders/update-status with order_id and payment status.
    Verify all calls return appropriate status codes and response time under 2 seconds.
    """
    
    print(f"Request: {request}")
    result = agent.process_enhanced_request(request)
    
    if result['success']:
        print(f"✅ Enhanced script generated: {result['script_path']}")
        print(f"📊 Transaction name: {result['parsed_request'].transaction_name}")
        print(f"🔗 API sequence: {len(result['parsed_request'].api_sequence)} steps")
        for i, step in enumerate(result['parsed_request'].api_sequence):
            print(f"   Step {i+1}: {step.name} - {step.method} {step.url}")
    else:
        print(f"❌ Error: {result['error']}")
    
    print()

def demo_search_and_filter():
    """Demo search and filter functionality"""
    print("🔍 Demo: Search and Filter Flow")
    print("=" * 60)
    
    agent = EnhancedLocustAgent()
    
    # Search and filter request
    request = """
    Create a SearchFilter transaction named "ProductSearch" with 15 users for 4 minutes.
    First call GET /api/products/search?q=laptop to search products, extract first_product_id.
    Then call GET /api/products/{product_id} to get product details.
    Then call GET /api/products/filter?category=electronics&price_min=100 to filter products.
    Then call GET /api/products/sort?sort_by=price&order=asc to sort results.
    Finally call GET /api/products/recommendations?product_id={product_id} for recommendations.
    Verify all calls return status 200 and response time under 600ms.
    """
    
    print(f"Request: {request}")
    result = agent.process_enhanced_request(request)
    
    if result['success']:
        print(f"✅ Enhanced script generated: {result['script_path']}")
        print(f"📊 Transaction name: {result['parsed_request'].transaction_name}")
        print(f"🔗 API sequence: {len(result['parsed_request'].api_sequence)} steps")
        for i, step in enumerate(result['parsed_request'].api_sequence):
            print(f"   Step {i+1}: {step.name} - {step.method} {step.url}")
    else:
        print(f"❌ Error: {result['error']}")
    
    print()

def demo_error_handling():
    """Demo error handling in enhanced agent"""
    print("⚠️ Demo: Error Handling")
    print("=" * 60)
    
    agent = EnhancedLocustAgent()
    
    # Invalid request
    request = "Create an invalid transaction with non-existent endpoints"
    
    print(f"Request: {request}")
    result = agent.process_enhanced_request(request)
    
    if result['success']:
        print(f"✅ Enhanced script generated: {result['script_path']}")
    else:
        print(f"❌ Error handled gracefully: {result['error']}")
    
    print()

def show_enhanced_capabilities():
    """Show enhanced agent capabilities"""
    print("🚀 Enhanced Agent Capabilities")
    print("=" * 60)
    
    print("✅ Multi-API Sequences:")
    print("   • Support for multiple API calls in sequence")
    print("   • Dependency management between steps")
    print("   • Variable extraction and correlation")
    print("   • Conditional logic based on responses")
    
    print("\n✅ Transaction Naming:")
    print("   • Custom transaction names (HomePage, GetCharacters, etc.)")
    print("   • Meaningful step names for better reporting")
    print("   • Transaction-level metrics and reporting")
    
    print("\n✅ Advanced Correlation:")
    print("   • Extract variables from API responses")
    print("   • Use extracted variables in subsequent calls")
    print("   • Dynamic parameter substitution")
    print("   • Header and body correlation")
    
    print("\n✅ Complex Scenarios:")
    print("   • Authentication flows")
    print("   • E-commerce checkout processes")
    print("   • Multi-step user journeys")
    print("   • Payment processing workflows")
    
    print("\n✅ Enhanced Assertions:")
    print("   • Step-specific assertions")
    print("   • Response time validation")
    print("   • Status code verification")
    print("   • JSON path validation")
    
    print()

def main():
    """Main enhanced demo function"""
    print("🎯 Enhanced Locust Performance Testing Agent Demo")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Warning: OPENAI_API_KEY environment variable not set")
        print("   Set it with: export OPENAI_API_KEY='your-api-key'")
        print("   Some demos may fail without the API key")
        print()
    
    # Run enhanced demos
    try:
        show_enhanced_capabilities()
        demo_authentication_flow()
        demo_ecommerce_checkout()
        demo_rick_and_morty_sequence()
        demo_user_registration_flow()
        demo_payment_processing()
        demo_search_and_filter()
        demo_error_handling()
        
        print("✅ All enhanced demos completed successfully!")
        print("\n💡 Enhanced Features:")
        print("  - Multi-API sequences with correlation")
        print("  - Transaction naming for better reporting")
        print("  - Variable extraction and reuse")
        print("  - Complex workflow support")
        print("  - Advanced error handling")
        print("\n🔧 Usage Examples:")
        print("  - Authentication flows with token correlation")
        print("  - E-commerce checkout with cart/order IDs")
        print("  - Multi-step user journeys")
        print("  - Payment processing workflows")
        
    except Exception as e:
        print(f"❌ Enhanced demo failed with error: {e}")
        print("   Check the troubleshooting section in README.md")

if __name__ == "__main__":
    main() 