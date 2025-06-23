from locust import HttpUser, task, between
import json
import time
import logging

class RickAndMortyApiTest5User(HttpUser):
    wait_time = between(1.0, 5.0)

    def on_start(self):
        self.variables = {}
        self.logger = logging.getLogger(__name__)

    def extract_variables(self, response, extract_config):
        if not extract_config:
            return
        try:
            data = response.json()
            for var_name, json_path in extract_config.items():
                try:
                    parts = json_path.split('.')
                    value = data
                    for part in parts:
                        if isinstance(value, dict):
                            value = value.get(part)
                        else:
                            value = None
                            break
                    if value is not None:
                        self.variables[var_name] = str(value)
                        self.logger.info(f'Extracted {var_name} = {value}')
                except Exception as e:
                    self.logger.error(f'Error extracting {var_name}: {str(e)}')
        except Exception as e:
            self.logger.error(f'Error parsing response JSON: {str(e)}')

    def replace_variables(self, text):
        if not text:
            return text
        try:
            for var_name, value in self.variables.items():
                text = text.replace(f'{{{{{var_name}}}}}', str(value))
            return text
        except Exception as e:
            self.logger.error(f'Error replacing variables: {str(e)}')
            return text

    @task
    def run_scenario(self):
        # Step: Get Characters Page 1
        try:
            url = self.replace_variables('/api/character?page=1')
            headers = {
                'Content-Type': self.replace_variables('application/json'),
                'Accept': self.replace_variables('application/json'),
            }
            with self.client.get(
                url,
                headers=headers,
                catch_response=True) as response:
                self.extract_variables(response, {
                    'total_pages': 'info.pages',
                    'total_count': 'info.count',
                })
                # Run assertions
                if response.status_code != 200:
                    response.failure('Status code assertion failed')
        except Exception as e:
            self.logger.error(f'Error in API call: {str(e)}')

        # Step: Wait
        time.sleep(1)

        # Step: Get Specific Character
        try:
            url = self.replace_variables('/api/character/1')
            headers = {
                'Content-Type': self.replace_variables('application/json'),
                'Accept': self.replace_variables('application/json'),
            }
            with self.client.get(
                url,
                headers=headers,
                catch_response=True) as response:
                self.extract_variables(response, {
                    'character_name': 'name',
                    'character_status': 'status',
                })
                # Run assertions
                if response.status_code != 200:
                    response.failure('Status code assertion failed')
        except Exception as e:
            self.logger.error(f'Error in API call: {str(e)}')

        # Step: Wait
        time.sleep(1)

        # Step: Search Characters
        try:
            url = self.replace_variables('/api/character?name=rick')
            headers = {
                'Content-Type': self.replace_variables('application/json'),
                'Accept': self.replace_variables('application/json'),
            }
            with self.client.get(
                url,
                headers=headers,
                catch_response=True) as response:
                self.extract_variables(response, {
                    'search_results': 'results',
                })
                # Run assertions
                if response.status_code != 200:
                    response.failure('Status code assertion failed')
        except Exception as e:
            self.logger.error(f'Error in API call: {str(e)}')
