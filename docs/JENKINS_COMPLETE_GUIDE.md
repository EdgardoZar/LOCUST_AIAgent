# Complete Jenkins CI/CD Pipeline Guide for Locust AI Agent

## 📋 Overview

This guide provides everything you need to set up and configure Jenkins CI/CD pipelines for the Locust AI Agent project. The setup includes two main pipelines:

1. **Script Generation Pipeline** - Creates Locust test scripts from JSON scenarios
2. **Test Execution Pipeline** - Runs existing scripts and generates performance reports

---

## 🚀 Quick Start

### **1. Prerequisites**
- Jenkins server running
- Git repository configured
- Python environment with required packages
- Environment variables set up

### **2. Setup Steps**
1. **Configure Environment Variables** (see [Environment Variables Guide](./JENKINS_ENVIRONMENT_VARIABLES.md))
2. **Create Script Generation Pipeline** (see [Setup Checklist](./JENKINS_SETUP_CHECKLIST.md))
3. **Create Test Execution Pipeline** (see [Setup Checklist](./JENKINS_SETUP_CHECKLIST.md))
4. **Test Both Pipelines** with sample data

### **3. First Run**
```bash
# Script Generation Pipeline
SCENARIO_NAME: "API Health Check"
SCENARIO_JSON: [Copy from examples/sample_scenario_for_jenkins.json]
TARGET_HOST: "https://rickandmortyapi.com"
ENVIRONMENT: "dev"
USERS: "5"
RUN_TIME: "2m"

# Test Execution Pipeline
SELECTED_SCRIPT: [auto-populated]
TARGET_HOST: "https://rickandmortyapi.com"
ENVIRONMENT: "dev"
USERS: "5"
RUN_TIME: "2m"
TEST_DESCRIPTION: "Initial smoke test"
TEST_TAGS: "smoke,api"
```

---

## 📚 Documentation Structure

### **Core Documentation**
- **[Setup Checklist](./JENKINS_SETUP_CHECKLIST.md)** - Step-by-step setup instructions
- **[Parameters Guide](./JENKINS_PIPELINE_PARAMETERS_GUIDE.md)** - Detailed parameter configuration
- **[Quick Reference](./JENKINS_PARAMETERS_QUICK_REFERENCE.md)** - Fast parameter lookup
- **[Environment Variables](./JENKINS_ENVIRONMENT_VARIABLES.md)** - Environment configuration

### **Pipeline Files**
- **[Jenkinsfile-ScriptGeneration](../Jenkinsfile-ScriptGeneration)** - Script generation pipeline
- **[Jenkinsfile-TestExecution](../Jenkinsfile-TestExecution)** - Test execution pipeline

### **Sample Files**
- **[Sample Scenario JSON](../examples/sample_scenario_for_jenkins.json)** - Example JSON for testing
- **[Sample Test Config](../examples/sample_test_config.json)** - Example test configuration

---

## 🔧 Pipeline Architecture

### **Script Generation Pipeline**
```
Input: JSON Scenario → Generate Locust Script → Commit to Git → Archive Results
```

**Stages:**
1. **Environment Setup** - Configure workspace and variables
2. **Script Generation** - Create Locust script from JSON
3. **Git Operations** - Commit and push script to repository
4. **Result Archiving** - Save logs and metadata

### **Test Execution Pipeline**
```
Input: Script Selection → Run Locust Test → Generate Reports → Analyze Results
```

**Stages:**
1. **Environment Setup** - Configure workspace and variables
2. **Script Discovery** - List available scripts from Git
3. **Test Execution** - Run selected script with Locust
4. **Report Generation** - Create HTML and CSV reports
5. **Performance Analysis** - Validate against thresholds
6. **LLM Analysis** - AI-powered result analysis (optional)
7. **Result Archiving** - Save all results and reports

---

## 📊 Parameter Summary

### **Script Generation Pipeline Parameters**

#### **Required (2)**
| Parameter | Type | Description |
|-----------|------|-------------|
| `SCENARIO_NAME` | String | Name of the test scenario |
| `SCENARIO_JSON` | Text | JSON configuration for the scenario |

#### **Optional (12)**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `TARGET_HOST` | String | `https://api.example.com` | Target host URL |
| `API_TOKEN` | Password | (empty) | API token for authentication |
| `ENVIRONMENT` | Choice | `dev` | Target environment |
| `USERS` | String | `10` | Number of concurrent users |
| `SPAWN_RATE` | String | `2` | Users spawned per second |
| `RUN_TIME` | String | `5m` | Test duration |
| `MIN_WAIT` | String | `1000` | Min wait time (ms) |
| `MAX_WAIT` | String | `5000` | Max wait time (ms) |
| `GENERATE_HTML_REPORT` | Boolean | `true` | Generate HTML report |
| `GENERATE_CSV_REPORT` | Boolean | `true` | Generate CSV report |
| `LOG_LEVEL` | String | `INFO` | Logging level |
| `GIT_COMMIT_MESSAGE` | String | (empty) | Custom commit message |

