from locust import HttpUser, task, between
import json
import time
import logging
import random
import re

class ComprehensiveRandomSelectionTestUser(HttpUser):
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

        # Step: Get All Users - Extract User IDs
        try:
            url = self.replace_variables('/api/users')
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

            # Extract user_ids using JSONPath: $.users[*].id
            user_ids_value = self._extract_json_path(response_data, '$.users[*].id')
            if user_ids_value is not None:

                # Store as JSON if it's an array, otherwise as string
                if isinstance(user_ids_value, list):
                    self.variables['user_ids'] = json.dumps(user_ids_value)
                    self.logger.info(f'Extracted array {var_name} with {len(user_ids_value)} items')
                else:
                    self.variables['user_ids'] = str(user_ids_value)
                    self.logger.info(f'Extracted {var_name} = {self.variables["user_ids"]}')

            # Extract user_names using JSONPath: $.users[*].name
            user_names_value = self._extract_json_path(response_data, '$.users[*].name')
            if user_names_value is not None:

                # Store as JSON if it's an array, otherwise as string
                if isinstance(user_names_value, list):
                    self.variables['user_names'] = json.dumps(user_names_value)
                    self.logger.info(f'Extracted array {var_name} with {len(user_names_value)} items')
                else:
                    self.variables['user_names'] = str(user_names_value)
                    self.logger.info(f'Extracted {var_name} = {self.variables["user_names"]}')

            # Extract total_users using JSONPath: $.total
            total_users_value = self._extract_json_path(response_data, '$.total')
            if total_users_value is not None:

                # Store as JSON if it's an array, otherwise as string
                if isinstance(total_users_value, list):
                    self.variables['total_users'] = json.dumps(total_users_value)
                    self.logger.info(f'Extracted array {var_name} with {len(total_users_value)} items')
                else:
                    self.variables['total_users'] = str(total_users_value)
                    self.logger.info(f'Extracted {var_name} = {self.variables["total_users"]}')

        except Exception as e:
            self.logger.error(f'Error extracting variables: {{str(e)}}')

        # Run assertions
        assertion_failures = []

        # Status code assertion
        if response.status_code != 200:
            assertion_failures.append(f'Users API should return 200 status: expected 200, got {response.status_code}')

        # JSONPath assertion: $.total
        try:
            json_value = self._extract_json_path(response.json(), '$.total')
            if json_value is not None:

                if json_value < 1:
                    assertion_failures.append(f'Should have at least 1 user: value {json_value} is below minimum 1')

            else:
                assertion_failures.append(f'{description}: JSONPath expression returned None')
        except Exception as e:
            assertion_failures.append(f'{description}: error evaluating JSONPath - {{str(e)}}')

        # Report assertion failures
        if assertion_failures:
            failure_message = '; '.join(assertion_failures)
            response.failure(f'Assertions failed: {{failure_message}}')
            self.logger.error(f'Assertions failed: {{failure_message}}')
        else:
            self.logger.info('All assertions passed')

        except Exception as e:
            self.logger.error(f'Error in API call: {str(e)}')

        # Step: Get Random User Details
        try:
            url = self.replace_variables('/api/users/{{random_from_array(user_ids)}}')
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

            # Extract user_products using JSONPath: $.products[*].id
            user_products_value = self._extract_json_path(response_data, '$.products[*].id')
            if user_products_value is not None:

                # Store as JSON if it's an array, otherwise as string
                if isinstance(user_products_value, list):
                    self.variables['user_products'] = json.dumps(user_products_value)
                    self.logger.info(f'Extracted array {var_name} with {len(user_products_value)} items')
                else:
                    self.variables['user_products'] = str(user_products_value)
                    self.logger.info(f'Extracted {var_name} = {self.variables["user_products"]}')

            # Extract user_orders using JSONPath: $.orders[*].id
            user_orders_value = self._extract_json_path(response_data, '$.orders[*].id')
            if user_orders_value is not None:

                # Store as JSON if it's an array, otherwise as string
                if isinstance(user_orders_value, list):
                    self.variables['user_orders'] = json.dumps(user_orders_value)
                    self.logger.info(f'Extracted array {var_name} with {len(user_orders_value)} items')
                else:
                    self.variables['user_orders'] = str(user_orders_value)
                    self.logger.info(f'Extracted {var_name} = {self.variables["user_orders"]}')

        except Exception as e:
            self.logger.error(f'Error extracting variables: {{str(e)}}')

        # Run assertions
        assertion_failures = []

        # Status code assertion
        if response.status_code != 200:
            assertion_failures.append(f'User details API should return 200 status: expected 200, got {response.status_code}')

        # Report assertion failures
        if assertion_failures:
            failure_message = '; '.join(assertion_failures)
            response.failure(f'Assertions failed: {{failure_message}}')
            self.logger.error(f'Assertions failed: {{failure_message}}')
        else:
            self.logger.info('All assertions passed')

        except Exception as e:
            self.logger.error(f'Error in API call: {str(e)}')

        # Step: Get Random Product from User
        try:
            url = self.replace_variables('/api/products/{{random_from_array(user_products)}}')
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

            # Extract product_categories using JSONPath: $.categories[*]
            product_categories_value = self._extract_json_path(response_data, '$.categories[*]')
            if product_categories_value is not None:

                # Store as JSON if it's an array, otherwise as string
                if isinstance(product_categories_value, list):
                    self.variables['product_categories'] = json.dumps(product_categories_value)
                    self.logger.info(f'Extracted array {var_name} with {len(product_categories_value)} items')
                else:
                    self.variables['product_categories'] = str(product_categories_value)
                    self.logger.info(f'Extracted {var_name} = {self.variables["product_categories"]}')

            # Extract product_price using JSONPath: $.price
            product_price_value = self._extract_json_path(response_data, '$.price')
            if product_price_value is not None:

                # Store as JSON if it's an array, otherwise as string
                if isinstance(product_price_value, list):
                    self.variables['product_price'] = json.dumps(product_price_value)
                    self.logger.info(f'Extracted array {var_name} with {len(product_price_value)} items')
                else:
                    self.variables['product_price'] = str(product_price_value)
                    self.logger.info(f'Extracted {var_name} = {self.variables["product_price"]}')

        except Exception as e:
            self.logger.error(f'Error extracting variables: {{str(e)}}')

        # Run assertions
        assertion_failures = []

        # Status code assertion
        if response.status_code != 200:
            assertion_failures.append(f'Product API should return 200 status: expected 200, got {response.status_code}')

        # Report assertion failures
        if assertion_failures:
            failure_message = '; '.join(assertion_failures)
            response.failure(f'Assertions failed: {{failure_message}}')
            self.logger.error(f'Assertions failed: {{failure_message}}')
        else:
            self.logger.info('All assertions passed')

        except Exception as e:
            self.logger.error(f'Error in API call: {str(e)}')

        # Step: Get Random Subset of Products
        try:
            url = self.replace_variables('/api/products/batch')
            headers = {}
            headers['Content-Type'] = self.replace_variables('application/json')

            headers['Accept'] = 'application/json'
            
            # Prepare request parameters
            params = {}
            params['ids'] = self.replace_variables('{{random_subset_from_array(user_products, 3)}}')
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
            assertion_failures.append(f'Batch products API should return 200 status: expected 200, got {response.status_code}')

        # Report assertion failures
        if assertion_failures:
            failure_message = '; '.join(assertion_failures)
            response.failure(f'Assertions failed: {{failure_message}}')
            self.logger.error(f'Assertions failed: {{failure_message}}')
        else:
            self.logger.info('All assertions passed')

        except Exception as e:
            self.logger.error(f'Error in API call: {str(e)}')

        # Step: Get Product by Random Index
        try:
            url = self.replace_variables('/api/products/by-index/{{random_index_from_array(user_products)}}')
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
            assertion_failures.append(f'Product by index API should return 200 status: expected 200, got {response.status_code}')

        # Report assertion failures
        if assertion_failures:
            failure_message = '; '.join(assertion_failures)
            response.failure(f'Assertions failed: {{failure_message}}')
            self.logger.error(f'Assertions failed: {{failure_message}}')
        else:
            self.logger.info('All assertions passed')

        except Exception as e:
            self.logger.error(f'Error in API call: {str(e)}')

        # Step: Search with Random Parameters
        try:
            url = self.replace_variables('/api/search')
            headers = {}
            headers['Content-Type'] = self.replace_variables('application/json')

            headers['Accept'] = 'application/json'
            
            # Prepare request parameters
            params = {}
            params['category'] = self.replace_variables('{{random_from_array(product_categories)}}')
            params['min_price'] = self.replace_variables('{{random(10, 100)}}')
            params['max_price'] = self.replace_variables('{{random(100, 500)}}')
            params['limit'] = self.replace_variables('{{random(5, 20)}}')
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
            assertion_failures.append(f'Search API should return 200 status: expected 200, got {response.status_code}')

        # Report assertion failures
        if assertion_failures:
            failure_message = '; '.join(assertion_failures)
            response.failure(f'Assertions failed: {{failure_message}}')
            self.logger.error(f'Assertions failed: {{failure_message}}')
        else:
            self.logger.info('All assertions passed')

        except Exception as e:
            self.logger.error(f'Error in API call: {str(e)}')

