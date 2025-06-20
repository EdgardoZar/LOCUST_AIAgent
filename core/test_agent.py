"""
Core test agent for automated Locust testing.
"""
import json
import os
import subprocess
import tempfile
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import requests
from dataclasses import dataclass, asdict, field

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

@dataclass
class CommandResult:
    """Stores the result of a shell command execution."""
    command: str
    success: bool = False
    log_output: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    execution_time: float = 0.0

@dataclass
class TestConfig:
    """Configuration for test execution."""
    scenario_name: str
    host: str
    users: int = 1
    spawn_rate: int = 1
    run_time: str = "1m"
    min_wait: int = 1000
    max_wait: int = 5000
    assertions: List[Dict] = None
    extract_variables: Dict[str, str] = None
    headers: Dict[str, str] = None
    params: Dict[str, str] = None
    body: Dict[str, Any] = None
    output_dir: str = "test_reports"
    generate_csv: bool = True
    generate_html: bool = True
    log_level: str = "INFO"

    def __post_init__(self):
        if self.assertions is None:
            self.assertions = []
        if self.extract_variables is None:
            self.extract_variables = {}
        if self.headers is None:
            self.headers = {}
        if self.params is None:
            self.params = {}


@dataclass
class TestResult:
    """Results from test execution."""
    success: bool
    scenario_name: str
    script_path: str
    html_report_path: Optional[str] = None
    csv_report_path: Optional[str] = None
    log_output: List[str] = None
    error_message: Optional[str] = None
    execution_time: float = 0.0
    total_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    requests_per_sec: float = 0.0

    def __post_init__(self):
        if self.log_output is None:
            self.log_output = []


