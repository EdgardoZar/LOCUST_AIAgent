# Jenkins Pipeline Setup Checklist

## 🚀 Quick Setup Checklist

### **Pre-requisites**
- [ ] Jenkins server is running and accessible
- [ ] Git repository is configured in Jenkins
- [ ] Jenkins has access to Python and required packages
- [ ] Environment variables are configured (see [JENKINS_ENVIRONMENT_VARIABLES.md](./JENKINS_ENVIRONMENT_VARIABLES.md))

---

## 📋 Script Generation Pipeline Setup

### **Step 1: Create Pipeline**
- [ ] Go to Jenkins Dashboard
- [ ] Click "New Item"
- [ ] Enter name: `LOCUST-Script-Generation-Pipeline`
- [ ] Select "Pipeline"
- [ ] Click "OK"

### **Step 2: Configure Pipeline**
- [ ] In "Pipeline" section, select "Pipeline script from SCM"
- [ ] Select "Git" as SCM
- [ ] Enter Repository URL
- [ ] Select branch (e.g., `main` or `master`)
- [ ] Set Script Path to: `Jenkinsfile-ScriptGeneration`
- [ ] Click "Save"

### **Step 3: Enable Parameters**
- [ ] Click "Configure" on the pipeline
- [ ] Check "This project is parameterized"
- [ ] Add required parameters:

#### **Required Parameters**
- [ ] **SCENARIO_NAME** (String Parameter)
  - Name: `SCENARIO_NAME`
  - Default Value: (leave empty)
  - Description: `Name of the test scenario`

- [ ] **SCENARIO_JSON** (Text Parameter)
  - Name: `SCENARIO_JSON`
  - Default Value: (leave empty)
  - Description: `JSON configuration for the scenario`

#### **Optional Parameters**
- [ ] **TARGET_HOST** (String Parameter)
  - Name: `TARGET_HOST`
  - Default Value: `https://api.example.com`
  - Description: `Target host URL for testing`

- [ ] **ENVIRONMENT** (Choice Parameter)
  - Name: `ENVIRONMENT`
  - Choices:
    ```
    dev
    staging
    prod
    ```
  - Description: `Target environment`

- [ ] **USERS** (String Parameter)
  - Name: `USERS`
  - Default Value: `10`
  - Description: `Number of concurrent users`

- [ ] **RUN_TIME** (String Parameter)
  - Name: `RUN_TIME`
  - Default Value: `5m`
  - Description: `Test duration`

- [ ] **GENERATE_HTML_REPORT** (Boolean Parameter)
  - Name: `GENERATE_HTML_REPORT`
  - Default Value: ✓ (checked)
  - Description: `Generate HTML report`

- [ ] **GENERATE_CSV_REPORT** (Boolean Parameter)
  - Name: `GENERATE_CSV_REPORT`
  - Default Value: ✓ (checked)
  - Description: `Generate CSV report`

### **Step 4: Test Script Generation**
- [ ] Click "Build with Parameters"
- [ ] Fill in test values:
  ```
  SCENARIO_NAME: "Test API"
  SCENARIO_JSON: [Copy from examples/sample_scenario_for_jenkins.json]
  TARGET_HOST: "https://rickandmortyapi.com"
  ENVIRONMENT: "dev"
  USERS: "5"
  RUN_TIME: "2m"
  ```
- [ ] Click "Build"
- [ ] Verify build succeeds
- [ ] Check that script is committed to Git

---

## 🎯 Test Execution Pipeline Setup

### **Step 1: Create Pipeline**
- [ ] Go to Jenkins Dashboard
- [ ] Click "New Item"
- [ ] Enter name: `LOCUST-Test-Execution-Pipeline`
- [ ] Select "Pipeline"
- [ ] Click "OK"

