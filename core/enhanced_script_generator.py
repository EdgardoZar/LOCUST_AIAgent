import json
import csv
import random
import re
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path

class EnhancedScriptGenerator:
    """
    Enhanced script generator supporting:
    - Dynamic parameters from CSV/JSON files
    - Variable extraction and correlation
    - Comprehensive assertions (status code, response time, JSON path, regex, text)
    - Left/right boundary text extraction
    """
    
    def __init__(self, scenario_file: str, output_file: str):
        self.scenario_file = scenario_file
        self.output_file = output_file
        self.scenario_data = {}
        self.data_sources = {}
        self.logger = logging.getLogger(__name__)
        
    def load_scenario(self):
        """Load the scenario JSON file"""
        try:
            with open(self.scenario_file, 'r', encoding='utf-8') as f:
                self.scenario_data = json.load(f)
            self.logger.info(f"Loaded scenario: {self.scenario_data.get('name', 'Unknown')}")
        except Exception as e:
            self.logger.error(f"Error loading scenario file: {str(e)}")
            raise
            
    def load_data_sources(self):
        """Load all data sources (CSV/JSON files)"""
        if 'parameters' not in self.scenario_data or 'data_sources' not in self.scenario_data['parameters']:
            return
            
        for source in self.scenario_data['parameters']['data_sources']:
            try:
                source_name = source['name']
                source_type = source['type']
                file_path = source['file']
                
                # Resolve relative path from scenario file location
                scenario_dir = Path(self.scenario_file).parent
                full_path = scenario_dir / file_path
                
                if source_type == 'csv':
                    self.data_sources[source_name] = self._load_csv_data(full_path, source.get('columns', []))
                elif source_type == 'json':
                    self.data_sources[source_name] = self._load_json_data(full_path, source.get('path', '$'))
                    
                self.logger.info(f"Loaded {source_type} data source: {source_name}")
                
            except Exception as e:
                self.logger.error(f"Error loading data source {source.get('name', 'Unknown')}: {str(e)}")
                
    def _load_csv_data(self, file_path: Path, columns: List[str]) -> List[Dict]:
        """Load CSV data and return as list of dictionaries"""
        data = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
            return data
        except Exception as e:
            self.logger.error(f"Error loading CSV file {file_path}: {str(e)}")
            return []
            
    def _load_json_data(self, file_path: Path, json_path: str) -> List[Dict]:
        """Load JSON data and extract using JSONPath-like expression"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Simple JSONPath-like extraction (supports basic patterns)
            if json_path.startswith('$.'):
                path_parts = json_path[2:].split('.')
                current = data
                for part in path_parts:
                    if part.endswith('[*]'):
                        # Array wildcard
                        key = part[:-3]
                        if key in current and isinstance(current[key], list):
                            return current[key]
                    elif part in current:
                        current = current[part]
                    else:
                        return []
                return [current] if not isinstance(current, list) else current
            else:
                return [data]
                
        except Exception as e:
            self.logger.error(f"Error loading JSON file {file_path}: {str(e)}")
            return []
            
    def _generate_data_source_code(self) -> str:
        """Generate code for loading and managing data sources"""
        if not self.data_sources:
            return ""
            
        code = """
    def load_test_data(self):
        \"\"\"Load test data from various sources\"\"\"
        self.test_data = {}
"""
        
        for source_name, data in self.data_sources.items():
            code += f"""
        # Load {source_name} data
        self.test_data['{source_name}'] = {repr(data)}
"""
            
        code += """
        # Randomize data for each user
        for source_name, data in self.test_data.items():
            if data and isinstance(data, list):
                self.test_data[f'{source_name}_current'] = random.choice(data)
"""
        
        return code
        
    def _generate_extraction_code(self, extract_config: Dict) -> str:
        """Generate code for extracting variables from responses"""
        if not extract_config:
            return ""
            
        code = """
        # Extract variables from response
        try:
            response_data = response.json()
"""
        
        for var_name, config in extract_config.items():
            extract_type = config.get('type', 'json_path')
            expression = config.get('expression', '')
            
            if extract_type == 'json_path':
                code += f"""
            # Extract {var_name} using JSONPath: {expression}
            {var_name}_value = self._extract_json_path(response_data, '{expression}')
            if {var_name}_value is not None:
                self.variables['{var_name}'] = str({var_name}_value)
                self.logger.info(f'Extracted {{var_name}} = {{self.variables["{var_name}"]}}')
"""
            elif extract_type == 'regex':
                code += f"""
            # Extract {var_name} using regex: {expression}
            {var_name}_value = self._extract_regex(response.text, r'{expression}')
            if {var_name}_value:
                self.variables['{var_name}'] = {var_name}_value
                self.logger.info(f'Extracted {{var_name}} = {{self.variables["{var_name}"]}}')
