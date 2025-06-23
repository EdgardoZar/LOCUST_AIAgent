pipeline {
    agent any
    
    parameters {
        // Pipeline mode selection
        choice(name: 'PIPELINE_MODE', choices: ['generate_script', 'run_test'], description: 'Pipeline mode')
        
        // Script generation parameters
        string(name: 'SCENARIO_NAME', defaultValue: '', description: 'Name of the test scenario')
        text(name: 'SCENARIO_JSON', defaultValue: '', description: 'JSON configuration for the scenario')
        
        // Test execution parameters
        string(name: 'SELECTED_SCRIPT', defaultValue: '', description: 'Script to run (will be populated from available scripts)')
        string(name: 'TARGET_HOST', defaultValue: 'https://api.example.com', description: 'Target host URL for testing')
        string(name: 'API_TOKEN', defaultValue: '', description: 'API token for authentication (optional)')
        choice(name: 'ENVIRONMENT', choices: ['dev', 'staging', 'prod'], description: 'Target environment')
        
        // Test configuration
        string(name: 'USERS', defaultValue: '10', description: 'Number of concurrent users')
        string(name: 'SPAWN_RATE', defaultValue: '2', description: 'User spawn rate per second')
        string(name: 'RUN_TIME', defaultValue: '5m', description: 'Test duration (e.g., 5m, 10m, 1h)')
        string(name: 'MIN_WAIT', defaultValue: '1000', description: 'Minimum wait time between requests (ms)')
        string(name: 'MAX_WAIT', defaultValue: '5000', description: 'Maximum wait time between requests (ms)')
        
        // Advanced options
        booleanParam(name: 'USE_LLM_ANALYSIS', defaultValue: false, description: 'Enable LLM-powered analysis')
        booleanParam(name: 'GENERATE_HTML_REPORT', defaultValue: true, description: 'Generate HTML test report')
        booleanParam(name: 'GENERATE_CSV_REPORT', defaultValue: true, description: 'Generate CSV test report')
        string(name: 'LOG_LEVEL', defaultValue: 'INFO', description: 'Logging level (DEBUG, INFO, WARNING, ERROR)')
        
        // Performance thresholds
        string(name: 'MAX_AVG_RESPONSE_TIME', defaultValue: '2000', description: 'Maximum average response time (ms)')
        string(name: 'MIN_SUCCESS_RATE', defaultValue: '95', description: 'Minimum success rate percentage')
        string(name: 'MIN_REQUESTS_PER_SEC', defaultValue: '10', description: 'Minimum requests per second')
    }
    
    environment {
        PYTHON_VERSION = '3.9'
        WORKSPACE_DIR = "${WORKSPACE}\\test_workspace"
        REPORTS_DIR = "${WORKSPACE}\\test_reports"
        SCRIPTS_DIR = "${WORKSPACE}\\generated_scripts"
        TIMESTAMP = "${new Date().format('yyyyMMdd_HHmmss')}"
        
        // Git configuration
        GIT_SCRIPTS_BRANCH = 'generated-scripts'
        GIT_SCRIPTS_FOLDER = 'test_workspace/generated_scripts'
        
        // Test configuration from parameters
        TEST_HOST = "${params.TARGET_HOST}"
        TEST_USERS = "${params.USERS}"
        TEST_SPAWN_RATE = "${params.SPAWN_RATE}"
        TEST_RUN_TIME = "${params.RUN_TIME}"
        TEST_MIN_WAIT = "${params.MIN_WAIT}"
        TEST_MAX_WAIT = "${params.MAX_WAIT}"
        TEST_LOG_LEVEL = "${params.LOG_LEVEL}"
        
        // Performance thresholds
        THRESHOLD_MAX_RESPONSE_TIME = "${params.MAX_AVG_RESPONSE_TIME}"
        THRESHOLD_MIN_SUCCESS_RATE = "${params.MIN_SUCCESS_RATE}"
        THRESHOLD_MIN_REQUESTS_PER_SEC = "${params.MIN_REQUESTS_PER_SEC}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout([$class: 'GitSCM', 
                    branches: [[name: '*/main']], 
                    doGenerateSubmoduleConfigurations: false, 
                    extensions: [], 
                    submoduleCfg: [], 
                    userRemoteConfigs: [[
                        credentialsId: 'github-credentials',
                        url: 'https://github.com/EdgardoZar/LOCUST_AIAgent.git'
                    ]]
                ])
                echo "Checked out code from ${env.BRANCH_NAME}"
                echo "Pipeline Mode: ${params.PIPELINE_MODE}"
            }
        }
        
        stage('Setup Environment') {
            steps {
                script {
                    // Create directories
                    bat "if not exist \"${WORKSPACE_DIR}\" mkdir \"${WORKSPACE_DIR}\""
                    bat "if not exist \"${REPORTS_DIR}\" mkdir \"${REPORTS_DIR}\""
                    bat "if not exist \"${SCRIPTS_DIR}\" mkdir \"${SCRIPTS_DIR}\""
                    
                    // Setup Python virtual environment
                    bat """
                        if not exist venv (
                            python -m venv venv
                        )
                        call venv\\Scripts\\activate.bat
                        pip install --upgrade pip
                        pip install -r requirements.txt
                        pip install -e .
                    """
                }
            }
        }
        
        stage('Script Generation') {
            when {
                expression { params.PIPELINE_MODE == 'generate_script' }
            }
            steps {
                script {
                    echo "Generating script from scenario configuration..."
                    
                    // Parse scenario JSON
                    def scenarioConfig = new groovy.json.JsonSlurper().parseText(params.SCENARIO_JSON)
                    
                    // Create test configuration
                    def testConfig = [
                        scenario_name: params.SCENARIO_NAME,
                        host: params.TARGET_HOST,
                        users: params.USERS,
                        spawn_rate: params.SPAWN_RATE,
                        run_time: params.RUN_TIME,
                        min_wait: params.MIN_WAIT,
                        max_wait: params.MAX_WAIT,
                        assertions: [
                            [type: "status_code", value: 200]
                        ],
                        extract_variables: [:],
                        headers: [
                            "Content-Type": "application/json",
                            "User-Agent": "Jenkins-Locust-AI-Agent/1.0"
                        ],
                        params: [:],
                        body: [:],
                        output_dir: REPORTS_DIR,
                        generate_csv: params.GENERATE_CSV_REPORT,
                        generate_html: params.GENERATE_HTML_REPORT,
                        log_level: params.LOG_LEVEL
                    ]
                    
                    // Save configurations
                    writeFile file: "${WORKSPACE_DIR}\\scenario_config.json", text: groovy.json.JsonOutput.toJson(scenarioConfig)
                    writeFile file: "${WORKSPACE_DIR}\\test_config.json", text: groovy.json.JsonOutput.toJson(testConfig)
                    
                    // Generate script using AI Agent
                    bat """
                        call venv\\Scripts\\activate.bat
                        cd ${WORKSPACE}
                        set PYTHONPATH=%PYTHONPATH%;${WORKSPACE}
                        
                        python -c "
import sys
sys.path.insert(0, '.')
from Locust_AI_Agent.core.test_agent import LocustTestAgent, TestConfig
import json

# Load configurations
with open('${WORKSPACE_DIR}\\scenario_config.json', 'r') as f:
    scenario_config = json.load(f)
with open('${WORKSPACE_DIR}\\test_config.json', 'r') as f:
    test_config_data = json.load(f)

# Create test config
test_config = TestConfig(**test_config_data)

# Generate script
agent = LocustTestAgent(workspace_dir='${WORKSPACE_DIR}')
script_path = agent.generate_script(scenario_config, test_config)
print(f'Script generated: {script_path}')
"
                    """
                    
                    // Commit script to Git
                    bat """
                        git config user.email "jenkins@example.com"
                        git config user.name "Jenkins Pipeline"
                        
                        rem Create scripts branch if it doesn't exist
                        git checkout -b ${GIT_SCRIPTS_BRANCH} 2>nul || git checkout ${GIT_SCRIPTS_BRANCH}
                        
                        rem Add generated script
                        git add ${SCRIPTS_DIR}\\*.py
                        git commit -m "Generated script: ${params.SCENARIO_NAME} - ${TIMESTAMP}" || echo "No changes to commit"
                        
                        rem Push to remote
                        git push origin ${GIT_SCRIPTS_BRANCH} || echo "Push failed or no changes"
                        
                        rem Return to main branch
                        git checkout main
                    """
                    
                    echo "Script generation completed successfully!"
                }
            }
        }
        
        stage('List Available Scripts') {
            when {
                expression { params.PIPELINE_MODE == 'run_test' }
            }
            steps {
                script {
                    echo "Fetching available scripts from Git..."
                    
                    // Fetch scripts branch
                    bat """
                        git fetch origin ${GIT_SCRIPTS_BRANCH}:${GIT_SCRIPTS_BRANCH} || echo "Branch not found"
                        git checkout ${GIT_SCRIPTS_BRANCH} || echo "Could not checkout scripts branch"
                    """
                    
                    // List available scripts
                    def scriptFiles = bat(script: "dir ${SCRIPTS_DIR}\\*.py /b", returnStdout: true).trim()
                    if (scriptFiles) {
                        echo "Available scripts:"
                        scriptFiles.split('\n').each { script ->
                            echo "  - ${script}"
                        }
                        
                        // If no script selected, use the first one
                        if (!params.SELECTED_SCRIPT) {
                            def firstScript = scriptFiles.split('\n')[0]
                            env.SELECTED_SCRIPT = firstScript
                            echo "Auto-selected script: ${firstScript}"
                        }
                    } else {
                        error "No scripts found in ${SCRIPTS_DIR}"
                    }
                    
                    // Return to main branch
                    bat "git checkout main"
                }
            }
        }
        
        stage('Run Test') {
            when {
                expression { params.PIPELINE_MODE == 'run_test' }
            }
            steps {
                script {
                    echo "Running test with script: ${env.SELECTED_SCRIPT}"
                    
                    // Create test configuration
                    def testConfig = [
                        scenario_name: env.SELECTED_SCRIPT.replace('.py', ''),
                        host: params.TARGET_HOST,
                        users: params.USERS,
                        spawn_rate: params.SPAWN_RATE,
                        run_time: params.RUN_TIME,
                        min_wait: params.MIN_WAIT,
                        max_wait: params.MAX_WAIT,
                        assertions: [
                            [type: "status_code", value: 200]
                        ],
                        extract_variables: [:],
                        headers: [
                            "Content-Type": "application/json",
                            "User-Agent": "Jenkins-Locust-AI-Agent/1.0"
                        ],
                        params: [:],
                        body: [:],
                        output_dir: REPORTS_DIR,
                        generate_csv: params.GENERATE_CSV_REPORT,
                        generate_html: params.GENERATE_HTML_REPORT,
                        log_level: params.LOG_LEVEL
                    ]
                    
                    writeFile file: "${WORKSPACE_DIR}\\test_config.json", text: groovy.json.JsonOutput.toJson(testConfig)
                    
                    // Fetch the selected script
                    bat """
                        git fetch origin ${GIT_SCRIPTS_BRANCH}:${GIT_SCRIPTS_BRANCH}
                        git checkout ${GIT_SCRIPTS_BRANCH} -- ${SCRIPTS_DIR}\\${env.SELECTED_SCRIPT}
                        git checkout main
                    """
                    
                    // Run the test
                    bat """
                        call venv\\Scripts\\activate.bat
                        cd ${WORKSPACE}
                        set PYTHONPATH=%PYTHONPATH%;${WORKSPACE}
                        
                        python -c "
import sys
sys.path.insert(0, '.')
from Locust_AI_Agent.core.test_agent import LocustTestAgent, TestConfig
import json

# Load test config
with open('${WORKSPACE_DIR}\\test_config.json', 'r') as f:
    test_config_data = json.load(f)

# Create test config
test_config = TestConfig(**test_config_data)

# Run test
agent = LocustTestAgent(workspace_dir='${WORKSPACE_DIR}')
script_path = '${SCRIPTS_DIR}\\${env.SELECTED_SCRIPT}'
result = agent.execute_test(script_path, test_config)

# Save results
workflow_result = {
    'workflow_success': result.success,
    'scenario_name': result.scenario_name,
    'script_path': result.script_path,
    'html_report_path': result.html_report_path,
    'csv_report_path': result.csv_report_path,
    'test_result': {
        'execution_time': result.execution_time,
        'total_requests': result.total_requests,
        'failed_requests': result.failed_requests,
        'avg_response_time': result.avg_response_time,
        'requests_per_sec': result.requests_per_sec
    }
}

with open('${WORKSPACE_DIR}\\test_results.json', 'w') as f:
    json.dump(workflow_result, f, indent=2)

print(f'Test completed: Success={result.success}')
"
                    """
                }
            }
        }
        
        stage('Archive Results') {
            when {
                expression { params.PIPELINE_MODE == 'run_test' }
            }
            steps {
                script {
                    // Archive test results and reports
                    archiveArtifacts artifacts: "test_workspace\\test_results.json", fingerprint: true
                    
                    // Archive generated reports
                    if (params.GENERATE_HTML_REPORT) {
                        archiveArtifacts artifacts: "test_reports\\**\\*.html", fingerprint: true
                    }
                    
                    if (params.GENERATE_CSV_REPORT) {
                        archiveArtifacts artifacts: "test_reports\\**\\*.csv", fingerprint: true
                    }
                }
            }
        }
        
        stage('Analyze Results') {
            when {
                expression { params.PIPELINE_MODE == 'run_test' }
            }
            steps {
                script {
                    // Load and analyze test results
                    def resultsText = readFile file: "test_workspace\\test_results.json"
                    def results = new groovy.json.JsonSlurper().parseText(resultsText)
                    
                    echo "Test Results Analysis:"
                    echo "  Success: ${results.workflow_success}"
                    echo "  Scenario: ${results.scenario_name}"
                    
                    if (results.test_result) {
                        def testResult = results.test_result
                        echo "  Execution Time: ${testResult.execution_time}s"
                        echo "  Total Requests: ${testResult.total_requests}"
                        echo "  Failed Requests: ${testResult.failed_requests}"
                        echo "  Avg Response Time: ${testResult.avg_response_time}ms"
                        echo "  Requests/sec: ${testResult.requests_per_sec}"
                        
                        // Calculate success rate
                        def successRate = testResult.total_requests > 0 ? 
                            ((testResult.total_requests - testResult.failed_requests) / testResult.total_requests * 100) : 0
                        echo "  Success Rate: ${successRate}%"
                        
                        // Performance threshold validation
                        def performanceIssues = []
                        
                        if (testResult.avg_response_time > params.MAX_AVG_RESPONSE_TIME.toInteger()) {
                            performanceIssues.add("Average response time (${testResult.avg_response_time}ms) exceeds threshold (${params.MAX_AVG_RESPONSE_TIME}ms)")
                        }
                        
                        if (successRate < params.MIN_SUCCESS_RATE.toInteger()) {
                            performanceIssues.add("Success rate (${successRate}%) below threshold (${params.MIN_SUCCESS_RATE}%)")
                        }
                        
                        if (testResult.requests_per_sec < params.MIN_REQUESTS_PER_SEC.toInteger()) {
                            performanceIssues.add("Requests per second (${testResult.requests_per_sec}) below threshold (${params.MIN_REQUESTS_PER_SEC})")
                        }
                        
                        if (performanceIssues.size() > 0) {
                            echo "Performance Issues Detected:"
                            performanceIssues.each { issue ->
                                echo "  - ${issue}"
                            }
                            currentBuild.result = 'UNSTABLE'
                        } else {
                            echo "All performance thresholds met!"
                        }
                    }
                }
            }
        }
        
        stage('Publish HTML Report') {
            when {
                allOf {
                    expression { params.PIPELINE_MODE == 'run_test' }
                    expression { params.GENERATE_HTML_REPORT }
                }
            }
            steps {
                script {
                    // Check if HTML report exists
                    def htmlReportExists = fileExists "test_reports\\*.html"
                    if (htmlReportExists) {
                        publishHTML([
                            allowMissing: false,
                            alwaysLinkToLastBuild: true,
                            keepAll: true,
                            reportDir: 'test_reports',
                            reportFiles: '*.html',
                            reportName: 'Locust Test Report',
                            reportTitles: 'Performance Test Results'
                        ])
                        echo "HTML report published successfully"
                    } else {
                        echo "No HTML report found to publish"
                    }
                }
            }
        }
    }
    
    post {
        always {
            script {
                echo "Pipeline completed with result: ${currentBuild.result}"
                echo "Build URL: ${env.BUILD_URL}"
                
                if (params.PIPELINE_MODE == 'generate_script') {
                    echo "Script generation completed"
                } else {
                    if (currentBuild.result == 'SUCCESS' || currentBuild.result == 'UNSTABLE') {
                        echo "Test completed successfully"
                    } else {
                        echo "Test failed - check logs for details"
                    }
                }
            }
        }
        
        success {
            if (params.PIPELINE_MODE == 'generate_script') {
                echo "Script generated and saved to Git successfully!"
            } else {
                echo "Test completed successfully! Check the HTML report for detailed results."
            }
        }
        
        failure {
            echo "Pipeline failed! Check the console output for error details."
        }
        
        unstable {
            echo "Pipeline completed with warnings. Performance thresholds not met."
        }
    }
} 