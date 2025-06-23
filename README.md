# Locust AI Agent

A comprehensive AI-powered solution for automating Locust performance testing in CI/CD pipelines with intelligent analysis using LLM APIs.

## Overview

The Locust AI Agent is a standalone module that provides automated performance testing capabilities with intelligent result analysis. It integrates seamlessly with Jenkins pipelines and can be used independently or as part of the larger SwarmTest application.

## Features

- **Automated Test Generation**: Create Locust scripts from JSON configurations
- **Headless Test Execution**: Run tests with configurable parameters
- **Intelligent Analysis**: LLM-powered result analysis with insights and recommendations
- **CI/CD Integration**: Jenkins pipeline support with artifact archiving
- **Flexible Configuration**: JSON-based scenario and test configuration
- **Comprehensive Reporting**: HTML and CSV report generation
- **Mock Mode**: Testing capabilities without LLM API dependencies

## Architecture

```
Locust_AI_Agent/
├── __init__.py              # Main package initialization
├── core/                    # Core testing components
│   ├── __init__.py
│   └── test_agent.py        # Main test agent implementation
├── analysis/                # Analysis components
│   ├── __init__.py
│   └── llm_analyzer.py      # LLM-based analysis
├── utils/                   # Utility components
│   ├── __init__.py
│   └── cli.py              # Command-line interface
├── examples/                # Example configurations
│   ├── sample_scenario.json
│   ├── sample_test_config.json
│   └── run_example.sh
├── Jenkinsfile             # Jenkins pipeline configuration
└── README.md               # This documentation
```

## Installation

### Prerequisites

- Python 3.8+
- Locust 2.0+
- requests library

### Setup

1. **Clone or copy the Locust_AI_Agent folder** to your project:
   ```bash
   cp -r Locust_AI_Agent /path/to/your/project/
   ```

2. **Install dependencies**:
   ```bash
   pip install locust requests
   ```

3. **Set up LLM API key** (optional):
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

## Usage

### Command Line Interface

The AI Agent provides a comprehensive CLI for running tests and managing configurations.

#### Basic Test Execution

```bash
# Run a test workflow
python -m Locust_AI_Agent run-test \
  --scenario-config scenario.json \
  --test-config test_config.json \
  --output-file results.json
```

#### With LLM Analysis

```bash
# Run with LLM analysis
python -m Locust_AI_Agent run-test \
  --scenario-config scenario.json \
  --test-config test_config.json \
  --use-llm \
  --llm-api-key your-api-key \
  --output-file results.json
```

#### Create Sample Configurations

```bash
# Generate sample configuration files
python -m Locust_AI_Agent create-samples
```

### Programmatic Usage

```python
from Locust_AI_Agent import LocustTestAgent, TestConfig, LLMAnalyzer

# Create test configuration
config = TestConfig(
    scenario_name="My API Test",
    host="https://api.example.com",
    users=10,
    spawn_rate=2,
    run_time="5m"
)

# Initialize agent
agent = LocustTestAgent()

# Run workflow
result = agent.run_complete_workflow(scenario_config, config)

# Analyze with LLM
llm_analyzer = LLMAnalyzer(api_key="your-api-key")
analysis = llm_analyzer.analyze_test_results(result["test_result"])
```

## Configuration

### Scenario Configuration

The scenario configuration defines the test steps and API calls:

```json
{
  "name": "API Test Scenario",
  "description": "Test description",
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
        "params": {
          "page": "1"
        },
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
    },
    {
      "id": 2,
      "type": "wait",
      "config": {
        "wait": 1
      }
    }
  ]
}
```

### Test Configuration

The test configuration defines execution parameters:

```json
{
  "scenario_name": "API Test",
  "host": "https://api.example.com",
  "users": 10,
  "spawn_rate": 2,
  "run_time": "5m",
  "min_wait": 1000,
  "max_wait": 5000,
  "output_dir": "test_reports",
  "generate_csv": true,
  "generate_html": true,
  "log_level": "INFO"
}
```

## Jenkins Integration

The AI Agent includes a comprehensive Jenkinsfile for CI/CD integration:

### Pipeline Features

- **Parameterized builds** with target host, API token, and environment selection
- **Automated test configuration** generation
- **LLM analysis** integration with credentials management
- **Artifact archiving** for reports and results
- **Performance threshold** validation
- **HTML report** generation and publishing

### Setup

1. **Add credentials** in Jenkins:
   - Go to Jenkins > Manage Jenkins > Credentials
   - Add a secret text credential with ID `openai-api-key`