### **Step 2: Configure Pipeline**
- [ ] In "Pipeline" section, select "Pipeline script from SCM"
- [ ] Select "Git" as SCM
- [ ] Enter Repository URL
- [ ] Select branch (e.g., `main` or `master`)
- [ ] Set Script Path to: `Jenkinsfile-TestExecution`
- [ ] Click "Save"

### **Step 3: Enable Parameters**
- [ ] Click "Configure" on the pipeline
- [ ] Check "This project is parameterized"
- [ ] Add parameters:

#### **Required Parameters**
- [ ] **SELECTED_SCRIPT** (String Parameter)
  - Name: `SELECTED_SCRIPT`
  - Default Value: (leave empty)
  - Description: `Script to run (auto-populated)`

#### **Optional Parameters**
- [ ] **TARGET_HOST** (String Parameter)
  - Name: `TARGET_HOST`
  - Default Value: `https://api.example.com`
  - Description: `Target host URL`

- [ ] **ENVIRONMENT** (Choice Parameter)
  - Name: `ENVIRONMENT`
  - Choices:
    ```
    dev
    staging
    prod
    ```
  - Description: `Target environment`

- [ ] **USERS** (String Parameter)
  - Name: `USERS`
  - Default Value: `10`
  - Description: `Number of concurrent users`

- [ ] **RUN_TIME** (String Parameter)
  - Name: `RUN_TIME`
  - Default Value: `5m`
  - Description: `Test duration`

- [ ] **MAX_AVG_RESPONSE_TIME** (String Parameter)
  - Name: `MAX_AVG_RESPONSE_TIME`
  - Default Value: `2000`
  - Description: `Max avg response time (ms)`

- [ ] **MIN_SUCCESS_RATE** (String Parameter)
  - Name: `MIN_SUCCESS_RATE`
  - Default Value: `95`
  - Description: `Min success rate (%)`

- [ ] **TEST_DESCRIPTION** (String Parameter)
  - Name: `TEST_DESCRIPTION`
  - Default Value: (leave empty)
  - Description: `Test run description`

- [ ] **TEST_TAGS** (String Parameter)
  - Name: `TEST_TAGS`
  - Default Value: (leave empty)
  - Description: `Test run tags`

- [ ] **USE_LLM_ANALYSIS** (Boolean Parameter)
  - Name: `USE_LLM_ANALYSIS`
  - Default Value: (unchecked)
  - Description: `Enable LLM analysis`

### **Step 4: Test Execution**
- [ ] Click "Build with Parameters"
- [ ] Select a script from the dropdown (should be auto-populated)
- [ ] Fill in test values:
  ```
  TARGET_HOST: "https://rickandmortyapi.com"
  ENVIRONMENT: "dev"
  USERS: "5"
  RUN_TIME: "2m"
  TEST_DESCRIPTION: "Smoke test"
  TEST_TAGS: "smoke,api"
  ```
- [ ] Click "Build"
- [ ] Verify build succeeds
- [ ] Check test results and reports

---

## 🔧 Environment Variables Setup

### **Global Environment Variables**
- [ ] Go to Jenkins Dashboard → Manage Jenkins → Configure System
- [ ] Scroll to "Global properties"
- [ ] Check "Environment variables"
- [ ] Add the following variables:

#### **Required Variables**
- [ ] **GIT_REPO_URL**
  - Name: `GIT_REPO_URL`
  - Value: `https://github.com/yourusername/your-repo.git`

- [ ] **GIT_BRANCH**
  - Name: `GIT_BRANCH`
  - Value: `main` (or your default branch)

- [ ] **PYTHON_PATH**
  - Name: `PYTHON_PATH`
  - Value: `python` (or full path to Python executable)

#### **Optional Variables**
- [ ] **OPENAI_API_KEY** (if using LLM analysis)
  - Name: `OPENAI_API_KEY`
  - Value: `your-openai-api-key`

- [ ] **JENKINS_WORKSPACE**
  - Name: `JENKINS_WORKSPACE`
  - Value: `%WORKSPACE%`

