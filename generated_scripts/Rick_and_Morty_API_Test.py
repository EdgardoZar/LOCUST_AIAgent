from locust import HttpUser, task, between
import json
import time
import logging
import random
import re

class RickAndMortyApiTestUser(HttpUser):
    wait_time = between(1.0, 3.0)
    
    def on_start(self):
        self.variables = {}
        self.logger = logging.getLogger(__name__)
        self.load_test_data()


    def _extract_json_path(self, data, expression):
        """Extract value using JSONPath-like expression"""
        try:
            if not expression.startswith('$'):
                return None
                
            parts = expression[2:].split('.')
            current = data
            
            for part in parts:
                if isinstance(current, dict):
                    current = current.get(part)
                elif isinstance(current, list):
                    if part == '*':
                        # Wildcard - return the entire array
                        return current
                    elif part.isdigit():
                        index = int(part)
                        if 0 <= index < len(current):
                            current = current[index]
                        else:
                            return None
                    else:
                        return None
                else:
                    return None
                    
            return current
        except Exception as e:
            self.logger.error(f'Error extracting JSONPath {expression}: {{str(e)}}')
            return None
            
    def _extract_regex(self, text, pattern):
        """Extract value using regex pattern"""
        try:
            match = re.search(pattern, text)
            return match.group(1) if match and match.groups() else match.group(0) if match else None
        except Exception as e:
            self.logger.error(f'Error extracting regex {pattern}: {{str(e)}}')
            return None
            
    def _extract_boundary(self, text, left_boundary, right_boundary):
        """Extract value between left and right boundaries"""
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
        """Get a value from test data sources"""
        try:
            current_data = self.test_data.get(f'{source_name}_current', {})
            if isinstance(current_data, dict):
                return current_data.get(field_name)
            return None
        except Exception as e:
            self.logger.error(f'Error getting test data value: {{str(e)}}')
            return None
            
    def _replace_dynamic_functions(self, text):
        """Replace dynamic function calls in text"""
        try:
            # Handle random(min, max) function
            random_pattern = r'\{\{random\(([^,]+),\s*([^)]+)\)\}\}'
            def replace_random(match):
                min_val = match.group(1).strip()
                max_val = match.group(2).strip()
                # Try to resolve variables in min/max values
                min_val = self._resolve_single_value(min_val)
                max_val = self._resolve_single_value(max_val)
                try:
                    min_int = int(min_val)
                    max_int = int(max_val)
                    return str(random.randint(min_int, max_int))
                except (ValueError, TypeError):
                    return '1'  # fallback
            text = re.sub(random_pattern, replace_random, text)
            
            # Handle random_from_array(array_var) function
            random_array_pattern = r'\{\{random_from_array\(([^)]+)\)\}\}'
            def replace_random_array(match):
                array_var = match.group(1).strip()
                if array_var in self.variables:
                    try:
                        # Try to parse as JSON array first
                        array_data = json.loads(self.variables[array_var])
                        if isinstance(array_data, list) and array_data:
                            return str(random.choice(array_data))
                    except (json.JSONDecodeError, TypeError):
                        # If not JSON, try to split by comma (fallback)
                        try:
                            array_str = self.variables[array_var]
                            if ',' in array_str:
                                array_data = [item.strip() for item in array_str.split(',')]
                                if array_data:
                                    return str(random.choice(array_data))
                        except:
                            pass
                return '1'  # fallback
            text = re.sub(random_array_pattern, replace_random_array, text)
            
            # Handle random_subset_from_array(array_var, n) function
            random_subset_pattern = r'\{\{random_subset_from_array\(([^,]+),\s*([^)]+)\)\}\}'
            def replace_random_subset(match):
                array_var = match.group(1).strip()
                n_val = match.group(2).strip()
                n_val = self._resolve_single_value(n_val)
                try:
                    n = int(n_val)
                except (ValueError, TypeError):
                    n = 1
                
                if array_var in self.variables:
                    try:
                        array_data = json.loads(self.variables[array_var])
                        if isinstance(array_data, list) and array_data:
                            subset = random.sample(array_data, min(n, len(array_data)))
                            return json.dumps(subset)
                    except (json.JSONDecodeError, TypeError):
                        pass
                return '[]'  # fallback
            text = re.sub(random_subset_pattern, replace_random_subset, text)
            
            # Handle random_index_from_array(array_var) function
            random_index_pattern = r'\{\{random_index_from_array\(([^)]+)\)\}\}'
            def replace_random_index(match):
                array_var = match.group(1).strip()
                if array_var in self.variables:
                    try:
                        array_data = json.loads(self.variables[array_var])
                        if isinstance(array_data, list) and array_data:
                            return str(random.randint(0, len(array_data) - 1))
                    except (json.JSONDecodeError, TypeError):
                        pass
                return '0'  # fallback
            text = re.sub(random_index_pattern, replace_random_index, text)
            
            return text
        except Exception as e:
            self.logger.error(f'Error replacing dynamic functions: {{str(e)}}')
            return text
    
    def _resolve_single_value(self, value):
        """Resolve a single value, handling variable references"""
        if value in self.variables:
            return self.variables[value]
        return value
        
    def _apply_transform(self, value, transform_name):
        """Apply custom transformation to extracted value"""
        try:
            if transform_name == 'extract_page_number':
                return self._extract_page_number(value)
            # Add more transformations as needed
            return value
        except Exception as e:
            self.logger.error(f'Error applying transform {transform_name}: {{str(e)}}')
            return value
            
    def _extract_page_number(self, url):
        """Extract page number from next URL"""
        if url and 'page=' in url:
            match = re.search(r'page=(\d+)', url)
            if match:
                return int(match.group(1))
        return 1

    
    def replace_variables(self, text):
        """Replace variables in text with actual values"""
        if not text:
            return text
        try:
            # Handle dynamic functions first
            text = self._replace_dynamic_functions(text)
            
            # Replace test data variables
            for source_name, data in self.test_data.items():
                if source_name.endswith('_current') and isinstance(data, dict):
                    for field_name, value in data.items():
                        placeholder = f'{{{field_name}}}'
                        if placeholder in text:
                            text = text.replace(placeholder, str(value))
                            
            # Replace extracted variables
            for var_name, value in self.variables.items():
                placeholder = f'{{{var_name}}}'
                if placeholder in text:
                    text = text.replace(placeholder, str(value))
                    
            return text
        except Exception as e:
            self.logger.error(f'Error replacing variables: {str(e)}')
            return text
    
    @task
    def run_scenario(self):
        """Execute the complete test scenario"""

        # Step: Get Characters List - Extract Total Pages
        try:
            url = self.replace_variables('/api/character')
            headers = {}
            headers['Content-Type'] = self.replace_variables('application/json')

            headers['Accept'] = 'application/json'
            
            # Prepare request parameters
            params = {}
            body = None

            with self.client.get(
                url,
                headers=headers,
                params=params,
                json=body,
                catch_response=True) as response:

        # Extract variables from response
        try:
            response_data = response.json()

            # Extract total_pages using JSONPath: $.info.pages
            total_pages_value = self._extract_json_path(response_data, '$.info.pages')
            if total_pages_value is not None:

                # Store as JSON if it's an array, otherwise as string
                if isinstance(total_pages_value, list):
                    self.variables['total_pages'] = json.dumps(total_pages_value)
                    self.logger.info(f'Extracted array {var_name} with {len(total_pages_value)} items')
                else:
                    self.variables['total_pages'] = str(total_pages_value)
                    self.logger.info(f'Extracted {var_name} = {self.variables["total_pages"]}')

            # Extract total_count using JSONPath: $.info.count
            total_count_value = self._extract_json_path(response_data, '$.info.count')
            if total_count_value is not None:

                # Store as JSON if it's an array, otherwise as string
                if isinstance(total_count_value, list):
                    self.variables['total_count'] = json.dumps(total_count_value)
                    self.logger.info(f'Extracted array {var_name} with {len(total_count_value)} items')
                else:
                    self.variables['total_count'] = str(total_count_value)
                    self.logger.info(f'Extracted {var_name} = {self.variables["total_count"]}')

        except Exception as e:
            self.logger.error(f'Error extracting variables: {{str(e)}}')

        # Run assertions
        assertion_failures = []

        # Status code assertion
        if response.status_code != 200:
            assertion_failures.append(f'Characters API should return 200 status: expected 200, got {response.status_code}')

        # JSONPath assertion: $.info.pages
        try:
            json_value = self._extract_json_path(response.json(), '$.info.pages')
            if json_value is not None:

                if json_value < 1:
                    assertion_failures.append(f'Should have at least 1 page: value {json_value} is below minimum 1')

            else:
                assertion_failures.append(f'{description}: JSONPath expression returned None')
        except Exception as e:
            assertion_failures.append(f'{description}: error evaluating JSONPath - {{str(e)}}')

        # JSONPath assertion: $.info.count
        try:
            json_value = self._extract_json_path(response.json(), '$.info.count')
            if json_value is not None:

                if json_value < 1:
                    assertion_failures.append(f'Should have at least 1 character: value {json_value} is below minimum 1')

            else:
                assertion_failures.append(f'{description}: JSONPath expression returned None')
        except Exception as e:
            assertion_failures.append(f'{description}: error evaluating JSONPath - {{str(e)}}')

        # Response time assertion
        if response.elapsed.total_seconds() * 1000 > 5000:
            assertion_failures.append(f'Response should complete within 5 seconds: response time {response.elapsed.total_seconds() * 1000:.0f}ms exceeds 5000ms')

        # Report assertion failures
        if assertion_failures:
            failure_message = '; '.join(assertion_failures)
            response.failure(f'Assertions failed: {{failure_message}}')
            self.logger.error(f'Assertions failed: {{failure_message}}')
        else:
            self.logger.info('All assertions passed')

        except Exception as e:
            self.logger.error(f'Error in API call: {str(e)}')

        # Step: Get Random Page of Characters
        try:
            url = self.replace_variables('/api/character/')
            headers = {}
            headers['Content-Type'] = self.replace_variables('application/json')

            headers['Accept'] = 'application/json'
            
            # Prepare request parameters
            params = {}
            params['page'] = self.replace_variables('{{random(1, total_pages)}}')
            body = None

            with self.client.get(
                url,
                headers=headers,
                params=params,
                json=body,
                catch_response=True) as response:

        # Extract variables from response
        try:
            response_data = response.json()

            # Extract character_ids using JSONPath: $.results[*].id
            character_ids_value = self._extract_json_path(response_data, '$.results[*].id')
            if character_ids_value is not None:

                # Store as JSON if it's an array, otherwise as string
                if isinstance(character_ids_value, list):
                    self.variables['character_ids'] = json.dumps(character_ids_value)
                    self.logger.info(f'Extracted array {var_name} with {len(character_ids_value)} items')
                else:
                    self.variables['character_ids'] = str(character_ids_value)
                    self.logger.info(f'Extracted {var_name} = {self.variables["character_ids"]}')

            # Extract character_names using JSONPath: $.results[*].name
            character_names_value = self._extract_json_path(response_data, '$.results[*].name')
            if character_names_value is not None:

                # Store as JSON if it's an array, otherwise as string
                if isinstance(character_names_value, list):
                    self.variables['character_names'] = json.dumps(character_names_value)
                    self.logger.info(f'Extracted array {var_name} with {len(character_names_value)} items')
                else:
                    self.variables['character_names'] = str(character_names_value)
                    self.logger.info(f'Extracted {var_name} = {self.variables["character_names"]}')

            # Extract page_number using JSONPath: $.info.next
            page_number_value = self._extract_json_path(response_data, '$.info.next')
            if page_number_value is not None:

                # Apply custom transformation: extract_page_number
                page_number_value = self._apply_transform(page_number_value, 'extract_page_number')

                # Store as JSON if it's an array, otherwise as string
                if isinstance(page_number_value, list):
                    self.variables['page_number'] = json.dumps(page_number_value)
                    self.logger.info(f'Extracted array {var_name} with {len(page_number_value)} items')
                else:
                    self.variables['page_number'] = str(page_number_value)
                    self.logger.info(f'Extracted {var_name} = {self.variables["page_number"]}')

        except Exception as e:
            self.logger.error(f'Error extracting variables: {{str(e)}}')

        # Run assertions
        assertion_failures = []

        # Status code assertion
        if response.status_code != 200:
            assertion_failures.append(f'Page API should return 200 status: expected 200, got {response.status_code}')

        # JSONPath assertion: $.results
        try:
            json_value = self._extract_json_path(response.json(), '$.results')
            if json_value is not None:

                if json_value < 1:
                    assertion_failures.append(f'Should have at least 1 character in results: value {json_value} is below minimum 1')

            else:
                assertion_failures.append(f'{description}: JSONPath expression returned None')
        except Exception as e:
            assertion_failures.append(f'{description}: error evaluating JSONPath - {{str(e)}}')

        # Response time assertion
        if response.elapsed.total_seconds() * 1000 > 5000:
            assertion_failures.append(f'Response should complete within 5 seconds: response time {response.elapsed.total_seconds() * 1000:.0f}ms exceeds 5000ms')

        # Report assertion failures
        if assertion_failures:
            failure_message = '; '.join(assertion_failures)
            response.failure(f'Assertions failed: {{failure_message}}')
            self.logger.error(f'Assertions failed: {{failure_message}}')
        else:
            self.logger.info('All assertions passed')

        except Exception as e:
            self.logger.error(f'Error in API call: {str(e)}')

        # Step: Get Random Character Details
        try:
            url = self.replace_variables('/api/character/{{random_from_array(character_ids)}}')
            headers = {}
            headers['Content-Type'] = self.replace_variables('application/json')

            headers['Accept'] = 'application/json'
            
            # Prepare request parameters
            params = {}
            body = None

            with self.client.get(
                url,
                headers=headers,
                params=params,
                json=body,
                catch_response=True) as response:

        # Extract variables from response
        try:
            response_data = response.json()

            # Extract character_name using JSONPath: $.name
            character_name_value = self._extract_json_path(response_data, '$.name')
            if character_name_value is not None:

                # Store as JSON if it's an array, otherwise as string
                if isinstance(character_name_value, list):
                    self.variables['character_name'] = json.dumps(character_name_value)
                    self.logger.info(f'Extracted array {var_name} with {len(character_name_value)} items')
                else:
                    self.variables['character_name'] = str(character_name_value)
                    self.logger.info(f'Extracted {var_name} = {self.variables["character_name"]}')

            # Extract character_status using JSONPath: $.status
            character_status_value = self._extract_json_path(response_data, '$.status')
            if character_status_value is not None:

                # Store as JSON if it's an array, otherwise as string
                if isinstance(character_status_value, list):
                    self.variables['character_status'] = json.dumps(character_status_value)
                    self.logger.info(f'Extracted array {var_name} with {len(character_status_value)} items')
                else:
                    self.variables['character_status'] = str(character_status_value)
                    self.logger.info(f'Extracted {var_name} = {self.variables["character_status"]}')

            # Extract character_species using JSONPath: $.species
            character_species_value = self._extract_json_path(response_data, '$.species')
            if character_species_value is not None:

                # Store as JSON if it's an array, otherwise as string
                if isinstance(character_species_value, list):
                    self.variables['character_species'] = json.dumps(character_species_value)
                    self.logger.info(f'Extracted array {var_name} with {len(character_species_value)} items')
                else:
                    self.variables['character_species'] = str(character_species_value)
                    self.logger.info(f'Extracted {var_name} = {self.variables["character_species"]}')

            # Extract character_origin using JSONPath: $.origin.name
            character_origin_value = self._extract_json_path(response_data, '$.origin.name')
            if character_origin_value is not None:

                # Store as JSON if it's an array, otherwise as string
                if isinstance(character_origin_value, list):
                    self.variables['character_origin'] = json.dumps(character_origin_value)
                    self.logger.info(f'Extracted array {var_name} with {len(character_origin_value)} items')
                else:
                    self.variables['character_origin'] = str(character_origin_value)
                    self.logger.info(f'Extracted {var_name} = {self.variables["character_origin"]}')

        except Exception as e:
            self.logger.error(f'Error extracting variables: {{str(e)}}')

        # Run assertions
        assertion_failures = []

        # Status code assertion
        if response.status_code != 200:
            assertion_failures.append(f'Character API should return 200 status: expected 200, got {response.status_code}')

        # JSONPath assertion: $.id
        try:
            json_value = self._extract_json_path(response.json(), '$.id')
            if json_value is not None:

                if json_value < 1:
                    assertion_failures.append(f'Character should have a valid ID: value {json_value} is below minimum 1')

            else:
                assertion_failures.append(f'{description}: JSONPath expression returned None')
        except Exception as e:
            assertion_failures.append(f'{description}: error evaluating JSONPath - {{str(e)}}')

        # JSONPath assertion: $.name
        try:
            json_value = self._extract_json_path(response.json(), '$.name')
            if json_value is not None:

            else:
                assertion_failures.append(f'{description}: JSONPath expression returned None')
        except Exception as e:
            assertion_failures.append(f'{description}: error evaluating JSONPath - {{str(e)}}')

        # JSONPath assertion: $.status
        try:
            json_value = self._extract_json_path(response.json(), '$.status')
            if json_value is not None:

            else:
                assertion_failures.append(f'{description}: JSONPath expression returned None')
        except Exception as e:
            assertion_failures.append(f'{description}: error evaluating JSONPath - {{str(e)}}')

        # Response time assertion
        if response.elapsed.total_seconds() * 1000 > 3000:
            assertion_failures.append(f'Response should complete within 3 seconds: response time {response.elapsed.total_seconds() * 1000:.0f}ms exceeds 3000ms')

        # Report assertion failures
        if assertion_failures:
            failure_message = '; '.join(assertion_failures)
            response.failure(f'Assertions failed: {{failure_message}}')
            self.logger.error(f'Assertions failed: {{failure_message}}')
        else:
            self.logger.info('All assertions passed')

        except Exception as e:
            self.logger.error(f'Error in API call: {str(e)}')

        # Step: Get Multiple Random Characters
        try:
            url = self.replace_variables('/api/character/{{random_subset_from_array(character_ids, 3)}}')
            headers = {}
            headers['Content-Type'] = self.replace_variables('application/json')

            headers['Accept'] = 'application/json'
            
            # Prepare request parameters
            params = {}
            body = None

            with self.client.get(
                url,
                headers=headers,
                params=params,
                json=body,
                catch_response=True) as response:

        # Run assertions
        assertion_failures = []

        # Status code assertion
        if response.status_code != 200:
            assertion_failures.append(f'Multiple characters API should return 200 status: expected 200, got {response.status_code}')

        # Report assertion failures
        if assertion_failures:
            failure_message = '; '.join(assertion_failures)
            response.failure(f'Assertions failed: {{failure_message}}')
            self.logger.error(f'Assertions failed: {{failure_message}}')
        else:
            self.logger.info('All assertions passed')

        except Exception as e:
            self.logger.error(f'Error in API call: {str(e)}')

