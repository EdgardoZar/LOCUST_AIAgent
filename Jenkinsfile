pipeline {
    agent any
    
    parameters {
        // Basic test parameters
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
        TIMESTAMP = "${new Date().format('yyyyMMdd_HHmmss')}"
        
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
                checkout scm
                echo "Checked out code from ${env.BRANCH_NAME}"
                echo "Build parameters:"
                echo "  Target Host: ${params.TARGET_HOST}"
                echo "  Environment: ${params.ENVIRONMENT}"
                echo "  Users: ${params.USERS}"
                echo "  Run Time: ${params.RUN_TIME}"
                echo "  LLM Analysis: ${params.USE_LLM_ANALYSIS}"
            }
        }
        
        stage('Setup Environment') {
            steps {
                script {
                    // Create workspace directories
                    bat "if not exist ${WORKSPACE_DIR} mkdir ${WORKSPACE_DIR}"
                    bat "if not exist ${REPORTS_DIR} mkdir ${REPORTS_DIR}"
                    
                    // Setup Python environment
                    bat """
                        python -m venv venv
                        call venv\\Scripts\\activate.bat
                        python -m pip install --upgrade pip
                        pip install -r requirements.txt
                        pip install -e .
                    """
                }
            }
        }
        
        stage('Create Test Configuration') {
            steps {
                script {
                    // Create scenario configuration
                    def scenarioConfig = [
                        name: "Jenkins Pipeline Test - ${params.ENVIRONMENT}",
                        description: "Automated test from Jenkins pipeline for ${params.ENVIRONMENT} environment",
                        min_wait: params.MIN_WAIT,
                        max_wait: params.MAX_WAIT,
                        steps: [
                            [
                                id: 1,
                                type: "api_call",
                                config: [
                                    name: "Health Check",
                                    method: "GET",
                                    url: "/health",
                                    headers: [
                                        "Content-Type": "application/json",
                                        "User-Agent": "Jenkins-Locust-AI-Agent/1.0"
                                    ],
                                    params: [:],
                                    body: null,
                                    extract: [:],
                                    assertions: [
                                        [type: "status_code", value: 200]
                                    ]
                                ]
                            ],
                            [
                                id: 2,
                                type: "wait",
                                config: [wait: 1]
                            ],
                            [
                                id: 3,
                                type: "api_call",
                                config: [
                                    name: "API Endpoint Test",
                                    method: "GET",
                                    url: "/api/v1/status",
                                    headers: [
                                        "Content-Type": "application/json",
                                        "User-Agent": "Jenkins-Locust-AI-Agent/1.0"
                                    ],
                                    params: [:],
                                    body: null,
                                    extract: [
                                        status: "\$.status"
                                    ],
                                    assertions: [
                                        [type: "status_code", value: 200],
                                        [type: "json_path", path: "\$.status", value: "healthy"]
                                    ]
                                ]
                            ]
                        ]
                    ]
                    
                    // Add authentication if API token is provided
                    if (params.API_TOKEN) {
                        scenarioConfig.steps[2].config.headers["Authorization"] = "Bearer ${params.API_TOKEN}"
                    }
                    
                    writeFile file: "${WORKSPACE_DIR}\\scenario_config.json", text: groovy.json.JsonOutput.toJson(scenarioConfig)
                    
                    // Create test configuration
                    def testConfig = [
                        scenario_name: "Jenkins Pipeline Test - ${params.ENVIRONMENT}",
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
                    
                    echo "Test configuration created:"
                    echo "  Scenario: ${testConfig.scenario_name}"
                    echo "  Host: ${testConfig.host}"
                    echo "  Users: ${testConfig.users}"
                    echo "  Run Time: ${testConfig.run_time}"
                }
            }
        }
        
        stage('Run AI Agent') {
            steps {
                script {
                    // Activate virtual environment and run AI agent
                    bat """
                        call venv\\Scripts\\activate.bat
                        cd ${WORKSPACE}
                        
                        rem Add current directory to Python path
                        set PYTHONPATH=%PYTHONPATH%;${WORKSPACE}
                        
                        rem Run the AI agent
                        python run_example.py
                    """
                    
                    // Run with LLM analysis if enabled
                    if (params.USE_LLM_ANALYSIS) {
                        withCredentials([string(credentialsId: 'openai-api-key', variable: 'OPENAI_API_KEY')]) {
                            bat """
                                call venv\\Scripts\\activate.bat
                                cd ${WORKSPACE}
                                set PYTHONPATH=%PYTHONPATH%;${WORKSPACE}
                                set OPENAI_API_KEY=${OPENAI_API_KEY}
                                
                                rem Run with LLM analysis
                                python -c "
import sys
sys.path.insert(0, '.')
from Locust_AI_Agent.core.test_agent import LocustTestAgent, TestConfig
from Locust_AI_Agent.analysis.llm_analyzer import LLMAnalyzer
import json

# Load configurations
with open('${WORKSPACE_DIR}\\scenario_config.json', 'r') as f:
    scenario_config = json.load(f)
with open('${WORKSPACE_DIR}\\test_config.json', 'r') as f:
    test_config_data = json.load(f)

# Create test config
test_config = TestConfig(**test_config_data)

# Run workflow
agent = LocustTestAgent(workspace_dir='${WORKSPACE_DIR}')
workflow_result = agent.run_complete_workflow(scenario_config, test_config)

# LLM analysis
llm_analyzer = LLMAnalyzer(api_key='${OPENAI_API_KEY}')
llm_analysis = llm_analyzer.analyze_test_results(
    workflow_result['test_result'],
    workflow_result.get('html_report_path')
)
workflow_result['llm_analysis'] = llm_analysis

# Save results
with open('${WORKSPACE_DIR}\\test_results_with_llm.json', 'w') as f:
    json.dump(workflow_result, f, indent=2)
"
                            """
                        }
                    }
                }
            }
        }
        
        stage('Archive Results') {
            steps {
                script {
                    // Archive test results and reports
                    archiveArtifacts artifacts: "${WORKSPACE_DIR}\\test_results.json", fingerprint: true
                    
                    if (params.USE_LLM_ANALYSIS) {
                        archiveArtifacts artifacts: "${WORKSPACE_DIR}\\test_results_with_llm.json", fingerprint: true
                    }
                    
                    // Archive generated reports
                    if (params.GENERATE_HTML_REPORT) {
                        archiveArtifacts artifacts: "${REPORTS_DIR}\\**\\*.html", fingerprint: true
                    }
                    
                    if (params.GENERATE_CSV_REPORT) {
                        archiveArtifacts artifacts: "${REPORTS_DIR}\\**\\*.csv", fingerprint: true
                    }
                    
                    // Archive generated scripts
                    archiveArtifacts artifacts: "${WORKSPACE_DIR}\\generated_scripts\\**\\*", fingerprint: true
                }
            }
        }
        
        stage('Analyze Results') {
            steps {
                script {
                    // Load and analyze test results
                    def resultsText = readFile file: "${WORKSPACE_DIR}\\test_results.json"
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
                        
                        if (testResult.avg_response_time > params.MAX_AVG_RESPONSE_TIME) {
                            performanceIssues.add("Average response time (${testResult.avg_response_time}ms) exceeds threshold (${params.MAX_AVG_RESPONSE_TIME}ms)")
                        }
                        
                        if (successRate < params.MIN_SUCCESS_RATE) {
                            performanceIssues.add("Success rate (${successRate}%) below threshold (${params.MIN_SUCCESS_RATE}%)")
                        }
                        
                        if (testResult.requests_per_sec < params.MIN_REQUESTS_PER_SEC) {
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
                    
                    // LLM analysis summary
                    if (params.USE_LLM_ANALYSIS && results.llm_analysis) {
                        def llmAnalysis = results.llm_analysis
                        echo "LLM Analysis:"
                        echo "  Performance Grade: ${llmAnalysis.performance_grade}"
                        echo "  Summary: ${llmAnalysis.summary}"
                        
                        if (llmAnalysis.key_insights) {
                            echo "  Key Insights:"
                            llmAnalysis.key_insights.each { insight ->
                                echo "    • ${insight}"
                            }
                        }
                        
                        if (llmAnalysis.recommendations) {
                            echo "  Recommendations:"
                            llmAnalysis.recommendations.each { rec ->
                                echo "    • ${rec}"
                            }
                        }
                    }
                }
            }
        }
        
        stage('Publish HTML Report') {
            when {
                expression { params.GENERATE_HTML_REPORT }
            }
            steps {
                script {
                    // Check if HTML report exists
                    def htmlReportExists = fileExists "${REPORTS_DIR}\\*.html"
                    if (htmlReportExists) {
                        publishHTML([
                            allowMissing: false,
                            alwaysLinkToLastBuild: true,
                            keepAll: true,
                            reportDir: REPORTS_DIR,
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
                
                // Clean up workspace if needed
                if (currentBuild.result == 'SUCCESS' || currentBuild.result == 'UNSTABLE') {
                    echo "Test completed successfully"
                } else {
                    echo "Test failed - check logs for details"
                }
            }
        }
        
        success {
            echo "Pipeline succeeded! Check the HTML report for detailed results."
        }
        
        failure {
            echo "Pipeline failed! Check the console output for error details."
        }
        
        unstable {
            echo "Pipeline completed with warnings. Performance thresholds not met."
        }
    }
} 