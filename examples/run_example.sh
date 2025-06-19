#!/bin/bash

# Example script to run the Locust AI Agent
# This script demonstrates how to use the AI agent for automated testing

set -e

echo "=========================================="
echo "Locust AI Agent - Example Execution"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "sample_scenario_config.json" ]; then
    echo "Creating sample configuration files..."
    python -m Locust_AI_Agent create-samples
fi

echo "Running test workflow with sample configuration..."

# Run the test workflow
python -m Locust_AI_Agent run-test \
    --scenario-config sample_scenario_config.json \
    --test-config sample_test_config.json \
    --output-file test_results.json \
    --verbose

echo ""
echo "Test workflow completed!"
echo "Check test_results.json for detailed results."
echo "Check generated_scripts/ for the generated Locust script."
echo "Check generated_reports/ for HTML and CSV reports."

# Optional: Run with LLM analysis (requires API key)
if [ ! -z "$OPENAI_API_KEY" ]; then
    echo ""
    echo "Running with LLM analysis..."
    python -m Locust_AI_Agent run-test \
        --scenario-config sample_scenario_config.json \
        --test-config sample_test_config.json \
        --output-file test_results_with_llm.json \
        --use-llm \
        --llm-api-key "$OPENAI_API_KEY" \
        --verbose
    echo "LLM analysis completed! Check test_results_with_llm.json"
else
    echo ""
    echo "To run with LLM analysis, set OPENAI_API_KEY environment variable:"
    echo "export OPENAI_API_KEY=your-api-key-here"
    echo "Then run this script again."
fi

echo ""
echo "=========================================="
echo "Example execution completed!"
echo "==========================================" 