class LocustTestAgent:
    """
    AI Agent for automated Locust testing.
    
    This agent can:
    1. Create test scenarios from JSON configurations
    2. Generate Locust scripts
    3. Execute tests with specified parameters
    4. Save reports in desired locations
    5. Analyze results and provide summaries
    """
    
    def __init__(self, workspace_dir: str = None, script_generator=None):
        """
        Initialize the test agent.
        
        Args:
            workspace_dir: Directory for storing scripts and reports
            script_generator: External script generator (optional)
        """
        self.workspace_dir = workspace_dir or os.getcwd()
        self.scripts_dir = os.path.join(self.workspace_dir, "generated_scripts")
        self.reports_dir = os.path.join(self.workspace_dir, "generated_reports")
        self.script_generator = script_generator
        
        # Create directories if they don't exist
        os.makedirs(self.scripts_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def execute_command(self, cmd: list) -> CommandResult:
        """Executes a shell command and returns the result."""
        result = CommandResult(command=" ".join(cmd))
        start_time = time.time()
        
        self.logger.info(f"Executing command: {' '.join(cmd)}")
        
        try:
            process = subprocess.run(cmd, capture_output=True, text=True, check=False, cwd=self.workspace_dir)
            result.success = process.returncode == 0
            
            # Always log stdout and stderr for debugging
            if process.stdout:
                self.logger.info(f"Command stdout:\n{process.stdout}")
            if process.stderr:
                self.logger.warning(f"Command stderr:\n{process.stderr}")

            if not result.success:
                result.error_message = f"Test failed with return code {process.returncode}"
                self.logger.error(f"Test execution failed: {result.error_message}")
            
            output_lines = process.stdout.split('\n') + process.stderr.split('\n')
            result.log_output = [line.strip() for line in output_lines if line.strip()]

        except FileNotFoundError:
            result.error_message = f"Command not found: {cmd[0]}"
            self.logger.error(f"Test execution failed: {result.error_message}")

        except Exception as e:
            result.error_message = f"Error executing command: {e}"
            self.logger.error(f"Test execution failed: {result.error_message}")

        finally:
            result.execution_time = time.time() - start_time
            return result
    
    def create_scenario_from_json(self, scenario_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a test scenario from JSON configuration.
        
        Args:
            scenario_config: Dictionary containing scenario configuration
            
        Returns:
            Dictionary representing the scenario
        """
        try:
            # Validate required fields
            if "name" not in scenario_config:
                raise ValueError("Missing required field 'name' in scenario config")
            
            # Return the scenario config as-is for compatibility
            return scenario_config
            
        except KeyError as e:
            raise ValueError(f"Missing required field in scenario config: {e}")
        except Exception as e:
            raise ValueError(f"Error creating scenario: {e}")
    
    def generate_script(self, scenario: Dict[str, Any], config: TestConfig) -> str:
        """
        Generate a Locust script for the given scenario.
        
        Args:
            scenario: Scenario configuration dictionary
            config: TestConfig object
            
        Returns:
            Path to generated script
        """
        try:
            # Use external script generator if provided
            if self.script_generator:
                script_content = self.script_generator.generate_script(scenario)
            else:
                # Fallback to basic script generation
                script_content = self._generate_basic_script(scenario, config)
            
            # Create safe filename
            safe_name = ''.join(c if c.isalnum() or c in ('-', '_') else '_' for c in scenario["name"])
            script_filename = f"{safe_name}.py"
            script_path = os.path.join(self.scripts_dir, script_filename)
            
            # Write script to file
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            self.logger.info(f"Generated script: {script_path}")
            return script_path
            
        except Exception as e:
            raise RuntimeError(f"Error generating script: {e}")
    
    def _generate_basic_script(self, scenario: Dict[str, Any], config: TestConfig) -> str:
        """Generate a basic Locust script when no external generator is available."""
        # Convert wait times to integers to avoid division errors
        min_wait_sec = int(config.min_wait) / 1000
        max_wait_sec = int(config.max_wait) / 1000
        
        script_lines = [
            "from locust import HttpUser, task, between",
            "import json",
            "import time",
            "import logging",
            "",
            f"class {self._class_name_from_scenario(scenario['name'])}User(HttpUser):",
            f"    wait_time = between({min_wait_sec}, {max_wait_sec})",
            "",
            "    def on_start(self):",
            "        self.variables = {}",
            "        self.logger = logging.getLogger(__name__)",
            "",
            "    def extract_variables(self, response, extract_config):",
            "        if not extract_config:",
            "            return",
            "        try:",
            "            data = response.json()",
            "            for var_name, json_path in extract_config.items():",
            "                try:",
            "                    parts = json_path.split('.')",
            "                    value = data",
            "                    for part in parts:",
            "                        if isinstance(value, dict):",
            "                            value = value.get(part)",
            "                        else:",
            "                            value = None",
            "                            break",
            "                    if value is not None:",
            "                        self.variables[var_name] = str(value)",
            "                        self.logger.info(f'Extracted {var_name} = {value}')",
            "                except Exception as e:",
            "                    self.logger.error(f'Error extracting {var_name}: {str(e)}')",
            "        except Exception as e:",
            "            self.logger.error(f'Error parsing response JSON: {str(e)}')",
            "",
            "    def replace_variables(self, text):",
            "        if not text:",
            "            return text",
            "        try:",
            "            for var_name, value in self.variables.items():",
            "                text = text.replace(f'{{{{{var_name}}}}}', str(value))",
            "            return text",
            "        except Exception as e:",
            "            self.logger.error(f'Error replacing variables: {str(e)}')",
            "            return text",
            "",
            "    @task",
            "    def run_scenario(self):"
        ]
        
        # Add steps from scenario
        steps = scenario.get("steps", [])
        for step in steps:
            if step.get("type") == "api_call":
                config_data = step.get("config", {})
                method = config_data.get("method", "GET")
                url = config_data.get("url", "")
                headers = config_data.get("headers", {})
                params = config_data.get("params", {})
                body = config_data.get("body", None)
                extract = config_data.get("extract", {})
                assertions = config_data.get("assertions", [])
                
                if not assertions:
                    assertions = [{"type": "status_code", "value": 200}]
                
                script_lines.extend([
                    f"        # Step: {config_data.get('name', 'API Call')}",
                    f"        try:",
                    f"            url = self.replace_variables('{url}')",
                ])
                
                if headers:
                    script_lines.append("            headers = {")
                    for key, value in headers.items():
                        script_lines.append(f"                '{key}': self.replace_variables('{value}'),")
                    script_lines.append("            }")
                else:
                    script_lines.append("            headers = {}")
                
                if params:
                    script_lines.append("            params = {")
                    for key, value in params.items():
                        script_lines.append(f"                '{key}': self.replace_variables('{value}'),")
                    script_lines.append("            }")
                
                if body:
                    script_lines.append("            body = {")
                    for key, value in body.items():
                        if isinstance(value, str):
                            script_lines.append(f"                '{key}': self.replace_variables('{value}'),")
                        else:
                            script_lines.append(f"                '{key}': {json.dumps(value)},")
                    script_lines.append("            }")
                
                script_lines.append(f"            with self.client.{method.lower()}(")
                script_lines.append("                url,")
                if headers:
                    script_lines.append("                headers=headers,")
                if params:
                    script_lines.append("                params=params,")
                if body:
                    script_lines.append("                json=body,")
                script_lines.append("                catch_response=True) as response:")
                
                block_lines = []
                if extract:
                    block_lines.append("                self.extract_variables(response, {")
                    for var_name, json_path in extract.items():
                        block_lines.append(f"                    '{var_name}': '{json_path}',")
                    block_lines.append("                })")
                
                if assertions:
                    block_lines.append("                # Run assertions")
                    for assertion in assertions:
                        if assertion.get("type") == "status_code":
                            block_lines.append(f"                if response.status_code != {assertion.get('value')}:")
                            block_lines.append("                    response.failure('Status code assertion failed')")
                
                if not block_lines:
                    block_lines.append("                pass")
                
                script_lines.extend(block_lines)
                script_lines.append("        except Exception as e:")
                script_lines.append("            self.logger.error(f'Error in API call: {str(e)}')")
                script_lines.append("")
            
            elif step.get("type") == "wait":
                wait_time = step.get("config", {}).get("wait", 1)
                script_lines.extend([
                    "        # Step: Wait",
                    f"        time.sleep({wait_time})",
                    ""
                ])
        
        return "\n".join(script_lines)
    
    def _class_name_from_scenario(self, scenario_name: str) -> str:
        """Generate a class name from a scenario name."""
        class_name = "".join(c if c.isalnum() else "_" for c in scenario_name)
        class_name = "".join(word.capitalize() for word in class_name.split("_") if word)
        return class_name
    
    def execute_test(self, script_path: str, config: TestConfig) -> TestResult:
        """
        Execute a Locust test with the given configuration.
        
        Args:
            script_path: Path to the Locust script
            config: TestConfig object
            
        Returns:
            TestResult object
        """
        start_time = time.time()
        result = TestResult(
            success=False,
            scenario_name=config.scenario_name,
            script_path=script_path
        )
        
        try:
            # Build command
            cmd = [
                "locust", "-f", script_path,
                "--headless",
                "--host", config.host,
                "--users", str(config.users),
                "--spawn-rate", str(config.spawn_rate),
                "--run-time", config.run_time,
                "--loglevel", config.log_level
            ]
            
            # Add report options
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_name = ''.join(c if c.isalnum() or c in ('-', '_') else '_' for c in config.scenario_name)
            
            if config.generate_html:
                html_filename = f"{safe_name}_{timestamp}.html"
                html_path = os.path.join(self.reports_dir, html_filename)
                cmd.extend(["--html", html_path])
                result.html_report_path = html_path
            
            if config.generate_csv:
                csv_prefix = f"{safe_name}_{timestamp}"
                csv_path = os.path.join(self.reports_dir, csv_prefix)
                cmd.extend(["--csv", csv_path])
                result.csv_report_path = f"{csv_path}_stats.csv"
            
            # Execute command
            command_result = self.execute_command(cmd)
            
            # Process output
            result.log_output = command_result.log_output
            result.success = command_result.success
            result.execution_time = command_result.execution_time
            
            if not result.success:
                result.error_message = command_result.error_message
            else:
                self.logger.info("Test execution completed successfully")
                # Parse basic metrics from output
                self._parse_metrics(result, command_result.log_output)
            
            return result
            
        except Exception as e:
            result.error_message = f"Error executing test: {e}"
            result.execution_time = time.time() - start_time
            self.logger.error(f"Test execution error: {e}")
            return result
    
    def _parse_metrics(self, result: TestResult, output_lines: List[str]):
        """Parse basic metrics from Locust output."""
        try:
            for line in output_lines:
                if "Total requests" in line:
                    # Extract total requests
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part.isdigit() and i > 0 and "requests" in parts[i-1]:
                            result.total_requests = int(part)
                            break
                
                elif "Failed requests" in line:
                    # Extract failed requests
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part.isdigit() and i > 0 and "requests" in parts[i-1]:
                            result.failed_requests = int(part)
                            break
                
                elif "Average response time" in line:
                    # Extract average response time
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part.replace('.', '').isdigit() and i > 0 and "time" in parts[i-1]:
                            result.avg_response_time = float(part)
                            break
                
                elif "Requests/sec" in line:
                    # Extract requests per second
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part.replace('.', '').isdigit() and i > 0 and "sec" in parts[i-1]:
                            result.requests_per_sec = float(part)
                            break
                            
        except Exception as e:
            self.logger.warning(f"Error parsing metrics: {e}")
    
    def analyze_results(self, result: TestResult) -> Dict[str, Any]:
        """
        Analyze test results and provide insights.
        
        Args:
            result: TestResult object
            
        Returns:
            Dictionary with analysis results
        """
        analysis = {
            "scenario_name": result.scenario_name,
            "success": result.success,
            "execution_time": result.execution_time,
            "total_requests": result.total_requests,
            "failed_requests": result.failed_requests,
            "success_rate": 0.0,
            "avg_response_time": result.avg_response_time,
            "requests_per_sec": result.requests_per_sec,
            "performance_grade": "UNKNOWN",
            "recommendations": [],
            "summary": ""
        }
        
        if result.total_requests > 0:
            analysis["success_rate"] = ((result.total_requests - result.failed_requests) / result.total_requests) * 100
        
        # Performance grading
        if result.success:
            if analysis["success_rate"] >= 99.5 and result.avg_response_time < 200:
                analysis["performance_grade"] = "EXCELLENT"
            elif analysis["success_rate"] >= 99.0 and result.avg_response_time < 500:
                analysis["performance_grade"] = "GOOD"
            elif analysis["success_rate"] >= 95.0:
                analysis["performance_grade"] = "ACCEPTABLE"
            else:
                analysis["performance_grade"] = "POOR"
        
        # Generate recommendations
        if result.failed_requests > 0:
            analysis["recommendations"].append("Investigate failed requests to improve reliability")
        
        if result.avg_response_time > 1000:
            analysis["recommendations"].append("Response times are high - consider optimization")
        
        if result.requests_per_sec < 1.0:
            analysis["recommendations"].append("Throughput is low - check system capacity")
        
        # Generate summary
        if result.success:
            analysis["summary"] = (
                f"Test completed successfully in {result.execution_time:.2f}s. "
                f"Processed {result.total_requests} requests with {analysis['success_rate']:.1f}% success rate. "
                f"Average response time: {result.avg_response_time:.2f}ms, "
                f"Throughput: {result.requests_per_sec:.2f} req/s. "
                f"Performance grade: {analysis['performance_grade']}"
            )
        else:
            analysis["summary"] = f"Test failed: {result.error_message}"
        
        return analysis
    
    def run_complete_workflow(self, scenario_config: Dict[str, Any], test_config: TestConfig) -> Dict[str, Any]:
        """
        Run the complete testing workflow.
        
        Args:
            scenario_config: JSON configuration for the test scenario
            test_config: TestConfig object with execution parameters
            
        Returns:
            Dictionary with complete workflow results
        """
        self.logger.info(f"Starting complete workflow for scenario: {test_config.scenario_name}")
        
        try:
            # Step 1: Create scenario
            self.logger.info("Step 1: Creating test scenario")
            scenario = self.create_scenario_from_json(scenario_config)
            
            # Step 2: Generate script
            self.logger.info("Step 2: Generating Locust script")
            script_path = self.generate_script(scenario, test_config)
            
            # Step 3: Execute test
            self.logger.info("Step 3: Executing test")
            result = self.execute_test(script_path, test_config)
            
            # Step 4: Analyze results
            self.logger.info("Step 4: Analyzing results")
            analysis = self.analyze_results(result)
            
            # Step 5: Prepare final report
            workflow_result = {
                "workflow_success": result.success,
                "scenario_name": test_config.scenario_name,
                "script_path": script_path,
                "html_report_path": result.html_report_path,
                "csv_report_path": result.csv_report_path,
                "test_result": asdict(result),
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info("Workflow completed successfully")
            return workflow_result
            
        except Exception as e:
            self.logger.error(f"Workflow failed: {e}")
            return {
                "workflow_success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            } 