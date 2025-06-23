from locust import HttpUser, task, between
import json
import time
import logging
import random
import re

class EnhancedEcommerceApiTestUser(HttpUser):
    wait_time = between(1.0, 5.0)
    
    def on_start(self):
        self.variables = {}
        self.logger = logging.getLogger(__name__)
        self.load_test_data()

    def load_test_data(self):
        """Load test data from various sources"""
        self.test_data = {}

        # Load user_credentials data
        self.test_data['user_credentials'] = [{'username': 'testuser1', 'password': 'password123', 'email': 'test1@example.com'}, {'username': 'testuser2', 'password': 'password456', 'email': 'test2@example.com'}, {'username': 'testuser3', 'password': 'password789', 'email': 'test3@example.com'}, {'username': 'admin', 'password': 'admin123', 'email': 'admin@example.com'}, {'username': 'demo', 'password': 'demo123', 'email': 'demo@example.com '}]

        # Load product_catalog data
        self.test_data['product_catalog'] = [{'id': 'PROD001', 'name': 'Laptop Computer', 'category': 'electronics', 'price': 999.99, 'description': 'High-performance laptop for work and gaming'}, {'id': 'PROD002', 'name': 'Wireless Headphones', 'category': 'electronics', 'price': 199.99, 'description': 'Noise-cancelling wireless headphones'}, {'id': 'PROD003', 'name': 'Smartphone', 'category': 'electronics', 'price': 699.99, 'description': 'Latest smartphone with advanced features'}, {'id': 'PROD004', 'name': 'Coffee Maker', 'category': 'home', 'price': 89.99, 'description': 'Programmable coffee maker for home use'}, {'id': 'PROD005', 'name': 'Running Shoes', 'category': 'sports', 'price': 129.99, 'description': 'Comfortable running shoes for athletes'}]

        # Randomize data for each user
        for source_name, data in self.test_data.items():
            if data and isinstance(data, list):
                self.test_data[f'{source_name}_current'] = random.choice(data)


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

    
    def replace_variables(self, text):
        """Replace variables in text with actual values"""
        if not text:
            return text
        try:
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

        # Step: User Login
        try:
            url = self.replace_variables('/api/auth/login')
            headers = {}
            headers['Content-Type'] = self.replace_variables('application/json')

            headers['Accept'] = 'application/json'
            
            # Prepare request parameters
            params = {}
            body = {
            "username": "{{username}}",
            "password": "{{password}}"
}
            body = self.replace_variables(json.dumps(body))
            body = json.loads(body)

            with self.client.post(
                url,
                headers=headers,
                params=params,
                json=body,
                catch_response=True) as response:

        # Extract variables from response
        try:
            response_data = response.json()

            # Extract auth_token using JSONPath: $.data.token
            auth_token_value = self._extract_json_path(response_data, '$.data.token')
            if auth_token_value is not None:
                self.variables['auth_token'] = str(auth_token_value)
                self.logger.info(f'Extracted {var_name} = {self.variables["auth_token"]}')

            # Extract user_id using JSONPath: $.data.user.id
            user_id_value = self._extract_json_path(response_data, '$.data.user.id')
            if user_id_value is not None:
                self.variables['user_id'] = str(user_id_value)
                self.logger.info(f'Extracted {var_name} = {self.variables["user_id"]}')

        except Exception as e:
            self.logger.error(f'Error extracting variables: {{str(e)}}')

        # Run assertions
        assertion_failures = []

        # Status code assertion
        if response.status_code != 200:
            assertion_failures.append(f'Login should return 200 status: expected 200, got {response.status_code}')

        # Response time assertion
        if response.elapsed.total_seconds() * 1000 > 2000:
            assertion_failures.append(f'Login should complete within 2 seconds: response time {response.elapsed.total_seconds() * 1000:.0f}ms exceeds 2000ms')

        # JSONPath assertion: $.success
        try:
            json_value = self._extract_json_path(response.json(), '$.success')
            if json_value is not None:

                if json_value != True:
                    assertion_failures.append(f'Login should be successful: expected True, got {json_value}')

            else:
                assertion_failures.append(f'{description}: JSONPath expression returned None')
        except Exception as e:
            assertion_failures.append(f'{description}: error evaluating JSONPath - {{str(e)}}')

        # Body contains text assertion
        if 'token' not in response.text:
            assertion_failures.append(f'Response should contain token: response does not contain text "token"')

        # Report assertion failures
        if assertion_failures:
            failure_message = '; '.join(assertion_failures)
            response.failure(f'Assertions failed: {{failure_message}}')
            self.logger.error(f'Assertions failed: {{failure_message}}')
        else:
            self.logger.info('All assertions passed')

        except Exception as e:
            self.logger.error(f'Error in API call: {str(e)}')

        # Step: Search Products
        try:
            url = self.replace_variables('/api/products/search')
            headers = {}
            headers['Authorization'] = self.replace_variables('Bearer {{auth_token}}')
            headers['Content-Type'] = self.replace_variables('application/json')

            headers['Accept'] = 'application/json'
            
            # Prepare request parameters
            params = {}
            params['query'] = self.replace_variables('{{product_name}}')
            params['category'] = self.replace_variables('{{product_category}}')
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

            # Extract first_product_id using JSONPath: $.products[0].id
            first_product_id_value = self._extract_json_path(response_data, '$.products[0].id')
            if first_product_id_value is not None:
                self.variables['first_product_id'] = str(first_product_id_value)
                self.logger.info(f'Extracted {var_name} = {self.variables["first_product_id"]}')

            # Extract total_results using JSONPath: $.total
            total_results_value = self._extract_json_path(response_data, '$.total')
            if total_results_value is not None:
                self.variables['total_results'] = str(total_results_value)
                self.logger.info(f'Extracted {var_name} = {self.variables["total_results"]}')

        except Exception as e:
            self.logger.error(f'Error extracting variables: {{str(e)}}')

        # Run assertions
        assertion_failures = []

        # Status code assertion
        if response.status_code != 200:
            assertion_failures.append(f'status_code assertion: expected 200, got {response.status_code}')

        # JSONPath assertion: $.total
        try:
            json_value = self._extract_json_path(response.json(), '$.total')
            if json_value is not None:

                if json_value < 1:
                    assertion_failures.append(f'Should find at least one product: value {json_value} is below minimum 1')

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

        # Step: Add Product to Cart
        try:
            url = self.replace_variables('/api/cart/add')
            headers = {}
            headers['Authorization'] = self.replace_variables('Bearer {{auth_token}}')
            headers['Content-Type'] = self.replace_variables('application/json')

            headers['Accept'] = 'application/json'
            
            # Prepare request parameters
            params = {}
            body = {
            "product_id": "{{first_product_id}}",
            "quantity": 1
}
            body = self.replace_variables(json.dumps(body))
            body = json.loads(body)

            with self.client.post(
                url,
                headers=headers,
                params=params,
                json=body,
                catch_response=True) as response:

        # Extract variables from response
        try:
            response_data = response.json()

            # Extract cart_id using JSONPath: $.cart_id
            cart_id_value = self._extract_json_path(response_data, '$.cart_id')
            if cart_id_value is not None:
                self.variables['cart_id'] = str(cart_id_value)
                self.logger.info(f'Extracted {var_name} = {self.variables["cart_id"]}')

        except Exception as e:
            self.logger.error(f'Error extracting variables: {{str(e)}}')

        # Run assertions
        assertion_failures = []

        # Status code assertion
        if response.status_code != 201:
            assertion_failures.append(f'status_code assertion: expected 201, got {response.status_code}')

        # JSONPath assertion: $.success
        try:
            json_value = self._extract_json_path(response.json(), '$.success')
            if json_value is not None:

                if json_value != True:
                    assertion_failures.append(f'json_path assertion: expected True, got {json_value}')

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

        # Step: Proceed to Checkout
        try:
            url = self.replace_variables('/api/checkout')
            headers = {}
            headers['Authorization'] = self.replace_variables('Bearer {{auth_token}}')
            headers['Content-Type'] = self.replace_variables('application/json')

            headers['Accept'] = 'application/json'
            
            # Prepare request parameters
            params = {}
            body = {
            "cart_id": "{{cart_id}}",
            "shipping_address": {
                        "street": "123 Test St",
                        "city": "Test City",
                        "zip": "12345"
            }
}
            body = self.replace_variables(json.dumps(body))
            body = json.loads(body)

            with self.client.post(
                url,
                headers=headers,
                params=params,
                json=body,
                catch_response=True) as response:

        # Extract variables from response
        try:
            response_data = response.json()

            # Extract order_id using JSONPath: $.order.id
            order_id_value = self._extract_json_path(response_data, '$.order.id')
            if order_id_value is not None:
                self.variables['order_id'] = str(order_id_value)
                self.logger.info(f'Extracted {var_name} = {self.variables["order_id"]}')

            # Extract order_status using JSONPath: $.order.status
            order_status_value = self._extract_json_path(response_data, '$.order.status')
            if order_status_value is not None:
                self.variables['order_status'] = str(order_status_value)
                self.logger.info(f'Extracted {var_name} = {self.variables["order_status"]}')

        except Exception as e:
            self.logger.error(f'Error extracting variables: {{str(e)}}')

        # Run assertions
        assertion_failures = []

        # Status code assertion
        if response.status_code != 200:
            assertion_failures.append(f'status_code assertion: expected 200, got {response.status_code}')

        # JSONPath assertion: $.order.status
        try:
            json_value = self._extract_json_path(response.json(), '$.order.status')
            if json_value is not None:

                if json_value != 'pending':
                    assertion_failures.append(f'Order should be in pending status: expected 'pending', got {json_value}')

            else:
                assertion_failures.append(f'{description}: JSONPath expression returned None')
        except Exception as e:
            assertion_failures.append(f'{description}: error evaluating JSONPath - {{str(e)}}')

        # Regex assertion
        if not re.search(r'ORD-\d{8}', response.text):
            assertion_failures.append(f'Order ID should match expected format: response does not match pattern "ORD-\d{8}"')

        # Report assertion failures
        if assertion_failures:
            failure_message = '; '.join(assertion_failures)
            response.failure(f'Assertions failed: {{failure_message}}')
            self.logger.error(f'Assertions failed: {{failure_message}}')
        else:
            self.logger.info('All assertions passed')

        except Exception as e:
            self.logger.error(f'Error in API call: {str(e)}')