"""
            elif extract_type == 'boundary':
                left_boundary = config.get('left_boundary', '')
                right_boundary = config.get('right_boundary', '')
                code += f"""
            # Extract {var_name} using boundaries: '{left_boundary}' -> '{right_boundary}'
            {var_name}_value = self._extract_boundary(response.text, '{left_boundary}', '{right_boundary}')
            if {var_name}_value:
                self.variables['{var_name}'] = {var_name}_value
                self.logger.info(f'Extracted {{var_name}} = {{self.variables["{var_name}"]}}')
"""
        
        code += """
        except Exception as e:
            self.logger.error(f'Error extracting variables: {{str(e)}}')
"""
        
        return code
        
    def _generate_assertion_code(self, assertions: List[Dict]) -> str:
        """Generate code for running assertions"""
        if not assertions:
            return ""
            
        code = """
        # Run assertions
        assertion_failures = []
"""
        
        for assertion in assertions:
            assertion_type = assertion.get('type', '')
            description = assertion.get('description', f'{assertion_type} assertion')
            
            if assertion_type == 'status_code':
                expected = assertion.get('expected', 200)
                code += f"""
        # Status code assertion
        if response.status_code != {expected}:
            assertion_failures.append(f'{description}: expected {expected}, got {{response.status_code}}')
"""
                
            elif assertion_type == 'response_time_ms':
                max_time = assertion.get('max', 5000)
                code += f"""
        # Response time assertion
        if response.elapsed.total_seconds() * 1000 > {max_time}:
            assertion_failures.append(f'{description}: response time {{response.elapsed.total_seconds() * 1000:.0f}}ms exceeds {max_time}ms')
"""
                
            elif assertion_type == 'json_path':
                expression = assertion.get('expression', '')
                expected = assertion.get('expected')
                min_val = assertion.get('min')
                max_val = assertion.get('max')
                
                code += f"""
        # JSONPath assertion: {expression}
        try:
            json_value = self._extract_json_path(response.json(), '{expression}')
            if json_value is not None:
"""
                
                if expected is not None:
                    code += f"""
                if json_value != {repr(expected)}:
                    assertion_failures.append(f'{description}: expected {repr(expected)}, got {{json_value}}')
"""
                if min_val is not None:
                    code += f"""
                if json_value < {min_val}:
                    assertion_failures.append(f'{description}: value {{json_value}} is below minimum {min_val}')
"""
                if max_val is not None:
                    code += f"""
                if json_value > {max_val}:
                    assertion_failures.append(f'{description}: value {{json_value}} exceeds maximum {max_val}')
"""
                code += """
            else:
                assertion_failures.append(f'{description}: JSONPath expression returned None')
        except Exception as e:
            assertion_failures.append(f'{description}: error evaluating JSONPath - {{str(e)}}')
"""
                
            elif assertion_type == 'body_contains_text':
                text = assertion.get('text', '')
                code += f"""
        # Body contains text assertion
        if '{text}' not in response.text:
            assertion_failures.append(f'{description}: response does not contain text "{text}"')
"""
                
            elif assertion_type == 'regex':
                pattern = assertion.get('pattern', '')
                code += f"""
        # Regex assertion
        if not re.search(r'{pattern}', response.text):
            assertion_failures.append(f'{description}: response does not match pattern "{pattern}"')
"""
        
        code += """
        # Report assertion failures
        if assertion_failures:
            failure_message = '; '.join(assertion_failures)
            response.failure(f'Assertions failed: {{failure_message}}')
            self.logger.error(f'Assertions failed: {{failure_message}}')
        else:
            self.logger.info('All assertions passed')
"""
        
        return code
        
    def _generate_helper_methods(self) -> str:
        """Generate helper methods for extraction and utilities"""
        return """
    def _extract_json_path(self, data, expression):
        \"\"\"Extract value using JSONPath-like expression\"\"\"
        try:
            if not expression.startswith('$'):
                return None
                
            parts = expression[2:].split('.')
            current = data
            
            for part in parts:
                if isinstance(current, dict):
                    current = current.get(part)
                elif isinstance(current, list) and part.isdigit():
                    index = int(part)
                    if 0 <= index < len(current):
                        current = current[index]
                    else:
                        return None
                else:
                    return None
                    
            return current
        except Exception as e:
            self.logger.error(f'Error extracting JSONPath {expression}: {{str(e)}}')
            return None
            
    def _extract_regex(self, text, pattern):
        \"\"\"Extract value using regex pattern\"\"\"
        try:
            match = re.search(pattern, text)
            return match.group(1) if match and match.groups() else match.group(0) if match else None
        except Exception as e:
            self.logger.error(f'Error extracting regex {pattern}: {{str(e)}}')
            return None
            
    def _extract_boundary(self, text, left_boundary, right_boundary):
        \"\"\"Extract value between left and right boundaries\"\"\"
        try:
            start = text.find(left_boundary)
            if start == -1:
                return None
            start += len(left_boundary)
            
            end = text.find(right_boundary, start)
            if end == -1:
                return None
                
            return text[start:end].strip()
        except Exception as e:
            self.logger.error(f'Error extracting boundary: {{str(e)}}')
            return None
            
    def _get_test_data_value(self, source_name, field_name):
        \"\"\"Get a value from test data sources\"\"\"
        try:
            current_data = self.test_data.get(f'{source_name}_current', {})
            if isinstance(current_data, dict):
                return current_data.get(field_name)
            return None
        except Exception as e:
            self.logger.error(f'Error getting test data value: {{str(e)}}')
            return None