2. **Configure the pipeline**:
   - Create a new Jenkins pipeline job
   - Point to the Jenkinsfile in the Locust_AI_Agent folder
   - Set build parameters as needed

3. **Run the pipeline**:
   - The pipeline will automatically generate test configurations
   - Execute tests with the specified parameters
   - Archive results and generate reports

### Pipeline Parameters

- `TARGET_HOST`: Target API host URL
- `API_TOKEN`: Authentication token
- `ENVIRONMENT`: Target environment (dev/staging/prod)
- `USE_LLM_ANALYSIS`: Enable LLM-powered analysis

## Examples

### Running the Example

```bash
# Navigate to the examples directory
cd Locust_AI_Agent/examples

# Run the example script
chmod +x run_example.sh
./run_example.sh
```

### Custom Test Scenario

1. **Create scenario configuration**:
   ```json
   {
     "name": "Custom API Test",
     "steps": [
       {
         "id": 1,
         "type": "api_call",
         "config": {
           "name": "Login",
           "method": "POST",
           "url": "/auth/login",
           "body": {
             "username": "testuser",
             "password": "testpass"
           }
         }
       }
     ]
   }
   ```

2. **Create test configuration**:
   ```json
   {
     "scenario_name": "Custom API Test",
     "host": "https://your-api.com",
     "users": 5,
     "run_time": "2m"
   }
   ```

3. **Run the test**:
   ```bash
   python -m Locust_AI_Agent run-test \
     --scenario-config custom_scenario.json \
     --test-config custom_test.json
   ```

## API Reference

### LocustTestAgent

Main class for test execution and management.

#### Methods

- `create_scenario_from_json(config)`: Create scenario from JSON
- `generate_script(scenario, config)`: Generate Locust script
- `execute_test(script_path, config)`: Execute test with parameters
- `analyze_results(result)`: Analyze test results
- `run_complete_workflow(scenario_config, test_config)`: Run complete workflow

### TestConfig

Configuration dataclass for test execution.

#### Fields

- `scenario_name`: Name of the test scenario
- `host`: Target host URL
- `users`: Number of concurrent users
- `spawn_rate`: User spawn rate
- `run_time`: Test duration
- `min_wait`/`max_wait`: Wait times between requests
- `output_dir`: Output directory for reports
- `generate_csv`/`generate_html`: Report format flags

### LLMAnalyzer

LLM-powered analysis component.

#### Methods

- `analyze_test_results(test_result, html_report_path)`: Analyze results with LLM
- `_fallback_analysis(test_result)`: Fallback analysis without LLM

## Troubleshooting

### Common Issues

1. **Locust not found**:
   ```bash
   pip install locust
   ```

2. **LLM API errors**:
   - Check API key configuration
   - Verify API endpoint URL
   - Use mock mode for testing: `--mock-llm`

3. **Permission errors**:
   ```bash
   chmod +x examples/run_example.sh
   ```

4. **Import errors**:
   ```bash
   export PYTHONPATH="${PYTHONPATH}:/path/to/Locust_AI_Agent"
   ```

### Debug Mode

Enable verbose logging for detailed output:

```bash
python -m Locust_AI_Agent run-test \
  --scenario-config scenario.json \
  --test-config test_config.json \
  --verbose
```

### Mock Mode

Test without LLM API dependencies:

```bash
python -m Locust_AI_Agent run-test \
  --scenario-config scenario.json \
  --test-config test_config.json \
  --use-llm \
  --mock-llm
```

## Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Use type hints and docstrings

## License

This project is part of the SwarmTest application and follows the same licensing terms.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the examples
3. Check the SwarmTest documentation
4. Create an issue in the project repository

## Documentation

- [Enhanced Features Guide](docs/ENHANCED_FEATURES_GUIDE.md) - Advanced features and capabilities
- [Random Selection Guide](docs/RANDOM_SELECTION_GUIDE.md) - Dynamic random selection features for realistic test scenarios
- [Jenkins Complete Guide](docs/JENKINS_COMPLETE_GUIDE.md) - Comprehensive Jenkins integration guide
- [Jenkins Setup Checklist](docs/JENKINS_SETUP_CHECKLIST.md) - Step-by-step Jenkins setup
- [Jenkins Environment Variables](docs/JENKINS_ENVIRONMENT_VARIABLES.md) - Environment variable configuration
- [Jenkins Parameters Quick Reference](docs/JENKINS_PARAMETERS_QUICK_REFERENCE.md) - Parameter configuration guide
- [Jenkins Pipeline Parameters Guide](docs/JENKINS_PIPELINE_PARAMETERS_GUIDE.md) - Advanced pipeline configuration 