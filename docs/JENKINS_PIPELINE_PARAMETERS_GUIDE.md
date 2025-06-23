# Jenkins Pipeline Parameters Configuration Guide

This guide provides step-by-step instructions for configuring all parameters in the Locust AI Agent Jenkins pipelines.

## 📋 Table of Contents

1. [Script Generation Pipeline Parameters](#script-generation-pipeline-parameters)
2. [Test Execution Pipeline Parameters](#test-execution-pipeline-parameters)
3. [Parameter Configuration Steps](#parameter-configuration-steps)
4. [Sample Parameter Values](#sample-parameter-values)
5. [Troubleshooting](#troubleshooting)

---

## 🔧 Script Generation Pipeline Parameters

### **Required Parameters**

#### 1. `SCENARIO_NAME`
- **Type**: String Parameter
- **Required**: ✅ Yes
- **Default Value**: (empty)
- **Description**: Name of the test scenario
- **Step-by-Step**:
  1. Click "Add Parameter" → "String Parameter"
  2. **Name**: `SCENARIO_NAME`
  3. **Default Value**: Leave empty
  4. **Description**: `Name of the test scenario (e.g., "User Login Test", "API Health Check")`
  5. **Example Values**:
     - `Rick and Morty API Test`
     - `User Authentication Flow`
     - `Product Catalog API`
     - `Payment Gateway Test`

#### 2. `SCENARIO_JSON`
- **Type**: Text Parameter
- **Required**: ✅ Yes
- **Default Value**: (empty)
- **Description**: JSON configuration for the scenario
- **Step-by-Step**:
  1. Click "Add Parameter" → "Text Parameter"
  2. **Name**: `SCENARIO_JSON`
  3. **Default Value**: Leave empty
  4. **Description**: `JSON configuration defining the test scenario steps, endpoints, and assertions`
  5. **Example Value**:
   ```json
   {
     "name": "Rick and Morty API Test",
     "description": "Test Rick and Morty API endpoints",
     "steps": [
       {
         "id": 1,
         "type": "api_call",
         "config": {
           "name": "Get Characters",
           "method": "GET",
           "url": "/api/character?page=1",
           "headers": {
             "Content-Type": "application/json"
           },
           "assertions": [
             {"type": "status_code", "value": 200}
           ]
         }
       }
     ]
   }
   ```

### **Optional Parameters**

#### 3. `TARGET_HOST`
- **Type**: String Parameter
- **Required**: ❌ No
- **Default Value**: `https://api.example.com`
- **Description**: Target host URL for testing
- **Step-by-Step**:
  1. Click "Add Parameter" → "String Parameter"
  2. **Name**: `TARGET_HOST`
  3. **Default Value**: `https://api.example.com`
  4. **Description**: `Base URL of the API to test (e.g., https://rickandmortyapi.com)`
  5. **Example Values**:
     - `https://rickandmortyapi.com`
     - `https://api.github.com`
     - `https://jsonplaceholder.typicode.com`
     - `https://httpbin.org`

#### 4. `API_TOKEN`
- **Type**: Password Parameter
- **Required**: ❌ No
- **Default Value**: (empty)
- **Description**: API token for authentication
- **Step-by-Step**:
  1. Click "Add Parameter" → "Password Parameter"
  2. **Name**: `API_TOKEN`
  3. **Default Value**: Leave empty
  4. **Description**: `API token for authentication (if required by the target API)`
  5. **Security Note**: This parameter is masked in logs for security

#### 5. `ENVIRONMENT`
- **Type**: Choice Parameter
- **Required**: ❌ No
- **Default Value**: `dev`
- **Description**: Target environment
- **Step-by-Step**:
  1. Click "Add Parameter" → "Choice Parameter"
  2. **Name**: `ENVIRONMENT`
  3. **Choices** (add each on a new line):
     ```
     dev
     staging
     prod
     ```
  4. **Description**: `Target environment for the test (affects script naming)`

#### 6. `USERS`
- **Type**: String Parameter
- **Required**: ❌ No
- **Default Value**: `10`
- **Description**: Number of concurrent users
- **Step-by-Step**:
  1. Click "Add Parameter" → "String Parameter"
  2. **Name**: `USERS`
  3. **Default Value**: `10`
  4. **Description**: `Number of concurrent users for the test (1-1000)`
  5. **Example Values**: `1`, `5`, `10`, `50`, `100`

#### 7. `SPAWN_RATE`
- **Type**: String Parameter
- **Required**: ❌ No
- **Default Value**: `2`
- **Description**: User spawn rate per second
- **Step-by-Step**:
  1. Click "Add Parameter" → "String Parameter"
  2. **Name**: `SPAWN_RATE`
  3. **Default Value**: `2`
  4. **Description**: `How many users to spawn per second (1-10)`
  5. **Example Values**: `1`, `2`, `5`, `10`

#### 8. `RUN_TIME`
- **Type**: String Parameter
- **Required**: ❌ No
- **Default Value**: `5m`
- **Description**: Test duration
- **Step-by-Step**:
  1. Click "Add Parameter" → "String Parameter"
  2. **Name**: `RUN_TIME`
  3. **Default Value**: `5m`
  4. **Description**: `Test duration in format: 30s, 1m, 5m, 1h`
  5. **Example Values**: `30s`, `1m`, `5m`, `10m`, `1h`

#### 9. `MIN_WAIT`
- **Type**: String Parameter
- **Required**: ❌ No
- **Default Value**: `1000`
- **Description**: Minimum wait time between requests (ms)
- **Step-by-Step**:
  1. Click "Add Parameter" → "String Parameter"
  2. **Name**: `MIN_WAIT`
  3. **Default Value**: `1000`
  4. **Description**: `Minimum wait time between requests in milliseconds (100-10000)`
  5. **Example Values**: `500`, `1000`, `2000`, `5000`

#### 10. `MAX_WAIT`
- **Type**: String Parameter
- **Required**: ❌ No
- **Default Value**: `5000`
- **Description**: Maximum wait time between requests (ms)
- **Step-by-Step**:
  1. Click "Add Parameter" → "String Parameter"
  2. **Name**: `MAX_WAIT`
  3. **Default Value**: `5000`
  4. **Description**: `Maximum wait time between requests in milliseconds (1000-30000)`
  5. **Example Values**: `2000`, `5000`, `10000`, `15000`

#### 11. `GENERATE_HTML_REPORT`
- **Type**: Boolean Parameter
- **Required**: ❌ No
- **Default Value**: `true`
- **Description**: Generate HTML test report
- **Step-by-Step**:
  1. Click "Add Parameter" → "Boolean Parameter"
  2. **Name**: `GENERATE_HTML_REPORT`
  3. **Default Value**: Check the box (true)
  4. **Description**: `Generate HTML report for test results`

#### 12. `GENERATE_CSV_REPORT`
- **Type**: Boolean Parameter
- **Required**: ❌ No
- **Default Value**: `true`
- **Description**: Generate CSV test report
- **Step-by-Step**:
  1. Click "Add Parameter" → "Boolean Parameter"
  2. **Name**: `GENERATE_CSV_REPORT`
  3. **Default Value**: Check the box (true)
  4. **Description**: `Generate CSV report for test results`

#### 13. `LOG_LEVEL`
- **Type**: String Parameter
- **Required**: ❌ No
- **Default Value**: `INFO`
- **Description**: Logging level
- **Step-by-Step**:
  1. Click "Add Parameter" → "String Parameter"
  2. **Name**: `LOG_LEVEL`
  3. **Default Value**: `INFO`
  4. **Description**: `Logging level for the test (DEBUG, INFO, WARNING, ERROR)`
  5. **Example Values**: `DEBUG`, `INFO`, `WARNING`, `ERROR`

#### 14. `GIT_COMMIT_MESSAGE`
- **Type**: String Parameter
- **Required**: ❌ No
- **Default Value**: (empty)
- **Description**: Custom commit message
- **Step-by-Step**:
  1. Click "Add Parameter" → "String Parameter"
  2. **Name**: `GIT_COMMIT_MESSAGE`
  3. **Default Value**: Leave empty
  4. **Description**: `Custom commit message for the generated script (optional)`
  5. **Example Values**:
     - `Generated API health check script`
     - `Added user authentication test`
     - `Updated payment gateway test`

---

## 🚀 Test Execution Pipeline Parameters

### **Required Parameters**

#### 1. `SELECTED_SCRIPT`
- **Type**: String Parameter
- **Required**: ❌ No (auto-populated)
- **Default Value**: (empty)
- **Description**: Script to run
- **Step-by-Step**:
  1. Click "Add Parameter" → "String Parameter"
  2. **Name**: `SELECTED_SCRIPT`
  3. **Default Value**: Leave empty
  4. **Description**: `Script to run (will be auto-populated from available scripts)`
  5. **Note**: This will be automatically populated with available scripts

### **Optional Parameters**

#### 2. `TARGET_HOST`
- **Type**: String Parameter
- **Required**: ❌ No
- **Default Value**: `https://api.example.com`
- **Description**: Target host URL for testing
- **Step-by-Step**:
  1. Click "Add Parameter" → "String Parameter"
  2. **Name**: `TARGET_HOST`
  3. **Default Value**: `https://api.example.com`
  4. **Description**: `Base URL of the API to test`
  5. **Example Values**:
     - `https://rickandmortyapi.com`
     - `https://api.github.com`
     - `https://jsonplaceholder.typicode.com`

#### 3. `API_TOKEN`
- **Type**: Password Parameter
- **Required**: ❌ No
- **Default Value**: (empty)
- **Description**: API token for authentication
- **Step-by-Step**:
  1. Click "Add Parameter" → "Password Parameter"
  2. **Name**: `API_TOKEN`
  3. **Default Value**: Leave empty
  4. **Description**: `API token for authentication (if required)`

#### 4. `ENVIRONMENT`
- **Type**: Choice Parameter
- **Required**: ❌ No
- **Default Value**: `dev`
- **Description**: Target environment
- **Step-by-Step**:
  1. Click "Add Parameter" → "Choice Parameter"
  2. **Name**: `ENVIRONMENT`
  3. **Choices**:
     ```
     dev
     staging
     prod
     ```
  4. **Description**: `Target environment for the test`

#### 5. `USERS`
- **Type**: String Parameter
- **Required**: ❌ No
- **Default Value**: `10`
- **Description**: Number of concurrent users
- **Step-by-Step**:
  1. Click "Add Parameter" → "String Parameter"
  2. **Name**: `USERS`
  3. **Default Value**: `10`
  4. **Description**: `Number of concurrent users (1-1000)`
  5. **Example Values**: `1`, `5`, `10`, `50`, `100`

#### 6. `SPAWN_RATE`
- **Type**: String Parameter
- **Required**: ❌ No
- **Default Value**: `2`
- **Description**: User spawn rate per second
- **Step-by-Step**:
  1. Click "Add Parameter" → "String Parameter"
  2. **Name**: `SPAWN_RATE`
  3. **Default Value**: `2`
  4. **Description**: `Users spawned per second (1-10)`
  5. **Example Values**: `1`, `2`, `5`, `10`

#### 7. `RUN_TIME`
- **Type**: String Parameter
- **Required**: ❌ No
- **Default Value**: `5m`
- **Description**: Test duration
- **Step-by-Step**:
  1. Click "Add Parameter" → "String Parameter"
  2. **Name**: `RUN_TIME`
  3. **Default Value**: `5m`
  4. **Description**: `Test duration (30s, 1m, 5m, 1h)`
  5. **Example Values**: `30s`, `1m`, `5m`, `10m`, `1h`

#### 8. `MIN_WAIT`
- **Type**: String Parameter
- **Required**: ❌ No
- **Default Value**: `1000`
- **Description**: Minimum wait time between requests (ms)
- **Step-by-Step**:
  1. Click "Add Parameter" → "String Parameter"
  2. **Name**: `MIN_WAIT`
  3. **Default Value**: `1000`
  4. **Description**: `Min wait time in milliseconds (100-10000)`
  5. **Example Values**: `500`, `1000`, `2000`, `5000`

#### 9. `MAX_WAIT`
- **Type**: String Parameter
- **Required**: ❌ No
- **Default Value**: `5000`
- **Description**: Maximum wait time between requests (ms)
- **Step-by-Step**:
  1. Click "Add Parameter" → "String Parameter"
  2. **Name**: `MAX_WAIT`
  3. **Default Value**: `5000`
  4. **Description**: `Max wait time in milliseconds (1000-30000)`
  5. **Example Values**: `2000`, `5000`, `10000`, `15000`

#### 10. `USE_LLM_ANALYSIS`
- **Type**: Boolean Parameter
- **Required**: ❌ No
- **Default Value**: `false`
- **Description**: Enable LLM-powered analysis
- **Step-by-Step**:
  1. Click "Add Parameter" → "Boolean Parameter"
  2. **Name**: `USE_LLM_ANALYSIS`
  3. **Default Value**: Leave unchecked (false)
  4. **Description**: `Enable AI-powered analysis of test results (requires OpenAI API key)`

#### 11. `GENERATE_HTML_REPORT`
- **Type**: Boolean Parameter
- **Required**: ❌ No
- **Default Value**: `true`
- **Description**: Generate HTML test report
- **Step-by-Step**:
  1. Click "Add Parameter" → "Boolean Parameter"
  2. **Name**: `GENERATE_HTML_REPORT`
  3. **Default Value**: Check the box (true)
  4. **Description**: `Generate HTML report for test results`

#### 12. `GENERATE_CSV_REPORT`
- **Type**: Boolean Parameter
- **Required**: ❌ No
- **Default Value**: `true`
- **Description**: Generate CSV test report
- **Step-by-Step**:
  1. Click "Add Parameter" → "Boolean Parameter"
  2. **Name**: `GENERATE_CSV_REPORT`
  3. **Default Value**: Check the box (true)
  4. **Description**: `Generate CSV report for test results`

#### 13. `LOG_LEVEL`
- **Type**: String Parameter
- **Required**: ❌ No
- **Default Value**: `INFO`
- **Description**: Logging level
- **Step-by-Step**:
  1. Click "Add Parameter" → "String Parameter"
  2. **Name**: `LOG_LEVEL`
  3. **Default Value**: `INFO`
  4. **Description**: `Logging level (DEBUG, INFO, WARNING, ERROR)`
  5. **Example Values**: `DEBUG`, `INFO`, `WARNING`, `ERROR`

#### 14. `MAX_AVG_RESPONSE_TIME`
- **Type**: String Parameter
- **Required**: ❌ No
- **Default Value**: `2000`
- **Description**: Maximum average response time (ms)
- **Step-by-Step**:
  1. Click "Add Parameter" → "String Parameter"
  2. **Name**: `MAX_AVG_RESPONSE_TIME`
  3. **Default Value**: `2000`
  4. **Description**: `Maximum acceptable average response time in milliseconds`
  5. **Example Values**: `1000`, `2000`, `5000`, `10000`

#### 15. `MIN_SUCCESS_RATE`
- **Type**: String Parameter
- **Required**: ❌ No
- **Default Value**: `95`
- **Description**: Minimum success rate percentage
- **Step-by-Step**:
  1. Click "Add Parameter" → "String Parameter"
  2. **Name**: `MIN_SUCCESS_RATE`
  3. **Default Value**: `95`
  4. **Description**: `Minimum acceptable success rate percentage (0-100)`
  5. **Example Values**: `90`, `95`, `98`, `99`

#### 16. `MIN_REQUESTS_PER_SEC`
- **Type**: String Parameter
- **Required**: ❌ No
- **Default Value**: `10`
- **Description**: Minimum requests per second
- **Step-by-Step**:
  1. Click "Add Parameter" → "String Parameter"
  2. **Name**: `MIN_REQUESTS_PER_SEC`
  3. **Default Value**: `10`
  4. **Description**: `Minimum acceptable requests per second`
  5. **Example Values**: `5`, `10`, `20`, `50`

#### 17. `TEST_DESCRIPTION`
- **Type**: String Parameter
- **Required**: ❌ No
- **Default Value**: (empty)
- **Description**: Description of this test run
- **Step-by-Step**:
  1. Click "Add Parameter" → "String Parameter"
  2. **Name**: `TEST_DESCRIPTION`
  3. **Default Value**: Leave empty
  4. **Description**: `Description of this test run for documentation`
  5. **Example Values**:
     - `Smoke test for user API`
     - `Performance test for payment gateway`
     - `Load test for product catalog`

#### 18. `TEST_TAGS`
- **Type**: String Parameter
- **Required**: ❌ No
- **Default Value**: (empty)
- **Description**: Tags for this test run
- **Step-by-Step**:
  1. Click "Add Parameter" → "String Parameter"
  2. **Name**: `TEST_TAGS`
  3. **Default Value**: Leave empty
  4. **Description**: `Tags for categorizing this test run (comma-separated)`
  5. **Example Values**:
     - `smoke,api`
     - `performance,payment`
     - `load,user-management`

---

## ⚙️ Parameter Configuration Steps

### **Step 1: Access Pipeline Configuration**

1. Go to **Jenkins Dashboard**
2. Click on your pipeline name (e.g., `LOCUST-Script-Generation-Pipeline`)
3. Click **"Configure"** in the left sidebar
4. Scroll down to **"Build Triggers"** section

### **Step 2: Enable Parameterized Build**

1. Check the box **"This project is parameterized"**
2. This will reveal the **"Add Parameter"** button

### **Step 3: Add Parameters**

1. Click **"Add Parameter"**
2. Select the appropriate parameter type:
   - **String Parameter**: For text values
   - **Text Parameter**: For multi-line text (like JSON)
   - **Choice Parameter**: For dropdown selections
   - **Boolean Parameter**: For true/false values
   - **Password Parameter**: For sensitive data

### **Step 4: Configure Each Parameter**

For each parameter:
1. **Name**: Enter the parameter name exactly as shown above
2. **Default Value**: Enter the suggested default value
3. **Description**: Copy the description provided above
4. **Additional Options**: Configure any specific options (like choices for Choice parameters)

### **Step 5: Save Configuration**

1. Click **"Save"** at the bottom of the page
2. Verify the parameters appear in the **"Build with Parameters"** section

---

## 📊 Sample Parameter Values

### **Quick Start Configuration**

#### **Script Generation Pipeline - Quick Start**
```
SCENARIO_NAME: Rick and Morty API Test
SCENARIO_JSON: [Copy from examples/sample_scenario_for_jenkins.json]
TARGET_HOST: https://rickandmortyapi.com
ENVIRONMENT: dev
USERS: 5
RUN_TIME: 2m
```

#### **Test Execution Pipeline - Quick Start**
```
SELECTED_SCRIPT: [auto-populated]
TARGET_HOST: https://rickandmortyapi.com
ENVIRONMENT: dev
USERS: 5
RUN_TIME: 2m
TEST_DESCRIPTION: Initial smoke test
TEST_TAGS: smoke,api
```

### **Production Configuration**

#### **Script Generation Pipeline - Production**
```
SCENARIO_NAME: Payment Gateway API Test
SCENARIO_JSON: [Your production scenario JSON]
TARGET_HOST: https://api.payments.com
ENVIRONMENT: prod
USERS: 100
SPAWN_RATE: 10
RUN_TIME: 10m
MIN_WAIT: 2000
MAX_WAIT: 10000
GIT_COMMIT_MESSAGE: Production payment gateway test script
```

#### **Test Execution Pipeline - Production**
```
SELECTED_SCRIPT: Payment_Gateway_API_Test_prod.py
TARGET_HOST: https://api.payments.com
ENVIRONMENT: prod
USERS: 100
SPAWN_RATE: 10
RUN_TIME: 10m
MAX_AVG_RESPONSE_TIME: 5000
MIN_SUCCESS_RATE: 99
MIN_REQUESTS_PER_SEC: 20
USE_LLM_ANALYSIS: true
TEST_DESCRIPTION: Production load test for payment gateway
TEST_TAGS: production,load,payment
```

---

## 🔍 Troubleshooting

### **Common Issues**

#### **Parameter Not Found**
- **Problem**: Pipeline says parameter doesn't exist
- **Solution**: Check parameter name spelling and case sensitivity
- **Action**: Ensure parameter name matches exactly (e.g., `SCENARIO_NAME` not `scenario_name`)

#### **Invalid JSON Format**
- **Problem**: Script generation fails due to JSON errors
- **Solution**: Validate JSON format using online JSON validator
- **Action**: Copy the sample JSON and modify it carefully

#### **No Scripts Available**
- **Problem**: Test execution pipeline shows no scripts
- **Solution**: Run script generation pipeline first
- **Action**: Generate at least one script before running tests

#### **Permission Denied**
- **Problem**: Git operations fail
- **Solution**: Check Jenkins Git credentials
- **Action**: Configure Git credentials in Jenkins

### **Validation Checklist**

Before running pipelines, verify:

#### **Script Generation Pipeline**
- ✅ `SCENARIO_NAME` is not empty
- ✅ `SCENARIO_JSON` is valid JSON
- ✅ `TARGET_HOST` is a valid URL
- ✅ `ENVIRONMENT` is one of: dev, staging, prod

#### **Test Execution Pipeline**
- ✅ `TARGET_HOST` is a valid URL
- ✅ `USERS` is a positive number
- ✅ `RUN_TIME` is in correct format (e.g., "5m")
- ✅ Performance thresholds are reasonable

### **Debug Commands**

Add these to any stage for debugging:

```groovy
script {
    echo "=== Parameter Debug ==="
    echo "All parameters:"
    params.each { key, value ->
        echo "${key} = ${value}"
    }
    echo "=== Environment Debug ==="
    echo "All environment variables:"
    env.each { key, value ->
        echo "${key} = ${value}"
    }
}
```

---

## 📝 Best Practices

1. **Start Simple**: Begin with minimal parameters and add complexity gradually
2. **Use Descriptive Names**: Make scenario names and descriptions clear
3. **Validate Inputs**: Always validate JSON and URLs before running
4. **Document Changes**: Keep track of parameter changes and their effects
5. **Test Incrementally**: Test with small user counts before scaling up
6. **Monitor Resources**: Watch for resource usage during high-load tests
7. **Use Tags**: Tag your tests for better organization and filtering
8. **Version Control**: Keep your JSON scenarios in version control

---

## 🎯 Next Steps

After configuring parameters:

1. **Test Script Generation**: Run with a simple scenario first
2. **Verify Script Creation**: Check that scripts are saved to Git
3. **Test Execution**: Run the test execution pipeline
4. **Review Results**: Check HTML reports and performance metrics
5. **Iterate**: Refine parameters based on results
6. **Scale Up**: Gradually increase load and complexity

This guide should help you configure all parameters correctly for both pipelines. If you encounter any issues, refer to the troubleshooting section or check the Jenkins console output for detailed error messages. 