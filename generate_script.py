#!/usr/bin/env python3
"""
Simple script to generate a Locust test script
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.enhanced_script_generator import EnhancedScriptGenerator

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_script.py <scenario_file> <output_file>")
        sys.exit(1)
    
    scenario_file = sys.argv[1]
    output_file = sys.argv[2]
    
    print(f"Generating script from {scenario_file} to {output_file}")
    
    try:
        generator = EnhancedScriptGenerator(scenario_file, output_file)
        generator.generate_script()
        print(f"Script generated successfully: {output_file}")
    except Exception as e:
        print(f"Error generating script: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 