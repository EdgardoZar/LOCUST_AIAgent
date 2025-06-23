"""
Command-line interface for the Locust AI Agent.
"""
import argparse
import json
import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any

from ..core.test_agent import LocustTestAgent, TestConfig
from ..analysis.llm_analyzer import LLMAnalyzer, MockLLMAnalyzer


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('ai_agent.log')
        ]
    )


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        raise ValueError(f"Error loading config file {config_path}: {e}")


def save_results(results: Dict[str, Any], output_path: str):
    """Save results to JSON file."""
    try:
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to: {output_path}")
    except Exception as e:
        print(f"Error saving results: {e}")


def run_test_workflow(args):
    """Run the complete test workflow."""
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Load scenario configuration
        logger.info(f"Loading scenario configuration from: {args.scenario_config}")
        scenario_config = load_config(args.scenario_config)
        
        # Load test configuration
        logger.info(f"Loading test configuration from: {args.test_config}")
        test_config_data = load_config(args.test_config)
        
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
        
        # Initialize test agent
        logger.info("Initializing test agent")
        agent = LocustTestAgent(workspace_dir=args.workspace_dir)
        
        # Run complete workflow
        logger.info("Starting test workflow")
        workflow_result = agent.run_complete_workflow(scenario_config, test_config)
        
        # Initialize LLM analyzer
        if args.use_llm:
            if args.mock_llm:
                logger.info("Using mock LLM analyzer")
                llm_analyzer = MockLLMAnalyzer()
            else:
                logger.info("Initializing LLM analyzer")
                llm_analyzer = LLMAnalyzer(
                    api_key=args.llm_api_key,
                    api_endpoint=args.llm_endpoint,
                    model=args.llm_model
                )
            
            # Perform LLM analysis
            logger.info("Performing LLM analysis")
            llm_analysis = llm_analyzer.analyze_test_results(
                workflow_result["test_result"],
                workflow_result.get("html_report_path")
            )
            workflow_result["llm_analysis"] = llm_analysis
        
        # Save results
        if args.output_file:
            save_results(workflow_result, args.output_file)
        
        # Print summary
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
        
        if workflow_result.get("llm_analysis"):
            analysis = workflow_result["llm_analysis"]
            print(f"\nLLM Analysis:")
            print(f"Performance Grade: {analysis.get('performance_grade', 'UNKNOWN')}")
            print(f"Summary: {analysis.get('summary', 'No summary available')}")
            
            if analysis.get("key_insights"):
                print(f"\nKey Insights:")
                for insight in analysis["key_insights"]:
                    print(f"  • {insight}")
            
            if analysis.get("recommendations"):
                print(f"\nRecommendations:")
                for rec in analysis["recommendations"]:
                    print(f"  • {rec}")
        
        print("="*60)
        
        # Exit with appropriate code
        if workflow_result['workflow_success']:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        print(f"ERROR: {e}")
        sys.exit(1)


def create_sample_configs(args):
    """Create sample configuration files."""
    scenario_config = {
        "name": "Sample API Test",
        "description": "A sample API test scenario",
        "min_wait": 1000,
        "max_wait": 5000,
        "steps": [
            {
                "id": 1,
                "type": "api_call",
                "config": {
                    "name": "Get Users",
                    "method": "GET",
                    "url": "/api/users",
                    "headers": {
                        "Content-Type": "application/json"
                    },
                    "params": {},
                    "body": None,
                    "extract": {
                        "user_count": "$.total"
                    },
                    "assertions": [
                        {
                            "type": "status_code",
                            "value": 200
                        }
                    ]
                }
            }
        ]
    }
    
    test_config = {
        "scenario_name": "Sample API Test",
        "host": "https://api.example.com",
        "users": 10,
        "spawn_rate": 2,
        "run_time": "5m",
        "min_wait": 1000,
        "max_wait": 5000,
        "assertions": [
            {
                "type": "status_code",
                "value": 200
            }
        ],
        "extract_variables": {
            "user_count": "$.total"
        },
        "headers": {
            "Content-Type": "application/json"
        },
        "params": {},
        "body": {},
        "output_dir": "test_reports",
        "generate_csv": True,
        "generate_html": True,
        "log_level": "INFO"
    }
    
    # Save sample files
    with open("sample_scenario_config.json", "w") as f:
        json.dump(scenario_config, f, indent=2)
    
    with open("sample_test_config.json", "w") as f:
        json.dump(test_config, f, indent=2)
    
    print("Sample configuration files created:")
    print("  - sample_scenario_config.json")
    print("  - sample_test_config.json")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI Agent for automated Locust testing in Jenkins pipelines",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run a test workflow
  python -m Locust_AI_Agent run-test \\
    --scenario-config scenario.json \\
    --test-config test_config.json \\
    --output-file results.json

  # Run with LLM analysis
  python -m Locust_AI_Agent run-test \\
    --scenario-config scenario.json \\
    --test-config test_config.json \\
    --use-llm \\
    --llm-api-key your-api-key

  # Create sample configurations
  python -m Locust_AI_Agent create-samples
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Run test command
    run_parser = subparsers.add_parser("run-test", help="Run a test workflow")
    run_parser.add_argument("--scenario-config", required=True, help="Path to scenario configuration JSON file")
    run_parser.add_argument("--test-config", required=True, help="Path to test configuration JSON file")
    run_parser.add_argument("--workspace-dir", help="Workspace directory for scripts and reports")
    run_parser.add_argument("--output-file", help="Path to save results JSON file")
    run_parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    # LLM options
    run_parser.add_argument("--use-llm", action="store_true", help="Enable LLM analysis")
    run_parser.add_argument("--mock-llm", action="store_true", help="Use mock LLM for testing")
    run_parser.add_argument("--llm-api-key", help="LLM API key")
    run_parser.add_argument("--llm-endpoint", help="LLM API endpoint")
    run_parser.add_argument("--llm-model", default="gpt-3.5-turbo", help="LLM model name")
    
    run_parser.set_defaults(func=run_test_workflow)
    
    # Create samples command
    samples_parser = subparsers.add_parser("create-samples", help="Create sample configuration files")
    samples_parser.set_defaults(func=create_sample_configs)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main() 