"""
        
    def generate_script(self):
        """Generate the complete Locust test script"""
        self.load_scenario()
        self.load_data_sources()
        
        scenario_name = self.scenario_data.get('name', 'TestScenario')
        class_name = self._generate_class_name(scenario_name)
        base_url = self.scenario_data.get('base_url', 'http://localhost')
        min_wait = self.scenario_data.get('min_wait', 1000) / 1000.0
        max_wait = self.scenario_data.get('max_wait', 5000) / 1000.0
        
        script_content = f'''from locust import HttpUser, task, between
import json
import time
import logging
import random
import re

class {class_name}(HttpUser):
    wait_time = between({min_wait}, {max_wait})
    
    def on_start(self):
        self.variables = {{}}
        self.logger = logging.getLogger(__name__)
        self.load_test_data()
{self._generate_data_source_code()}
{self._generate_helper_methods()}
    
    def replace_variables(self, text):
        \"\"\"Replace variables in text with actual values\"\"\"
        if not text:
            return text
        try:
            # Replace test data variables
            for source_name, data in self.test_data.items():
                if source_name.endswith('_current') and isinstance(data, dict):
                    for field_name, value in data.items():
                        placeholder = f'{{{{{{field_name}}}}}}'
                        if placeholder in text:
                            text = text.replace(placeholder, str(value))
                            
            # Replace extracted variables
            for var_name, value in self.variables.items():
                placeholder = f'{{{{{{var_name}}}}}}'
                if placeholder in text:
                    text = text.replace(placeholder, str(value))
                    
            return text
        except Exception as e:
            self.logger.error(f'Error replacing variables: {{str(e)}}')
            return text
    
    @task
    def run_scenario(self):
        \"\"\"Execute the complete test scenario\"\"\"
'''
        
        # Generate code for each step
        for step in self.scenario_data.get('steps', []):
            step_id = step.get('id', 'unknown')
            step_name = step.get('name', 'Unknown Step')
            method = step.get('method', 'GET')
            url = step.get('url', '/')
            headers = step.get('headers', {})
            params = step.get('params', {})
            body = step.get('body')
            extract = step.get('extract', {})
            assertions = step.get('assertions', [])
            
            script_content += f'''
        # Step: {step_name}
        try:
            url = self.replace_variables('{url}')
            headers = {{}}
'''
            
            # Add headers
            for header_name, header_value in headers.items():
                script_content += f"            headers['{header_name}'] = self.replace_variables('{header_value}')\n"
            
            script_content += f"""
            headers['Accept'] = 'application/json'
            
            # Prepare request parameters
"""
            
            # Add query parameters
            if params:
                script_content += "            params = {}\n"
                for param_name, param_value in params.items():
                    script_content += f"            params['{param_name}'] = self.replace_variables('{param_value}')\n"
            else:
                script_content += "            params = {}\n"
            
            # Add request body
            if body:
                script_content += f"            body = {json.dumps(body, indent=12)}\n"
                script_content += "            body = self.replace_variables(json.dumps(body))\n"
                script_content += "            body = json.loads(body)\n"
            else:
                script_content += "            body = None\n"
            
            # Make the request
            script_content += f"""
            with self.client.{method.lower()}(
                url,
                headers=headers,
                params=params,
                json=body,
                catch_response=True) as response:
"""
            
            # Add extraction code
            script_content += self._generate_extraction_code(extract)
            
            # Add assertion code
            script_content += self._generate_assertion_code(assertions)
            
            script_content += """
        except Exception as e:
            self.logger.error(f'Error in API call: {str(e)}')
"""
        
        script_content += "\n"
        
        # Write the script to file
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(script_content)
            self.logger.info(f"Generated enhanced script: {self.output_file}")
        except Exception as e:
            self.logger.error(f"Error writing script file: {str(e)}")
            raise
            
    def _generate_class_name(self, scenario_name: str) -> str:
        """Generate a valid Python class name from scenario name"""
        # Remove special characters and convert to CamelCase
        class_name = re.sub(r'[^a-zA-Z0-9\s]', '', scenario_name)
        class_name = ''.join(word.capitalize() for word in class_name.split())
        return f"{class_name}User" 