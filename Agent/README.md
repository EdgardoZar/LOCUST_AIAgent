# Locust Performance Testing Agent

An AI-powered agent that generates Locust performance test scripts from natural language requests using OpenAI's GPT models.

## 🚀 Features

- **Natural Language Processing**: Convert plain English requests into structured test scenarios
- **Intelligent Script Generation**: Automatically generate production-ready Locust scripts
- **Data-Driven Testing**: Support for CSV and JSON data sources
- **Comprehensive Assertions**: Built-in validation templates and custom assertions
- **Load Profile Templates**: Predefined load testing scenarios (smoke, load, stress, spike)
- **Jenkins Integration**: Ready-to-use YAML configurations for CI/CD pipelines

## 📁 Structure

```
Agent/
├── README.md                           # This file
├── locust_agent.py                     # Main agent script
├── enhanced_locust_agent.py            # Enhanced agent with multi-API support
├── script_generator_config.yaml        # Script generation configuration
├── test_execution_config.yaml          # Test execution configuration
├── setup_env.py                        # OpenAI API key setup script
├── api_endpoints.csv                   # Common API endpoints reference
├── test_scenarios.csv                  # Predefined test scenarios
├── load_profiles.csv                   # Load testing profiles
├── assertion_templates.csv             # Assertion templates
└── data_sources.csv                    # Data source templates
```

## 🔑 OpenAI API Key Setup

**IMPORTANT**: You need an OpenAI API key to use the enhanced agent features.

### **Quick Setup**

Run the setup script:
```bash
python Agent/setup_env.py
```

### **Manual Setup**

**Option 1: Environment Variable (Recommended)**

**Windows PowerShell:**
```powershell
$env:OPENAI_API_KEY="your-openai-api-key-here"
```

**Windows Command Prompt:**
```cmd
set OPENAI_API_KEY=your-openai-api-key-here
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

**Option 2: Create a .env file**

Create a `.env` file in the project root:
```
OPENAI_API_KEY=your-openai-api-key-here
```

**Option 3: Temporary Session**

Set it for the current session:
```bash
python -c "import os; os.environ['OPENAI_API_KEY']='your-key-here'"
```

### **Get Your OpenAI API Key**

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and use it in the setup above

## 🛠️ Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set OpenAI API Key** (see setup above)

3. **Verify Configuration**:
   ```bash
   python Agent/setup_env.py
   ```

## 📖 Usage

### **Basic Agent Usage**

```bash
# Basic usage
python Agent/locust_agent.py "Test the Rick and Morty API with 20 users for 5 minutes"

# Advanced usage with specific endpoints
python Agent/locust_agent.py "Load test the e-commerce API with 50 users for 10 minutes, test /api/products and /api/orders endpoints"

# With custom assertions
python Agent/locust_agent.py "Test user authentication API with 10 users for 2 minutes, verify response time under 500ms and status code 200"
```

### **Enhanced Agent Usage (Multi-API Sequences)**

```bash
# Authentication flow with correlation
python Agent/enhanced_locust_agent.py "Create a HomePage transaction that calls /api/login, then /api/user/profile using the token from login, then /api/logout"

# E-commerce checkout flow
python Agent/enhanced_locust_agent.py "Create a CheckoutFlow transaction that calls /api/products, extracts product_id, calls /api/cart with product_id, extracts cart_id, calls /api/orders with cart_id"

# Rick and Morty sequence
python Agent/enhanced_locust_agent.py "Create a GetCharacters transaction that calls /api/character?page=1, extracts character_name, calls /api/character?name={character_name}"
```

### **Programmatic Usage**

```python
from Agent.locust_agent import LocustAgent

# Initialize agent
agent = LocustAgent()

# Process natural language request
result = agent.process_request(
    "Test the Rick and Morty API with 20 users for 5 minutes"
)

if result['success']:
    print(f"Script generated: {result['script_path']}")
    if result['test_results']:
        print(f"Test metrics: {result['test_results']['metrics']}")
else:
    print(f"Error: {result['error']}")
```

### **Enhanced Agent Programmatic Usage**

```python
from Agent.enhanced_locust_agent import EnhancedLocustAgent

# Initialize enhanced agent
agent = EnhancedLocustAgent()

# Process complex multi-API request
result = agent.process_enhanced_request(
    "Create a HomePage transaction that calls /api/login, then /api/user/profile using the token from login, then /api/logout"
)

if result['success']:
    print(f"Transaction: {result['parsed_request'].transaction_name}")
    print(f"API Steps: {len(result['parsed_request'].api_sequence)}")
    print(f"Script: {result['script_path']}")
```

## 🎯 Natural Language Examples

### **Basic API Testing**
```
"Test the Rick and Morty API with 10 users for 5 minutes"
```

### **E-commerce Load Testing**
```
"Load test the e-commerce API with 50 users for 10 minutes, 
test product browsing and checkout flow"
```

### **Authentication Testing**
```
"Test user login API with 20 users for 3 minutes, 
verify response time under 500ms and successful authentication"
```

### **Multi-API Sequences with Correlation**
```
"Create a HomePage transaction that calls /api/login, then /api/user/profile using the token from login, then /api/logout"

