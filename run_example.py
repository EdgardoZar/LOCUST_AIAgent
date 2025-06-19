#!/usr/bin/env python3
"""
Simple script to run the Locust AI Agent example
"""
import sys
import os
import json

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from Locust_AI_Agent.core.test_agent import LocustTestAgent, TestConfig
    from Locust_AI_Agent.analysis.llm_analyzer import MockLLMAnalyzer
except ImportError as e:
    print(f"Import error: {e}")
    print("Trying alternative import...")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from core.test_agent import LocustTestAgent, TestConfig
    from analysis.llm_analyzer import MockLLMAnalyzer

def main():
    print("="*60)
    print("Locust AI Agent - Example Execution")
    print("="*60)
    
    # Load scenario configuration
    scenario_path = "examples/sample_scenario.json"
    test_config_path = "examples/sample_test_config.json"
    
    print(f"Loading scenario from: {scenario_path}")
    with open(scenario_path, 'r') as f:
        scenario_config = json.load(f)
    
    print(f"Loading test config from: {test_config_path}")
    with open(test_config_path, 'r') as f:
        test_config_data = json.load(f)
    
    # Create test configuration object
    test_config = TestConfig(
        scenario_name=test_config_data.get("scenario_name", scenario_config.get("name", "Unknown")),
        host=test_config_data.get("host", "http://localhost:8080"),
        users=test_config_data.get("users", 1),
        spawn_rate=test_config_data.get("spawn_rate", 1),
        run_time=test_config_data.get("run_time", "1m"),
        min_wait=test_config_data.get("min_wait", 1000),
        max_wait=test_config_data.get("max_wait", 5000),
        assertions=test_config_data.get("assertions", []),
        extract_variables=test_config_data.get("extract_variables", {}),
        headers=test_config_data.get("headers", {}),
        params=test_config_data.get("params", {}),
        body=test_config_data.get("body", {}),
        output_dir=test_config_data.get("output_dir", "test_reports"),
        generate_csv=test_config_data.get("generate_csv", True),
        generate_html=test_config_data.get("generate_html", True),
        log_level=test_config_data.get("log_level", "INFO")
    )
    
    print("Initializing test agent...")
    agent = LocustTestAgent(workspace_dir="test_workspace")
    
    print("Starting test workflow...")
    try:
        workflow_result = agent.run_complete_workflow(scenario_config, test_config)
        
        print("\n" + "="*60)
        print("TEST WORKFLOW SUMMARY")
        print("="*60)
        print(f"Scenario: {workflow_result['scenario_name']}")
        print(f"Success: {workflow_result['workflow_success']}")
        print(f"Script: {workflow_result['script_path']}")
        
        if workflow_result.get("html_report_path"):
            print(f"HTML Report: {workflow_result['html_report_path']}")
        
        if workflow_result.get("csv_report_path"):
            print(f"CSV Report: {workflow_result['csv_report_path']}")
        
        # Save results
        with open("test_results.json", "w") as f:
            json.dump(workflow_result, f, indent=2)
        print("Results saved to: test_results.json")
        
        print("="*60)
        
    except Exception as e:
        print(f"Error running workflow: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 