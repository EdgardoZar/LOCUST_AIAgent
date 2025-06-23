#!/usr/bin/env python3

from core.enhanced_script_generator import EnhancedScriptGenerator

def main():
    try:
        generator = EnhancedScriptGenerator(
            'examples/rick_and_morty_scenario.json', 
            'generated_scripts/Rick_and_Morty_API_Test_Enhanced.py'
        )
        generator.generate_script()
        print("Successfully generated Rick and Morty API test script!")
    except Exception as e:
        print(f"Error generating script: {e}")

if __name__ == "__main__":
    main() 