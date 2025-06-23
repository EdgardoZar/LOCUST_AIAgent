# Jenkins Environment Variables Guide

This document describes all environment variables used in the Locust AI Agent Jenkins pipelines.

## 🌍 Global Environment Variables (Jenkins System Level)

Set these in **Jenkins Dashboard → Manage Jenkins → Configure System → Global properties → Environment variables**:

| Variable Name | Default Value | Description |
|---------------|---------------|-------------|
| `PYTHON_VERSION` | `3.9` | Python version to use for the pipelines |
| `GIT_SCRIPTS_BRANCH` | `generated-scripts` | Git branch where generated scripts are stored |
| `JENKINS_GIT_EMAIL` | `jenkins@example.com` | Git email for Jenkins commits |
| `JENKINS_GIT_USER` | `Jenkins Pipeline` | Git username for Jenkins commits |

## 🔧 Script Generation Pipeline Environment Variables

### Pipeline-Level Environment Variables

| Variable Name | Source | Description |
|---------------|--------|-------------|
| `WORKSPACE_DIR` | `${WORKSPACE}\test_workspace` | Directory for test workspace |
| `REPORTS_DIR` | `${WORKSPACE}\test_reports` | Directory for test reports |
| `SCRIPTS_DIR` | `${WORKSPACE}\generated_scripts` | Directory for generated scripts |
| `TIMESTAMP` | Current timestamp | Build timestamp in format `yyyyMMdd_HHmmss` |
| `GIT_EMAIL` | Global or default | Git email for commits |
| `GIT_USER` | Global or default | Git username for commits |
| `BUILD_INFO` | `${BUILD_NUMBER} - ${BUILD_ID}` | Build information string |
| `JOB_NAME` | Jenkins built-in | Name of the Jenkins job |
| `BUILD_URL` | Jenkins built-in | URL of the current build |
| `ENV_SUFFIX` | Based on environment | Environment suffix for script names |

### Runtime Environment Variables

These are set during pipeline execution:

| Variable Name | When Set | Description |
|---------------|----------|-------------|
| `SCENARIO_STEPS_COUNT` | Validation stage | Number of steps in the scenario |
| `SCENARIO_DESCRIPTION` | Validation stage | Description from scenario JSON |
| `GENERATED_SCRIPT` | Script generation stage | Name of the generated script file |

## 🚀 Test Execution Pipeline Environment Variables

### Pipeline-Level Environment Variables

| Variable Name | Source | Description |
|---------------|--------|-------------|
| `TEST_RUN_ID` | `${BUILD_NUMBER}_${TIMESTAMP}` | Unique identifier for test run |
| `TEST_ENVIRONMENT` | `${params.ENVIRONMENT}` | Target environment (dev/staging/prod) |
| `MAX_RESPONSE_TIME_MS` | `${params.MAX_AVG_RESPONSE_TIME}` | Max response time threshold |
| `MIN_SUCCESS_RATE_PCT` | `${params.MIN_SUCCESS_RATE}` | Min success rate threshold |
| `MIN_REQUESTS_PER_SEC` | `${params.MIN_REQUESTS_PER_SEC}` | Min requests per second threshold |

### Runtime Environment Variables

These are set during pipeline execution:

| Variable Name | When Set | Description |
|---------------|----------|-------------|
| `AVAILABLE_SCRIPTS` | List scripts stage | List of available scripts |
| `SCRIPTS_COUNT` | List scripts stage | Number of available scripts |
| `SELECTED_SCRIPT` | List scripts stage | Name of the selected script |
| `SCRIPT_NAME` | Validate script stage | Script name without extension |
| `SCRIPT_PATH` | Validate script stage | Full path to the script |
| `TEST_SUCCESS` | Run test stage | Whether test execution succeeded |
| `TOTAL_REQUESTS` | Run test stage | Total number of requests made |
| `FAILED_REQUESTS` | Run test stage | Number of failed requests |
| `AVG_RESPONSE_TIME` | Run test stage | Average response time in ms |
| `REQUESTS_PER_SEC` | Run test stage | Requests per second achieved |
| `EXECUTION_TIME` | Run test stage | Total execution time in seconds |
| `SUCCESS_RATE` | Analyze results stage | Calculated success rate percentage |
| `PERFORMANCE_ISSUES` | Analyze results stage | List of performance issues found |
| `LLM_GRADE` | LLM analysis stage | Performance grade from LLM analysis |
| `LLM_SUMMARY` | LLM analysis stage | Summary from LLM analysis |

## 📋 Jenkins Built-in Environment Variables

These are automatically available in all Jenkins pipelines:

| Variable Name | Description |
|---------------|-------------|
| `BUILD_NUMBER` | Current build number |
| `BUILD_ID` | Unique build identifier |
| `BUILD_URL` | URL to the current build |
| `JOB_NAME` | Name of the Jenkins job |
| `WORKSPACE` | Path to the workspace directory |
| `BRANCH_NAME` | Git branch name (if using Git) |
| `GIT_COMMIT` | Git commit hash |
| `GIT_BRANCH` | Git branch name |

## 🔧 How to Set Environment Variables

### Method 1: Jenkins Global Configuration

1. Go to **Jenkins Dashboard**
2. Click **"Manage Jenkins"**
3. Click **"Configure System"**
4. Scroll down to **"Global properties"**
5. Check **"Environment variables"**
6. Click **"Add"** for each variable
7. Click **"Save"**

### Method 2: Pipeline-Level Environment Variables

Environment variables can be defined in the `environment` block of each pipeline:

```groovy
environment {
    MY_VARIABLE = "my_value"
    ANOTHER_VARIABLE = "${params.PARAM_NAME}"
}
```

### Method 3: Runtime Environment Variables

Set variables during pipeline execution:

```groovy
script {
    env.MY_VARIABLE = "dynamic_value"
}
```

## 📊 Environment Variable Usage Examples

### In Script Generation Pipeline

```groovy
echo "Generating script: ${env.GENERATED_SCRIPT}"
echo "Branch: ${GIT_SCRIPTS_BRANCH}"
echo "Environment: ${params.ENVIRONMENT}"
```

### In Test Execution Pipeline

```groovy
echo "Test Run ID: ${TEST_RUN_ID}"
echo "Success Rate: ${env.SUCCESS_RATE}%"
echo "Performance Issues: ${env.PERFORMANCE_ISSUES}"
```

## 🔍 Troubleshooting Environment Variables

### Check Variable Values

Add this to any stage to debug environment variables:

```groovy
script {
    echo "All environment variables:"
    env.each { key, value ->
        echo "${key} = ${value}"
    }
}
```

### Common Issues

1. **Variable not found**: Check if the variable is defined in the correct scope
2. **Empty values**: Ensure the variable has a default value or is properly set
3. **Permission issues**: Some variables may require specific Jenkins permissions

## 📝 Best Practices

1. **Use descriptive names**: Make variable names clear and meaningful
2. **Provide defaults**: Always provide default values for optional variables
3. **Document changes**: Update this document when adding new variables
4. **Scope appropriately**: Use the smallest scope necessary for each variable
5. **Validate values**: Check variable values before using them in critical operations 