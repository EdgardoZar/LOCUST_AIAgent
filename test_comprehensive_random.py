#!/usr/bin/env python3

from core.enhanced_script_generator import EnhancedScriptGenerator

def main():
    try:
        # Test the comprehensive random scenario
        generator = EnhancedScriptGenerator(
            'examples/comprehensive_random_scenario.json', 
            'generated_scripts/Comprehensive_Random_Test.py'
        )
        generator.generate_script()
        print("Successfully generated Comprehensive Random Test script!")
        
        # Test the updated Rick and Morty scenario
        generator2 = EnhancedScriptGenerator(
            'examples/rick_and_morty_scenario.json', 
            'generated_scripts/Rick_and_Morty_API_Test_Enhanced_v2.py'
        )
        generator2.generate_script()
        print("Successfully generated enhanced Rick and Morty API test script!")
        
    except Exception as e:
        print(f"Error generating script: {e}")

if __name__ == "__main__":
    main() 