### **Test Execution Pipeline Parameters**

#### **Required (1)**
| Parameter | Type | Description |
|-----------|------|-------------|
| `SELECTED_SCRIPT` | String | Script to run (auto-populated) |

#### **Optional (17)**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `TARGET_HOST` | String | `https://api.example.com` | Target host URL |
| `API_TOKEN` | Password | (empty) | API token for authentication |
| `ENVIRONMENT` | Choice | `dev` | Target environment |
| `USERS` | String | `10` | Number of concurrent users |
| `SPAWN_RATE` | String | `2` | Users spawned per second |
| `RUN_TIME` | String | `5m` | Test duration |
| `MIN_WAIT` | String | `1000` | Min wait time (ms) |
| `MAX_WAIT` | String | `5000` | Max wait time (ms) |
| `USE_LLM_ANALYSIS` | Boolean | `false` | Enable LLM analysis |
| `GENERATE_HTML_REPORT` | Boolean | `true` | Generate HTML report |
| `GENERATE_CSV_REPORT` | Boolean | `true` | Generate CSV report |
| `LOG_LEVEL` | String | `INFO` | Logging level |
| `MAX_AVG_RESPONSE_TIME` | String | `2000` | Max avg response time (ms) |
| `MIN_SUCCESS_RATE` | String | `95` | Min success rate (%) |
| `MIN_REQUESTS_PER_SEC` | String | `10` | Min requests per second |
| `TEST_DESCRIPTION` | String | (empty) | Test run description |
| `TEST_TAGS` | String | (empty) | Test run tags |

---

## 🔑 Environment Variables

### **Required Variables**
- `GIT_REPO_URL` - Git repository URL
- `GIT_BRANCH` - Default branch name
- `PYTHON_PATH` - Python executable path

### **Optional Variables**
- `OPENAI_API_KEY` - For LLM analysis
- `JENKINS_WORKSPACE` - Jenkins workspace path
- `REPORTS_DIR` - Reports directory
- `SCRIPTS_DIR` - Scripts directory

---

## 🎯 Use Cases

### **1. API Testing**
- Generate scripts for REST API endpoints
- Test authentication flows
- Validate response formats
- Monitor performance metrics

### **2. Load Testing**
- Simulate multiple concurrent users
- Test system under stress
- Identify performance bottlenecks
- Validate scalability

### **3. Continuous Testing**
- Integrate with CI/CD pipelines
- Automated regression testing
- Performance regression detection
- Quality gates for deployments

### **4. Monitoring & Alerting**
- Set performance thresholds
- Generate detailed reports
- AI-powered analysis
- Historical trend tracking

---

## 🔍 Troubleshooting

### **Common Issues**

#### **Pipeline Build Failures**
- Check Jenkins console output
- Verify parameter names and types
- Validate JSON format for scenarios
- Ensure Git credentials are configured

#### **Script Generation Issues**
- Validate JSON schema
- Check Python environment
- Verify file permissions
- Review Git repository access

#### **Test Execution Issues**
- Verify target host accessibility
- Check API authentication
- Validate script existence
- Review performance thresholds

#### **Environment Issues**
- Verify environment variables
- Check Python package installation
- Validate workspace permissions
- Review Jenkins configuration

### **Debug Commands**
```groovy
// Add to any stage for debugging
script {
    echo "=== Parameter Debug ==="
    params.each { key, value ->
        echo "${key} = ${value}"
    }
    echo "=== Environment Debug ==="
    env.each { key, value ->
        echo "${key} = ${value}"
    }
}
```

---

## 📈 Performance Guidelines

### **Response Time Thresholds**
- **Excellent**: < 500ms
- **Good**: 500ms - 1s
- **Acceptable**: 1s - 2s
- **Poor**: > 2s

### **Success Rate Thresholds**
- **Production**: ≥ 99%
- **Staging**: ≥ 95%
- **Development**: ≥ 90%

### **Load Testing Scenarios**
| Scenario | Users | Spawn Rate | Run Time | Purpose |
|----------|-------|------------|----------|---------|
| **Smoke Test** | 1-5 | 1 | 1-2m | Basic functionality |
| **Load Test** | 10-50 | 2-5 | 5-10m | Normal load |
| **Stress Test** | 100-500 | 10-20 | 10-30m | System limits |
| **Spike Test** | 1000+ | 50+ | 5-15m | Peak load |

