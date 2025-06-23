#!/usr/bin/env python3
"""
Test script for the enhanced script generator
Demonstrates the new features: parameters, correlations, and assertions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.enhanced_script_generator import EnhancedScriptGenerator
import logging

def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Test the enhanced generator
    scenario_file = "examples/enhanced_scenario.json"
    output_file = "generated_scripts/Enhanced_Ecommerce_API_Test.py"
    
    print("🚀 Testing Enhanced Script Generator")
    print("=" * 50)
    
    try:
        # Create generator instance
        generator = EnhancedScriptGenerator(scenario_file, output_file)
        
        # Generate the script
        print(f"📝 Generating script from: {scenario_file}")
        print(f"📄 Output file: {output_file}")
        
        generator.generate_script()
        
        print("✅ Script generated successfully!")
        print("\n🎯 Enhanced Features Demonstrated:")
        print("   • Dynamic parameters from CSV/JSON files")
        print("   • Variable extraction using JSONPath")
        print("   • Comprehensive assertions (status, time, JSON, regex)")
        print("   • Left/right boundary text extraction")
        print("   • Request correlation between steps")
        
        # Show a preview of the generated script
        print(f"\n📋 Preview of generated script ({output_file}):")
        print("-" * 50)
        
        with open(output_file, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:30]):  # Show first 30 lines
                print(f"{i+1:3d}: {line.rstrip()}")
        
        if len(lines) > 30:
            print("   ... (truncated)")
            
        print(f"\n📊 Total lines generated: {len(lines)}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 