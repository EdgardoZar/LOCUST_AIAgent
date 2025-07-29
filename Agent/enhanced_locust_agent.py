#!/usr/bin/env python3
"""
Enhanced Locust Performance Testing Agent
Supports multi-API sequences with correlation and transaction naming
"""

import os
import sys
import yaml
import csv
import json
import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import openai
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.enhanced_script_generator import EnhancedScriptGenerator
from core.test_agent import LocustTestAgent, TestConfig

@dataclass
class APIStep:
    """Represents a single API step in a multi-API sequence"""
    name: str
    method: str
    url: str
    headers: Dict[str, str]
    body: Optional[Dict] = None
    params: Optional[Dict] = None
    extract: Optional[Dict] = None
    assertions: Optional[List[Dict]] = None
    wait_time: Optional[float] = None
    depends_on: Optional[str] = None  # Name of step this depends on

@dataclass
class EnhancedAgentRequest:
    """Enhanced request with multi-API sequence support"""
    description: str
    target_host: str
    load_profile: str
    transaction_name: str
    api_sequence: List[APIStep]
    assertions: List[str]
    data_sources: List[str]
    correlation_rules: Dict[str, str]  # Maps variable names to usage in subsequent steps

class EnhancedLocustAgent:
    """
    Enhanced AI Agent for generating Locust performance test scripts with multi-API support
    """
    
    def __init__(self, config_file: str = "Agent/script_generator_config.yaml"):
        """Initialize the enhanced agent with configuration"""
        self.config = self._load_config(config_file)
        self.data_sources = self._load_data_sources()
        self.openai_client = self._setup_openai()
        self.logger = self._setup_logging()
        
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load YAML configuration file"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise Exception(f"Failed to load configuration: {e}")
    
    def _load_data_sources(self) -> Dict[str, List[Dict]]:
        """Load all data source CSV files"""
        data_sources = {}
        
        for source_name, file_path in self.config['data_sources'].items():
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        data_sources[source_name] = list(reader)
                else:
                    print(f"Warning: Data source file not found: {file_path}")
                    data_sources[source_name] = []
            except Exception as e:
                print(f"Warning: Failed to load data source {source_name}: {e}")
                data_sources[source_name] = []
        
        return data_sources
    
    def _setup_openai(self):
        """Setup OpenAI client"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise Exception("OPENAI_API_KEY environment variable not set")
        
        return openai.OpenAI(api_key=api_key)
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def parse_natural_language_sequence(self, request: str) -> EnhancedAgentRequest:
        """
        Parse natural language request into structured multi-API sequence
        """
        self.logger.info(f"Parsing enhanced natural language request: {request}")
        
        # Use OpenAI to parse the complex request
        prompt = f"""
        Parse the following natural language request for a multi-API Locust performance test into structured format.
        
        Request: {request}
        
        Extract the following information:
        1. Target host/API endpoint
        2. Load profile (users, duration, spawn rate)
        3. Transaction name for the test
        4. Sequence of API calls with their dependencies
        5. Variable extraction and correlation rules
        6. Assertions for each step
        7. Data sources needed
        
        Return as JSON with these fields:
        - target_host: string
        - load_profile: string (e.g., "20 users for 5 minutes")
        - transaction_name: string (e.g., "HomePage", "GetCharacters")
        - api_sequence: array of objects with:
          - name: string (step name)
          - method: string (GET, POST, etc.)
          - url: string
          - headers: object
          - body: object (optional)
          - params: object (optional)
          - extract: object (variables to extract)
          - assertions: array of objects
          - wait_time: number (optional)
          - depends_on: string (name of previous step, optional)
        - correlation_rules: object (maps variable names to usage)
        - assertions: array of strings
        - data_sources: array of strings
        - description: string
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.config['agent']['openai']['model'],
                messages=[
                    {"role": "system", "content": "You are an expert performance testing engineer. Parse complex multi-API requests accurately with correlation rules."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config['agent']['openai']['temperature'],
                max_tokens=self.config['agent']['openai']['max_tokens']
            )
            
            # Parse the response
            content = response.choices[0].message.content
            parsed_data = json.loads(content)
            
            # Convert API sequence to APIStep objects
            api_sequence = []
            for step_data in parsed_data.get('api_sequence', []):
                api_sequence.append(APIStep(
                    name=step_data.get('name', 'Unknown'),
                    method=step_data.get('method', 'GET'),
                    url=step_data.get('url', '/'),
                    headers=step_data.get('headers', {}),
                    body=step_data.get('body'),
                    params=step_data.get('params'),
                    extract=step_data.get('extract'),
                    assertions=step_data.get('assertions', []),
                    wait_time=step_data.get('wait_time'),
                    depends_on=step_data.get('depends_on')
                ))
            
            return EnhancedAgentRequest(
                description=parsed_data.get('description', request),
                target_host=parsed_data.get('target_host', self.config['defaults']['base_url']),
                load_profile=parsed_data.get('load_profile', '10 users for 5 minutes'),
                transaction_name=parsed_data.get('transaction_name', 'MultiAPITest'),
                api_sequence=api_sequence,
                assertions=parsed_data.get('assertions', []),
                data_sources=parsed_data.get('data_sources', []),
                correlation_rules=parsed_data.get('correlation_rules', {})
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse natural language: {e}")
            # Fallback to basic parsing
            return self._fallback_parse_enhanced(request)
    
    def _fallback_parse_enhanced(self, request: str) -> EnhancedAgentRequest:
        """Fallback parsing for enhanced requests"""
        # Extract host
        host_match = re.search(r'https?://[^\s]+', request)
        target_host = host_match.group(0) if host_match else self.config['defaults']['base_url']
        
        # Extract load profile
        load_match = re.search(r'(\d+)\s+users?\s+(?:for\s+)?(\d+[mh]?)', request, re.IGNORECASE)
        if load_match:
            users = load_match.group(1)
            duration = load_match.group(2)
            load_profile = f"{users} users for {duration}"
        else:
            load_profile = "10 users for 5 minutes"
        
        # Extract transaction name
        transaction_match = re.search(r'(?:transaction|test)\s+(?:named\s+)?([A-Za-z0-9_]+)', request, re.IGNORECASE)
        transaction_name = transaction_match.group(1) if transaction_match else "MultiAPITest"
        
        # Create basic API sequence
        api_sequence = [
            APIStep(
                name="HealthCheck",
                method="GET",
                url="/",
                headers={"Content-Type": "application/json"},
                assertions=[{"type": "status_code", "expected": 200}]
            )
        ]
        
        return EnhancedAgentRequest(
            description=request,
            target_host=target_host,
            load_profile=load_profile,
            transaction_name=transaction_name,
            api_sequence=api_sequence,
            assertions=["status_code: 200"],
            data_sources=[],
            correlation_rules={}
        )
    
    def generate_enhanced_script(self, request: EnhancedAgentRequest) -> str:
        """
        Generate enhanced Locust script with multi-API sequence support
        """
        self.logger.info(f"Generating enhanced script for: {request.description}")
        
        # Create enhanced scenario from request
        scenario = self._create_enhanced_scenario_from_request(request)
        
        # Generate script using enhanced generator
        output_file = self._generate_enhanced_filename(request.transaction_name)
        
        try:
            generator = EnhancedScriptGenerator(
                scenario_file=self._save_scenario(scenario),
                output_file=output_file
            )
            generator.generate_script()
            
            self.logger.info(f"Enhanced script generated successfully: {output_file}")
            return output_file
            
        except Exception as e:
            self.logger.error(f"Failed to generate enhanced script: {e}")
            raise
    
    def _create_enhanced_scenario_from_request(self, request: EnhancedAgentRequest) -> Dict[str, Any]:
        """Create enhanced scenario JSON from agent request with multi-API support"""
        
        # Parse load profile
        load_config = self._parse_load_profile(request.load_profile)
        
        # Create enhanced scenario
        scenario = {
            "name": self._sanitize_name(request.transaction_name),
            "description": request.description,
            "base_url": request.target_host,
            "min_wait": self.config['defaults']['min_wait'],
            "max_wait": self.config['defaults']['max_wait'],
            "transaction_name": request.transaction_name,
            "steps": []
        }
        
        # Add data sources if specified
        if request.data_sources:
            scenario["parameters"] = {
                "data_sources": []
            }
            for source_name in request.data_sources:
                if source_name in self.data_sources['data_sources']:
                    for source in self.data_sources['data_sources']:
                        if source['source_name'] == source_name:
                            scenario["parameters"]["data_sources"].append({
                                "name": source_name,
                                "type": source['type'],
                                "file": source['file_path'],
                                "columns": source['columns'].split(',') if source['columns'] else [],
                                "json_path": source['json_path'] if source['json_path'] else None
                            })
                            break
        
        # Add steps from API sequence
        for i, api_step in enumerate(request.api_sequence):
            step = {
                "id": i + 1,
                "name": api_step.name,
                "method": api_step.method,
                "url": api_step.url,
                "headers": api_step.headers,
                "params": api_step.params or {},
                "body": api_step.body,
                "extract": api_step.extract or {},
                "assertions": self._create_assertions_from_step(api_step.assertions),
                "wait_time": api_step.wait_time
            }
            
            # Add dependency information
            if api_step.depends_on:
                step["depends_on"] = api_step.depends_on
            
            scenario["steps"].append(step)
        
        # Add correlation rules
        if request.correlation_rules:
            scenario["correlation_rules"] = request.correlation_rules
        
        return scenario
    
    def _create_assertions_from_step(self, step_assertions: List[Dict]) -> List[Dict]:
        """Create assertion objects from step assertions"""
        assertions = []
        
        for assertion in step_assertions:
            if isinstance(assertion, dict):
                assertions.append(assertion)
            elif isinstance(assertion, str):
                # Parse string assertions
                if "status_code" in assertion:
                    code_match = re.search(r'(\d+)', assertion)
                    if code_match:
                        assertions.append({
                            "type": "status_code",
                            "expected": int(code_match.group(1))
                        })
                elif "response_time" in assertion:
                    time_match = re.search(r'(\d+)', assertion)
                    if time_match:
                        assertions.append({
                            "type": "response_time",
                            "max_time": int(time_match.group(1))
                        })
        
        # Add default assertions if none specified
        if not assertions:
            assertions.append({
                "type": "status_code",
                "expected": 200
            })
        
        return assertions
    
    def _parse_load_profile(self, load_profile: str) -> Dict[str, Any]:
        """Parse load profile string into configuration"""
        config = {
            "users": 10,
            "spawn_rate": 1,
            "run_time": "5m"
        }
        
        # Extract users
        users_match = re.search(r'(\d+)\s+users?', load_profile, re.IGNORECASE)
        if users_match:
            config["users"] = int(users_match.group(1))
        
        # Extract duration
        duration_match = re.search(r'(\d+)\s*([mh])', load_profile, re.IGNORECASE)
        if duration_match:
            value = int(duration_match.group(1))
            unit = duration_match.group(2).lower()
            if unit == 'h':
                config["run_time"] = f"{value}h"
            else:
                config["run_time"] = f"{value}m"
        
        return config
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize name for use as filename"""
        return re.sub(r'[^a-zA-Z0-9\s_-]', '', name).strip().replace(' ', '_')
    
    def _generate_enhanced_filename(self, transaction_name: str) -> str:
        """Generate filename for the enhanced script"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = self._sanitize_name(transaction_name)
        return f"generated_scripts/{safe_name}_{timestamp}.py"
    
    def _save_scenario(self, scenario: Dict[str, Any]) -> str:
        """Save scenario to temporary file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"temp_enhanced_scenario_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(scenario, f, indent=2)
        
        return filename
    
    def process_enhanced_request(self, natural_language_request: str) -> Dict[str, Any]:
        """
        Main method to process an enhanced natural language request
        """
        try:
            # Parse the enhanced request
            parsed_request = self.parse_natural_language_sequence(natural_language_request)
            
            # Generate enhanced script
            script_path = self.generate_enhanced_script(parsed_request)
            
            # Execute test (optional)
            test_results = None
            if self.config.get('auto_execute', False):
                test_results = self.execute_enhanced_test(script_path, {
                    'name': parsed_request.transaction_name,
                    'host': parsed_request.target_host
                })
            
            return {
                'success': True,
                'script_path': script_path,
                'parsed_request': parsed_request,
                'test_results': test_results
            }
            
        except Exception as e:
            self.logger.error(f"Failed to process enhanced request: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def execute_enhanced_test(self, script_path: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the generated enhanced test script
        """
        self.logger.info(f"Executing enhanced test script: {script_path}")
        
        # Create test configuration
        test_config = TestConfig(
            scenario_name=config.get('name', 'Enhanced Test'),
            host=config.get('host', self.config['defaults']['base_url']),
            users=config.get('users', 10),
            spawn_rate=config.get('spawn_rate', 1),
            run_time=config.get('run_time', '5m'),
            output_dir='generated_reports'
        )
        
        # Execute test
        test_agent = LocustTestAgent()
        result = test_agent.execute_test(script_path, test_config)
        
        return {
            'success': result.success,
            'script_path': script_path,
            'html_report': result.html_report_path,
            'csv_report': result.csv_report_path,
            'metrics': {
                'total_requests': result.total_requests,
                'failed_requests': result.failed_requests,
                'avg_response_time': result.avg_response_time,
                'requests_per_sec': result.requests_per_sec
            }
        }

def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python enhanced_locust_agent.py 'your enhanced natural language request'")
        print("Example: python enhanced_locust_agent.py 'Create a HomePage transaction that calls /api/login, then /api/user/profile using the token from login, then /api/logout'")
        sys.exit(1)
    
    request = ' '.join(sys.argv[1:])
    
    # Initialize enhanced agent
    agent = EnhancedLocustAgent()
    
    # Process enhanced request
    result = agent.process_enhanced_request(request)
    
    if result['success']:
        print(f"✅ Enhanced script generated successfully: {result['script_path']}")
        print(f"📊 Transaction name: {result['parsed_request'].transaction_name}")
        print(f"🔗 API sequence: {len(result['parsed_request'].api_sequence)} steps")
        if result['test_results']:
            print(f"📊 Test executed with metrics: {result['test_results']['metrics']}")
    else:
        print(f"❌ Failed to process enhanced request: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main() 