"Create a CheckoutFlow transaction that calls /api/products, extracts product_id, calls /api/cart with product_id, extracts cart_id, calls /api/orders with cart_id"

"Create a GetCharacters transaction that calls /api/character?page=1, extracts character_name, calls /api/character?name={character_name}"
```

## 📊 Data Sources

The agent uses several CSV data sources to enhance script generation:

### **API Endpoints (`api_endpoints.csv`)**
Contains common API endpoints with their specifications:
- HTTP method
- Expected status codes
- Response time expectations
- Complexity levels

### **Test Scenarios (`test_scenarios.csv`)**
Predefined test scenarios for common use cases:
- User registration flow
- E-commerce checkout
- API health checks
- Authentication flows

### **Load Profiles (`load_profiles.csv`)**
Different load testing profiles:
- Smoke test (5 users, 2 minutes)
- Load test (20 users, 5 minutes)
- Stress test (50 users, 10 minutes)
- Spike test (100 users, 5 minutes)

### **Assertion Templates (`assertion_templates.csv`)**
Common validation patterns:
- Status code verification
- Response time thresholds
- JSON path validation
- Content type checks

## ⚙️ Configuration

### **Script Generator Configuration (`script_generator_config.yaml`)**

Key settings:
- **OpenAI Model**: Choose between GPT-3.5-turbo or GPT-4
- **Temperature**: Control creativity vs consistency (0.1-0.9)
- **Load Profiles**: Predefined user counts and durations
- **Assertion Templates**: Common validation patterns
- **Output Formats**: JSON, CSV, HTML, Markdown

### **Test Execution Configuration (`test_execution_config.yaml`)**

Key settings:
- **Jenkins Integration**: Pipeline stages and timeouts
- **Performance Thresholds**: Response time and throughput limits
- **Analysis Templates**: Report generation options
- **Error Handling**: Retry logic and failure handling

## 🔧 Customization

### **Adding New API Endpoints**

Edit `api_endpoints.csv`:
```csv
endpoint,method,description,base_url,headers,parameters,expected_status,response_time_ms,complexity
/api/custom,GET,Custom endpoint,https://api.example.com,Content-Type: application/json,param: string,200,150,low
```

### **Creating Custom Load Profiles**

Edit `load_profiles.csv`:
```csv
profile_name,description,users,spawn_rate,run_time,ramp_up,peak_load,steady_load,ramp_down,use_case
Custom Test,Custom load profile,25,2,8m,2m,25,25,2m,Custom testing
```

### **Adding Assertion Templates**

Edit `assertion_templates.csv`:
```csv
assertion_type,description,format,example,use_case
custom_validation,Custom validation logic,custom: {python_code},custom: len(response.json()) > 0,Custom validation
```

## 🚀 Jenkins Integration

### **Script Generation Pipeline**

Use `script_generator_config.yaml` with Jenkins:
```yaml
pipeline {
    agent any
    stages {
        stage('Generate Script') {
            steps {
                script {
                    def agent = new LocustAgent()
                    def result = agent.process_request(
                        params.NATURAL_LANGUAGE_REQUEST
                    )
                }
            }
        }
    }
}
```

### **Test Execution Pipeline**

Use `test_execution_config.yaml` with Jenkins:
```yaml
pipeline {
    agent any
    stages {
        stage('Execute Test') {
            steps {
                script {
                    def testAgent = new LocustTestAgent()
                    def result = testAgent.execute_test(
                        script_path, 
                        test_config
                    )
                }
            }
        }
    }
}
```

## 📈 Output Examples

### **Generated Script Structure**
```python
from locust import HttpUser, task, between
import json
import time
import logging

class TestRickAndMortyApiUser(HttpUser):
    wait_time = between(1.0, 5.0)
    
    def on_start(self):
        self.variables = {}
        self.logger = logging.getLogger(__name__)
    
    @task
    def run_scenario(self):
        # Step: Get Characters
        try:
            with self.client.get(
                "/api/character?page=1",
                headers={"Content-Type": "application/json"},
                catch_response=True) as response:
                if response.status_code != 200:
                    response.failure('Status code assertion failed')
        except Exception as e:
            self.logger.error(f'Error in API call: {str(e)}')
```

### **Test Results**
```json
{
  "success": true,
  "script_path": "generated_scripts/Test_Rick_And_Morty_API_20250729_143022.py",
  "test_results": {
    "success": true,
    "metrics": {
      "total_requests": 1250,
      "failed_requests": 0,
      "avg_response_time": 245.5,
      "requests_per_sec": 41.67
    }
  }
}
```

## 🐛 Troubleshooting

### **Common Issues**

1. **OpenAI API Key Not Set**
   ```bash
   python Agent/setup_env.py
   ```

2. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration File Not Found**
   ```bash
   # Ensure you're in the correct directory
   cd /path/to/LOCUST-SCRIPT-EXECUTOR
   ```

4. **Script Generation Fails**
   - Check natural language request clarity
   - Verify target host is accessible
   - Review error logs for specific issues

### **Debug Mode**

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Update documentation
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the configuration files
3. Open an issue on GitHub
4. Contact the development team

---

**Happy Performance Testing! 🚀** 