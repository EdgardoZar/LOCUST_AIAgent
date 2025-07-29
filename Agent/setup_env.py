#!/usr/bin/env python3
"""
Setup script for OpenAI API key configuration
"""

import os
import sys

def setup_openai_key():
    """Setup OpenAI API key"""
    print("🔑 OpenAI API Key Setup")
    print("=" * 40)
    
    # Check if key is already set
    if os.getenv('OPENAI_API_KEY'):
        print("✅ OPENAI_API_KEY is already set")
        return True
    
    print("To use the enhanced Locust agent, you need to set your OpenAI API key.")
    print()
    print("Options:")
    print("1. Set environment variable (recommended)")
    print("2. Create a .env file")
    print("3. Set it temporarily for this session")
    print()
    
    choice = input("Choose option (1-3): ").strip()
    
    if choice == "1":
        print("\n📝 Set the environment variable:")
        print("Windows PowerShell:")
        print('  $env:OPENAI_API_KEY="your-openai-api-key-here"')
        print("Windows Command Prompt:")
        print('  set OPENAI_API_KEY=your-openai-api-key-here')
        print("Linux/Mac:")
        print('  export OPENAI_API_KEY="your-openai-api-key-here"')
        print()
        print("⚠️  You'll need to set this every time you open a new terminal")
        print("   Or add it to your system environment variables")
        
    elif choice == "2":
        print("\n📝 Create a .env file in the project root:")
        print("OPENAI_API_KEY=your-openai-api-key-here")
        print()
        print("⚠️  Make sure to add .env to your .gitignore file")
        
    elif choice == "3":
        api_key = input("Enter your OpenAI API key: ").strip()
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
            print("✅ API key set for this session")
            return True
        else:
            print("❌ No API key provided")
            return False
    
    else:
        print("❌ Invalid choice")
        return False
    
    return False

def test_openai_connection():
    """Test OpenAI connection"""
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not set")
        return False
    
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Test with a simple request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        print("✅ OpenAI connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Locust AI Agent Setup")
    print("=" * 40)
    
    # Setup API key
    if setup_openai_key():
        # Test connection
        if test_openai_connection():
            print("\n🎉 Setup complete! You can now use the enhanced agent.")
            print("\nExample usage:")
            print('python Agent/enhanced_locust_agent.py "Create a HomePage transaction that calls /api/login, then /api/user/profile using the token from login, then /api/logout"')
        else:
            print("\n❌ Setup incomplete. Please check your API key.")
    else:
        print("\n⚠️  Please set your OpenAI API key before using the enhanced agent.")

if __name__ == "__main__":
    main() 