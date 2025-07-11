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
import csv
from dataclasses import dataclass, asdict, field

# Import the enhanced script generator
try:
    from .enhanced_script_generator import EnhancedScriptGenerator
    ENHANCED_GENERATOR_AVAILABLE = True
except ImportError:
    ENHANCED_GENERATOR_AVAILABLE = False

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
    use_enhanced_generator: bool = True  # New flag for enhanced features

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
    2. Generate Locust scripts (basic or enhanced)
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
        self.script_generator = script_generator
        
        # Create directories if they don't exist
        os.makedirs(self.scripts_dir, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Log enhanced generator availability
        if ENHANCED_GENERATOR_AVAILABLE:
            self.logger.info("Enhanced script generator is available")
        else:
            self.logger.warning("Enhanced script generator not available, using basic generator")
    
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
            # Check if we should use enhanced generator
            if (config.use_enhanced_generator and 
                ENHANCED_GENERATOR_AVAILABLE and 
                self._is_enhanced_scenario(scenario)):
                
                self.logger.info("Using enhanced script generator")
                return self._generate_enhanced_script(scenario, config)
            else:
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
                
                self.logger.info(f"Generated basic script: {script_path}")
                return script_path
                
        except Exception as e:
            self.logger.error(f"Error generating script: {e}")
            raise
    
    def _is_enhanced_scenario(self, scenario: Dict[str, Any]) -> bool:
        """
        Check if scenario uses enhanced features.
        
        Args:
            scenario: Scenario configuration
            
        Returns:
            True if scenario uses enhanced features
        """
        # Check for enhanced features
        has_parameters = 'parameters' in scenario and 'data_sources' in scenario.get('parameters', {})
        has_enhanced_extract = any(
            step.get('extract') and 
            any(isinstance(v, dict) and 'type' in v for v in step['extract'].values())
            for step in scenario.get('steps', [])
        )
        has_enhanced_assertions = any(
            step.get('assertions') and 
            any(isinstance(a, dict) and 'type' in a for a in step['assertions'])
            for step in scenario.get('steps', [])
        )
        
        return has_parameters or has_enhanced_extract or has_enhanced_assertions
    
    def _generate_enhanced_script(self, scenario: Dict[str, Any], config: TestConfig) -> str:
        """
        Generate script using enhanced generator.
        
        Args:
            scenario: Scenario configuration
            config: Test configuration
            
        Returns:
            Path to generated script
        """
        try:
            # Create safe filename for output
            safe_name = ''.join(c if c.isalnum() or c in ('-', '_') else '_' for c in scenario["name"])
            script_filename = f"{safe_name}.py"
            script_path = os.path.join(self.scripts_dir, script_filename)
            
            # Create temporary scenario file in the same directory as the script
            scenario_file = os.path.join(self.scripts_dir, f"{safe_name}_scenario.json")
            
            # Update file paths in scenario to be relative to the scenario file location
            updated_scenario = self._update_scenario_paths(scenario, self.scripts_dir)
            
            with open(scenario_file, 'w') as f:
                json.dump(updated_scenario, f, indent=2)
            
            # Use enhanced generator
            generator = EnhancedScriptGenerator(scenario_file, script_path)
            generator.generate_script()
            
            # Clean up temporary scenario file
            os.remove(scenario_file)
            
            self.logger.info(f"Generated enhanced script: {script_path}")
            return script_path
            
        except Exception as e:
            self.logger.error(f"Error generating enhanced script: {e}")
            raise
    
    def _update_scenario_paths(self, scenario: Dict[str, Any], base_dir: str) -> Dict[str, Any]:
        """
        Update file paths in scenario to be relative to the base directory.
        
        Args:
            scenario: Original scenario configuration
            base_dir: Base directory for path resolution
            
        Returns:
            Updated scenario with corrected paths
        """
        import copy
        updated_scenario = copy.deepcopy(scenario)
        
        # Update data source file paths
        if 'parameters' in updated_scenario and 'data_sources' in updated_scenario['parameters']:
            for source in updated_scenario['parameters']['data_sources']:
                if 'file' in source:
                    # Make path relative to the workspace directory
                    original_path = source['file']
                    if not os.path.isabs(original_path):
                        # If it's already relative, make it relative to workspace
                        source['file'] = os.path.relpath(
                            os.path.join(self.workspace_dir, original_path),
                            base_dir
                        )
        
        return updated_scenario
    
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
            # Create a unique directory for this test run
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_name = ''.join(c if c.isalnum() or c in ('-', '_') else '_' for c in config.scenario_name)
            run_output_dir_name = f"{safe_name}_{timestamp}"
            run_output_dir = os.path.join(config.output_dir, run_output_dir_name)
            os.makedirs(run_output_dir, exist_ok=True)

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
            if config.generate_html:
                html_path = os.path.join(run_output_dir, "report.html")
                cmd.extend(["--html", html_path])
                result.html_report_path = html_path
            
            if config.generate_csv:
                csv_prefix = os.path.join(run_output_dir, "report")
                cmd.extend(["--csv", csv_prefix])
                result.csv_report_path = f"{csv_prefix}_stats.csv"
            
            # Execute command
            command_result = self.execute_command(cmd)
            
            result.log_output = command_result.log_output
            result.execution_time = command_result.execution_time
            
            # A locust run is "successful" if the process ran and we have a report,
            # even if there are test failures (exit code 1).
            if os.path.exists(result.csv_report_path):
                self.logger.info("Test execution completed, CSV report found.")
                result.success = True
                self._parse_metrics_from_csv(result)
            else:
                self.logger.warning("Could not find CSV report. Parsing from logs as a fallback.")
                result.success = False # The run itself failed if no report was generated
                self._parse_metrics_from_log(result, command_result.log_output)
                
            if not result.success and not result.error_message:
                result.error_message = command_result.error_message
            
            return result
            
        except Exception as e:
            result.error_message = f"Error executing test: {e}"
            result.execution_time = time.time() - start_time
            self.logger.error(f"Test execution error: {e}")
            return result
    
    def _parse_metrics_from_log(self, result: TestResult, output_lines: List[str]):
        """Parse basic metrics from Locust output as a fallback."""
        self.logger.info("Attempting to parse metrics from log output...")
        try:
            aggregated_line = None
            for line in reversed(output_lines):
                if line.strip().startswith("Aggregated"):
                    aggregated_line = line
                    break
            
            if aggregated_line:
                # Expected format: Aggregated  <reqs> <fails> | <avg> <min> <max> <med> | <rps> <frs>
                parts = [p.strip() for p in aggregated_line.split('|')]
                if len(parts) == 3:
                    reqs_part = parts[0]
                    stats_part = parts[1]
                    rps_part = parts[2]
                    
                    reqs_fails_values = [v for v in reqs_part.split() if v.isdigit()]
                    if len(reqs_fails_values) >= 2:
                        result.total_requests = int(reqs_fails_values[-2])
                        result.failed_requests = int(reqs_fails_values[-1])
                    
                    stats_values = [v for v in stats_part.split() if v.replace('.', '', 1).isdigit()]
                    if len(stats_values) >= 1:
                        result.avg_response_time = float(stats_values[0])

                    rps_values = [v for v in rps_part.split() if v.replace('.', '', 1).isdigit()]
                    if len(rps_values) >= 1:
                        result.requests_per_sec = float(rps_values[0])
                    self.logger.info("Successfully parsed metrics from log.")
                else:
                    self.logger.warning("Could not parse aggregated log line: unexpected format.")
            else:
                self.logger.warning("Could not find 'Aggregated' line in log output.")
        except Exception as e:
            self.logger.warning(f"Error parsing metrics from log: {e}")

    def _parse_metrics_from_csv(self, result: TestResult):
        """Parse metrics from the Locust CSV stats file."""
        try:
            with open(result.csv_report_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['Name'] == 'Aggregated':
                        result.total_requests = int(row['Request Count'])
                        result.failed_requests = int(row['Failure Count'])
                        result.avg_response_time = float(row['Average Response Time'])
                        result.requests_per_sec = float(row['Requests/s'])
                        self.logger.info(f"Successfully parsed metrics from CSV for 'Aggregated' row.")
                        return
            self.logger.warning("Could not find 'Aggregated' row in CSV stats file.")
        except FileNotFoundError:
            self.logger.warning(f"CSV stats file not found at: {result.csv_report_path}")
        except Exception as e:
            self.logger.warning(f"Error parsing metrics from CSV: {e}")

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