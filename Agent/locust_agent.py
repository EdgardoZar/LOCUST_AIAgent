#!/usr/bin/env python3
"""
Locust Performance Testing Agent
AI-powered agent for generating and executing Locust performance test scripts
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
class AgentRequest:
    """Represents a natural language request for script generation"""
    description: str
    target_host: str
    load_profile: str
    assertions: List[str]
    data_sources: List[str]
    output_format: str = "python"
    
class LocustAgent:
    """
    AI Agent for generating Locust performance test scripts from natural language
    """
    
    def __init__(self, config_file: str = "Agent/script_generator_config.yaml"):
        """Initialize the agent with configuration"""
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
    
    def parse_natural_language(self, request: str) -> AgentRequest:
        """
        Parse natural language request into structured format
        """
        self.logger.info(f"Parsing natural language request: {request}")
        
        # Use OpenAI to parse the request
        prompt = f"""
        Parse the following natural language request for a Locust performance test into structured format.
        
        Request: {request}
        
        Extract the following information:
        1. Target host/API endpoint
        2. Load profile (users, duration, spawn rate)
        3. Specific endpoints to test
        4. Assertions to include
        5. Data sources needed
        
        Return as JSON with these fields:
        - target_host: string
        - load_profile: string (e.g., "20 users for 5 minutes")
        - endpoints: list of strings
        - assertions: list of strings
        - data_sources: list of strings
        - description: string
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.config['agent']['openai']['model'],
                messages=[
                    {"role": "system", "content": "You are a performance testing expert. Parse requests accurately."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config['agent']['openai']['temperature'],
                max_tokens=self.config['agent']['openai']['max_tokens']
            )
            
            # Parse the response
            content = response.choices[0].message.content
            parsed_data = json.loads(content)
            
            return AgentRequest(
                description=parsed_data.get('description', request),
                target_host=parsed_data.get('target_host', self.config['defaults']['base_url']),
                load_profile=parsed_data.get('load_profile', '10 users for 5 minutes'),
                assertions=parsed_data.get('assertions', []),
                data_sources=parsed_data.get('data_sources', [])
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse natural language: {e}")
            # Fallback to basic parsing
            return self._fallback_parse(request)
    
    def _fallback_parse(self, request: str) -> AgentRequest:
        """Fallback parsing using regex patterns"""
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
        
        # Extract endpoints
        endpoints = re.findall(r'/(?:api/)?[a-zA-Z0-9/_-]+', request)
        
        return AgentRequest(
            description=request,
            target_host=target_host,
            load_profile=load_profile,
            assertions=["status_code: 200"],
            data_sources=[]
        )
    
    def generate_script(self, request: AgentRequest) -> str:
        """
        Generate Locust script from parsed request
        """
        self.logger.info(f"Generating script for: {request.description}")
        
        # Create scenario from request
        scenario = self._create_scenario_from_request(request)
        
        # Generate script using enhanced generator
        output_file = self._generate_filename(request.description)
        
        try:
            generator = EnhancedScriptGenerator(
                scenario_file=self._save_scenario(scenario),
                output_file=output_file
            )
            generator.generate_script()
            
            self.logger.info(f"Script generated successfully: {output_file}")
            return output_file
            
        except Exception as e:
            self.logger.error(f"Failed to generate script: {e}")
            raise
    
    def _create_scenario_from_request(self, request: AgentRequest) -> Dict[str, Any]:
        """Create scenario JSON from agent request"""
        
        # Parse load profile
        load_config = self._parse_load_profile(request.load_profile)
        
        # Create basic scenario
        scenario = {
            "name": self._sanitize_name(request.description),
            "description": request.description,
            "base_url": request.target_host,
            "min_wait": self.config['defaults']['min_wait'],
            "max_wait": self.config['defaults']['max_wait'],
            "steps": []
        }
        
        # Add data sources if specified
        if request.data_sources:
            scenario["parameters"] = {
                "data_sources": []
            }
            for source_name in request.data_sources:
                if source_name in self.data_sources['data_sources']:
                    # Find the data source configuration
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
        
        # Add steps based on endpoints or create default steps
        if hasattr(request, 'endpoints') and request.endpoints:
            for i, endpoint in enumerate(request.endpoints):
                scenario["steps"].append({
                    "id": i + 1,
                    "name": f"Test {endpoint}",
                    "method": "GET",
                    "url": endpoint,
                    "headers": {"Content-Type": "application/json"},
                    "assertions": self._create_assertions(request.assertions)
                })
        else:
            # Create default health check step
            scenario["steps"].append({
                "id": 1,
                "name": "Health Check",
                "method": "GET",
                "url": "/",
                "headers": {"Content-Type": "application/json"},
                "assertions": self._create_assertions(request.assertions)
            })
        
        return scenario
    
    def _parse_load_profile(self, load_profile: str) -> Dict[str, Any]:
        """Parse load profile string into configuration"""
        # Default values
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
    
    def _create_assertions(self, assertion_strings: List[str]) -> List[Dict]:
        """Create assertion objects from assertion strings"""
        assertions = []
        
        for assertion_str in assertion_strings:
            if "status_code" in assertion_str:
                code_match = re.search(r'(\d+)', assertion_str)
                if code_match:
                    assertions.append({
                        "type": "status_code",
                        "expected": int(code_match.group(1))
                    })
            elif "response_time" in assertion_str:
                time_match = re.search(r'(\d+)', assertion_str)
                if time_match:
                    assertions.append({
                        "type": "response_time",
                        "max_time": int(time_match.group(1))
                    })
            elif "json_path" in assertion_str:
                # Parse JSONPath assertion
                path_match = re.search(r'\$[^\s]+', assertion_str)
                if path_match:
                    assertions.append({
                        "type": "json_path",
                        "path": path_match.group(0),
                        "expected": "exists"
                    })
        
        # Add default assertions if none specified
        if not assertions:
            assertions.append({
                "type": "status_code",
                "expected": 200
            })
        
        return assertions
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize name for use as filename"""
        return re.sub(r'[^a-zA-Z0-9\s_-]', '', name).strip().replace(' ', '_')
    
    def _generate_filename(self, description: str) -> str:
        """Generate filename for the script"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = self._sanitize_name(description)
        return f"generated_scripts/{safe_name}_{timestamp}.py"
    
    def _save_scenario(self, scenario: Dict[str, Any]) -> str:
        """Save scenario to temporary file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"temp_scenario_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(scenario, f, indent=2)
        
        return filename
    
    def execute_test(self, script_path: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the generated test script
        """
        self.logger.info(f"Executing test script: {script_path}")
        
        # Create test configuration
        test_config = TestConfig(
            scenario_name=config.get('name', 'Generated Test'),
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
    
    def process_request(self, natural_language_request: str) -> Dict[str, Any]:
        """
        Main method to process a natural language request
        """
        try:
            # Parse the request
            parsed_request = self.parse_natural_language(natural_language_request)
            
            # Generate script
            script_path = self.generate_script(parsed_request)
            
            # Execute test (optional)
            test_results = None
            if self.config.get('auto_execute', False):
                test_results = self.execute_test(script_path, {
                    'name': parsed_request.description,
                    'host': parsed_request.target_host
                })
            
            return {
                'success': True,
                'script_path': script_path,
                'parsed_request': parsed_request,
                'test_results': test_results
            }
            
        except Exception as e:
            self.logger.error(f"Failed to process request: {e}")
            return {
                'success': False,
                'error': str(e)
            }

def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python locust_agent.py 'your natural language request'")
        print("Example: python locust_agent.py 'Test the Rick and Morty API with 20 users for 5 minutes'")
        sys.exit(1)
    
    request = ' '.join(sys.argv[1:])
    
    # Initialize agent
    agent = LocustAgent()
    
    # Process request
    result = agent.process_request(request)
    
    if result['success']:
        print(f"✅ Script generated successfully: {result['script_path']}")
        if result['test_results']:
            print(f"📊 Test executed with metrics: {result['test_results']['metrics']}")
    else:
        print(f"❌ Failed to process request: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main() 