---

## 🚀 Advanced Features

### **LLM-Powered Analysis** ✅ **WORKING**
The Locust AI Agent includes advanced AI-powered analysis capabilities that provide intelligent insights into test results.

#### **Features**
- **AI-driven test result interpretation** using OpenAI models
- **Performance insights and recommendations** based on industry best practices
- **Automated issue detection** with specific problem identification
- **Natural language reporting** in Markdown format
- **Configurable AI models** (gpt-3.5-turbo, gpt-4, etc.)
- **Performance grading** (EXCELLENT, GOOD, ACCEPTABLE, POOR, FAILED)

#### **Setup Requirements**
1. **OpenAI API Key**: Add as Jenkins credential with ID `openai-api-key`
2. **Jenkins Parameter**: Enable `USE_LLM_ANALYSIS` in pipeline configuration
3. **Model Selection**: Configure `LLM_MODEL` parameter (default: gpt-3.5-turbo)

#### **Analysis Output**
The LLM analysis generates comprehensive reports including:
- **Performance Grade** with emoji indicators
- **Executive Summary** of test results
- **Response Time Analysis** with detailed metrics
- **Key Insights** highlighting important findings
- **Recommendations** for performance improvements
- **Potential Issues** with specific concerns
- **Business Impact** assessment
- **Next Steps** for follow-up actions

#### **Example Analysis Report**
```markdown
# 📊 LLM Performance Analysis Report

## Test Scenario: `Rick and Morty API Test`
**Test Run ID:** `Fixed_v6_20250623_153346`

## 📈 Performance Grade: GOOD 👍

### 📝 Summary
The API test showed good overall performance with 100% success rate and reasonable response times.

### ⏱️ Response Time Analysis
| Metric | Value |
|---|---|
| Average Response Time | 245ms |
| 90th Percentile | 456ms |
| 95th Percentile | 678ms |

### 💡 Key Insights
- All requests completed successfully
- Response times are within acceptable ranges
- No performance bottlenecks detected

### 🛠️ Recommendations
- Monitor response times under higher load
- Consider caching for frequently accessed data
```

#### **Integration with Jenkins**
- **Automatic Analysis**: Runs after test execution when enabled
- **Artifact Archiving**: Analysis reports are archived as build artifacts
- **Git Integration**: Analysis reports are committed to repository
- **Environment Variables**: Results available as `LLM_GRADE` and `LLM_SUMMARY`

### **Flexible Script Management**
- Dynamic script generation from JSON
- Version-controlled script storage
- Environment-specific configurations
- Reusable test components

### **Comprehensive Reporting**
- HTML reports with charts and metrics
- CSV exports for data analysis
- Performance threshold validation
- Historical trend tracking

### **Integration Capabilities**
- Git-based script versioning
- CI/CD pipeline integration
- Webhook triggers
- External tool integration

---

## 📝 Best Practices

### **Script Development**
1. Start with simple scenarios
2. Use descriptive names and tags
3. Validate JSON before running
4. Test incrementally
5. Document changes

### **Performance Testing**
1. Begin with smoke tests
2. Scale up gradually
3. Monitor resource usage
4. Set realistic thresholds
5. Analyze trends over time

### **Pipeline Management**
1. Use version control for scripts
2. Implement proper error handling
3. Set up monitoring and alerts
4. Regular maintenance and updates
5. Document configuration changes

---

## 🎯 Next Steps

### **Immediate Actions**
1. Complete the setup checklist
2. Run initial smoke tests
3. Validate pipeline integration
4. Configure monitoring

### **Medium-term Goals**
1. Create custom test scenarios
2. Set up automated triggers
3. Implement performance baselines
4. Configure alerting

### **Long-term Objectives**
1. Scale to production workloads
2. Integrate with monitoring tools
3. Implement advanced analytics
4. Optimize for your specific use case

---

## 📚 Additional Resources

### **Documentation**
- [Locust Documentation](https://docs.locust.io/)
- [Jenkins Pipeline Documentation](https://www.jenkins.io/doc/book/pipeline/)
- [Git Documentation](https://git-scm.com/doc)

### **Sample Files**
- [Sample Scenario JSON](../examples/sample_scenario_for_jenkins.json)
- [Sample Test Config](../examples/sample_test_config.json)
- [Run Example Script](../run_example.py)

### **Support**
- Check Jenkins console logs for detailed error messages
- Validate all configuration parameters
- Test with minimal load first
- Review environment variable setup

---

*This guide provides a complete reference for setting up and using Jenkins pipelines with the Locust AI Agent. Follow the setup checklist for step-by-step instructions, and refer to the detailed documentation for specific configuration options.* 