- [ ] **REPORTS_DIR**
  - Name: `REPORTS_DIR`
  - Value: `reports`

- [ ] **SCRIPTS_DIR**
  - Name: `SCRIPTS_DIR`
  - Value: `scripts`

### **Git Credentials**
- [ ] Go to Jenkins Dashboard → Manage Jenkins → Manage Credentials
- [ ] Click "System" → "Global credentials"
- [ ] Click "Add Credentials"
- [ ] Select "Username with password"
- [ ] Enter Git credentials:
  - Username: `your-git-username`
  - Password: `your-git-token-or-password`
  - ID: `git-credentials`
  - Description: `Git repository credentials`

---

## 🧪 Testing Your Setup

### **Test 1: Script Generation**
- [ ] Run Script Generation Pipeline
- [ ] Use sample JSON from `examples/sample_scenario_for_jenkins.json`
- [ ] Verify script is generated and committed to Git
- [ ] Check script appears in repository

### **Test 2: Test Execution**
- [ ] Run Test Execution Pipeline
- [ ] Select the generated script
- [ ] Run with minimal load (1-5 users)
- [ ] Verify test completes successfully
- [ ] Check HTML and CSV reports are generated

### **Test 3: Performance Validation**
- [ ] Run test with higher load (10-20 users)
- [ ] Verify performance thresholds are met
- [ ] Check response times are acceptable
- [ ] Validate success rate is above minimum

---

## 🔍 Troubleshooting Checklist

### **Common Issues**
- [ ] **Pipeline not found**: Check Jenkinsfile path and branch
- [ ] **Parameter errors**: Verify parameter names and types
- [ ] **Git permission denied**: Check Git credentials
- [ ] **Python not found**: Verify PYTHON_PATH environment variable
- [ ] **Script generation fails**: Validate JSON format
- [ ] **Test execution fails**: Check TARGET_HOST accessibility
- [ ] **No scripts available**: Run script generation first

### **Validation Steps**
- [ ] Check Jenkins console output for errors
- [ ] Verify environment variables are set correctly
- [ ] Test Git repository access manually
- [ ] Validate Python environment and packages
- [ ] Check file permissions in workspace

---

## 📊 Success Criteria

### **Script Generation Pipeline**
- [ ] Pipeline builds successfully
- [ ] Script is generated with correct name
- [ ] Script is committed to Git repository
- [ ] Script appears in repository with proper naming

### **Test Execution Pipeline**
- [ ] Pipeline builds successfully
- [ ] Script list is populated automatically
- [ ] Test runs without errors
- [ ] Reports are generated (HTML/CSV)
- [ ] Performance metrics are captured
- [ ] Results are archived properly

### **Integration**
- [ ] Scripts generated by first pipeline are available in second pipeline
- [ ] Both pipelines work together seamlessly
- [ ] Environment variables are properly passed
- [ ] Git operations work correctly

---

## 🎯 Next Steps After Setup

1. **Create your first custom scenario**:
   - Modify the sample JSON for your API
   - Test with your actual endpoints
   - Validate the generated script

2. **Set up monitoring**:
   - Configure performance thresholds
   - Set up alerts for failed builds
   - Monitor resource usage

3. **Scale up**:
   - Increase user load gradually
   - Test different scenarios
   - Optimize performance parameters

4. **Integrate with CI/CD**:
   - Trigger pipelines from code changes
   - Set up automated testing
   - Configure deployment gates

---

## 📚 Documentation References

- [Detailed Parameters Guide](./JENKINS_PIPELINE_PARAMETERS_GUIDE.md)
- [Quick Reference](./JENKINS_PARAMETERS_QUICK_REFERENCE.md)
- [Environment Variables](./JENKINS_ENVIRONMENT_VARIABLES.md)
- [Sample Scenario JSON](../examples/sample_scenario_for_jenkins.json)

---

*✅ Complete this checklist step by step to ensure your Jenkins pipelines are properly configured and ready for use.* 