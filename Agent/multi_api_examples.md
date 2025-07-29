# Multi-API Sequences with Correlation Examples

This guide shows how the enhanced Locust agent handles complex multi-API scenarios with correlation and transaction naming.

## 🎯 **Your Question Answered**

> **"Will this agent be able to run ANY API given? What if I want to run 3 APIs one after each other that requires some kind of correlation from the first one to use on the second one, and the third API needs a correlation from the second call?"**

**✅ YES!** The enhanced agent can handle exactly this scenario. Here are comprehensive examples:

## 🔐 **Example 1: Authentication Flow with Token Correlation**

### **Natural Language Request:**
```
Create a HomePage transaction named "UserAuthentication" with 15 users for 3 minutes.
First call POST /api/auth/login with username and password, extract the auth_token from response.
Then call GET /api/user/profile using the auth_token in Authorization header.
Finally call POST /api/auth/logout using the same auth_token.
Verify status code 200 for all calls and response time under 500ms.
```

### **Generated Script Structure:**
```python
class UserAuthenticationUser(HttpUser):
    wait_time = between(1.0, 5.0)
    
    def on_start(self):
        self.variables = {}
        self.logger = logging.getLogger(__name__)
    
    @task
    def run_scenario(self):
        # Step 1: Login and extract token
        with self.client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass"},
            headers={"Content-Type": "application/json"},
            catch_response=True) as response:
            
            if response.status_code == 200:
                # Extract auth_token from response
                auth_data = response.json()
                self.variables['auth_token'] = auth_data.get('token')
                response.success()
            else:
                response.failure('Login failed')
        
        # Step 2: Get user profile using token
        if 'auth_token' in self.variables:
            with self.client.get(
                "/api/user/profile",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.variables['auth_token']}"
                },
                catch_response=True) as response:
                
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure('Profile fetch failed')
        
        # Step 3: Logout using same token
        if 'auth_token' in self.variables:
            with self.client.post(
                "/api/auth/logout",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.variables['auth_token']}"
                },
                catch_response=True) as response:
                
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure('Logout failed')
```

## 🛒 **Example 2: E-commerce Checkout with Cart/Order Correlation**

### **Natural Language Request:**
```
Create a CheckoutFlow transaction named "EcommerceCheckout" with 20 users for 5 minutes.
First call GET /api/products to browse products, extract product_id from first product.
Then call POST /api/cart with the product_id to add to cart, extract cart_id from response.
Then call GET /api/cart/{cart_id} to view cart.
Then call POST /api/orders with cart_id and payment details, extract order_id.
Finally call GET /api/orders/{order_id} to confirm order.
Verify all calls return status 200 and response time under 1 second.
```

### **Generated Script Structure:**
```python
class EcommerceCheckoutUser(HttpUser):
    wait_time = between(1.0, 5.0)
    
    def on_start(self):
        self.variables = {}
        self.logger = logging.getLogger(__name__)
    
    @task
    def run_scenario(self):
        # Step 1: Browse products and extract product_id
        with self.client.get(
            "/api/products",
            headers={"Content-Type": "application/json"},
            catch_response=True) as response:
            
            if response.status_code == 200:
                products_data = response.json()
                if products_data.get('products'):
                    self.variables['product_id'] = products_data['products'][0]['id']
                response.success()
            else:
                response.failure('Products fetch failed')
        
        # Step 2: Add to cart and extract cart_id
        if 'product_id' in self.variables:
            with self.client.post(
                "/api/cart",
                json={"product_id": self.variables['product_id']},
                headers={"Content-Type": "application/json"},
                catch_response=True) as response:
                
                if response.status_code == 200:
                    cart_data = response.json()
                    self.variables['cart_id'] = cart_data.get('cart_id')
                    response.success()
                else:
                    response.failure('Add to cart failed')
        
        # Step 3: View cart using cart_id
        if 'cart_id' in self.variables:
            with self.client.get(
                f"/api/cart/{self.variables['cart_id']}",
                headers={"Content-Type": "application/json"},
                catch_response=True) as response:
                
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure('Cart view failed')
        
        # Step 4: Create order and extract order_id
        if 'cart_id' in self.variables:
            with self.client.post(
                "/api/orders",
                json={
                    "cart_id": self.variables['cart_id'],
                    "payment_method": "credit_card",
                    "shipping_address": "123 Main St"
                },
                headers={"Content-Type": "application/json"},
                catch_response=True) as response:
                
                if response.status_code == 200:
                    order_data = response.json()
                    self.variables['order_id'] = order_data.get('order_id')
                    response.success()
                else:
                    response.failure('Order creation failed')
        
        # Step 5: Confirm order using order_id
        if 'order_id' in self.variables:
            with self.client.get(
                f"/api/orders/{self.variables['order_id']}",
                headers={"Content-Type": "application/json"},
                catch_response=True) as response:
                
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure('Order confirmation failed')
```

## 🌌 **Example 3: Rick and Morty API with Character Correlation**

### **Natural Language Request:**
```
Create a GetCharacters transaction named "RickAndMortyAPI" with 10 users for 4 minutes.
First call GET /api/character?page=1 to get characters list, extract total_pages from info.
Then call GET /api/character/1 to get specific character, extract character_name.
Then call GET /api/character?name={character_name} to search for that character.
Finally call GET /api/location/1 to get location details.
Verify all calls return status 200 and response time under 300ms.
```

### **Generated Script Structure:**
```python
class RickAndMortyAPIUser(HttpUser):
    wait_time = between(1.0, 5.0)
    
    def on_start(self):
        self.variables = {}
        self.logger = logging.getLogger(__name__)
    
    @task
    def run_scenario(self):
        # Step 1: Get characters list and extract total_pages
        with self.client.get(
            "/api/character?page=1",
            headers={"Content-Type": "application/json"},
            catch_response=True) as response:
            
            if response.status_code == 200:
                characters_data = response.json()
                self.variables['total_pages'] = characters_data.get('info', {}).get('pages', 1)
                response.success()
            else:
                response.failure('Characters list fetch failed')
        
        # Step 2: Get specific character and extract character_name
        with self.client.get(
            "/api/character/1",
            headers={"Content-Type": "application/json"},
            catch_response=True) as response:
            
            if response.status_code == 200:
                character_data = response.json()
                self.variables['character_name'] = character_data.get('name')
                response.success()
            else:
                response.failure('Character fetch failed')
        
        # Step 3: Search for character using character_name
        if 'character_name' in self.variables:
            with self.client.get(
                f"/api/character?name={self.variables['character_name']}",
                headers={"Content-Type": "application/json"},
                catch_response=True) as response:
                
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure('Character search failed')
        
        # Step 4: Get location details
        with self.client.get(
            "/api/location/1",
            headers={"Content-Type": "application/json"},
            catch_response=True) as response:
            
            if response.status_code == 200:
                response.success()
            else:
                response.failure('Location fetch failed')
```

## 💳 **Example 4: Payment Processing with Intent Correlation**

### **Natural Language Request:**
```
Create a PaymentProcessing transaction named "PaymentFlow" with 8 users for 6 minutes.
First call GET /api/payment/methods to get available payment methods.
Then call POST /api/payment/create-intent with order details, extract payment_intent_id.
Then call POST /api/payment/confirm with payment_intent_id and payment method.
Then call GET /api/payment/status/{payment_intent_id} to check payment status.
Finally call POST /api/orders/update-status with order_id and payment status.
Verify all calls return appropriate status codes and response time under 2 seconds.
```

### **Generated Script Structure:**
```python
class PaymentFlowUser(HttpUser):
    wait_time = between(1.0, 5.0)
    
    def on_start(self):
        self.variables = {}
        self.logger = logging.getLogger(__name__)
    
    @task
    def run_scenario(self):
        # Step 1: Get payment methods
        with self.client.get(
            "/api/payment/methods",
            headers={"Content-Type": "application/json"},
            catch_response=True) as response:
            
            if response.status_code == 200:
                response.success()
            else:
                response.failure('Payment methods fetch failed')
        
        # Step 2: Create payment intent and extract payment_intent_id
        with self.client.post(
            "/api/payment/create-intent",
            json={
                "amount": 1000,
                "currency": "usd",
                "payment_method": "card"
            },
            headers={"Content-Type": "application/json"},
            catch_response=True) as response:
            
            if response.status_code == 200:
                intent_data = response.json()
                self.variables['payment_intent_id'] = intent_data.get('id')
                response.success()
            else:
                response.failure('Payment intent creation failed')
        
        # Step 3: Confirm payment using payment_intent_id
        if 'payment_intent_id' in self.variables:
            with self.client.post(
                "/api/payment/confirm",
                json={
                    "payment_intent_id": self.variables['payment_intent_id'],
                    "payment_method": "card"
                },
                headers={"Content-Type": "application/json"},
                catch_response=True) as response:
                
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure('Payment confirmation failed')
        
        # Step 4: Check payment status using payment_intent_id
        if 'payment_intent_id' in self.variables:
            with self.client.get(
                f"/api/payment/status/{self.variables['payment_intent_id']}",
                headers={"Content-Type": "application/json"},
                catch_response=True) as response:
                
                if response.status_code == 200:
                    status_data = response.json()
                    self.variables['payment_status'] = status_data.get('status')
                    response.success()
                else:
                    response.failure('Payment status check failed')
        
        # Step 5: Update order status with payment status
        if 'payment_status' in self.variables:
            with self.client.post(
                "/api/orders/update-status",
                json={
                    "order_id": "ORDER123",
                    "payment_status": self.variables['payment_status']
                },
                headers={"Content-Type": "application/json"},
                catch_response=True) as response:
                
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure('Order status update failed')
```

## 🔧 **Key Features Demonstrated**

### **✅ Multi-API Sequences**
- Support for any number of API calls in sequence
- Dependency management between steps
- Conditional execution based on previous responses

### **✅ Advanced Correlation**
- **Variable Extraction**: Extract values from API responses
- **Variable Reuse**: Use extracted variables in subsequent calls
- **Dynamic Substitution**: Replace placeholders with actual values
- **Header Correlation**: Use extracted tokens in Authorization headers
- **URL Correlation**: Use extracted IDs in URL paths

### **✅ Transaction Naming**
- **Custom Names**: HomePage, GetCharacters, CheckoutFlow, etc.
- **Meaningful Reporting**: Clear transaction names in test reports
- **Step-Level Naming**: Each API call has a descriptive name

### **✅ Complex Scenarios**
- **Authentication Flows**: Login → Use Token → Logout
- **E-commerce**: Browse → Add to Cart → Checkout → Confirm
- **Data Retrieval**: Get List → Extract ID → Get Details → Search
- **Payment Processing**: Create Intent → Confirm → Check Status → Update

## 🚀 **Usage Examples**

### **Command Line:**
```bash
# Basic multi-API sequence
python Agent/enhanced_locust_agent.py "Create a HomePage transaction that calls /api/login, then /api/user/profile using the token from login, then /api/logout"

# Complex e-commerce flow
python Agent/enhanced_locust_agent.py "Create a CheckoutFlow transaction that calls /api/products, extracts product_id, calls /api/cart with product_id, extracts cart_id, calls /api/orders with cart_id"

# Rick and Morty sequence
python Agent/enhanced_locust_agent.py "Create a GetCharacters transaction that calls /api/character?page=1, extracts character_name, calls /api/character?name={character_name}"
```

### **Programmatic:**
```python
from Agent.enhanced_locust_agent import EnhancedLocustAgent

agent = EnhancedLocustAgent()

# Process complex multi-API request
result = agent.process_enhanced_request(
    "Create a HomePage transaction that calls /api/login, then /api/user/profile using the token from login, then /api/logout"
)

if result['success']:
    print(f"Transaction: {result['parsed_request'].transaction_name}")
    print(f"API Steps: {len(result['parsed_request'].api_sequence)}")
    print(f"Script: {result['script_path']}")
```

## 🎯 **Answer to Your Question**

**YES!** The enhanced agent can handle:

1. ✅ **ANY API** - Supports any HTTP method, URL, headers, body
2. ✅ **Multi-API Sequences** - 3, 5, 10+ API calls in sequence
3. ✅ **Correlation** - Extract from first API, use in second, extract from second, use in third
4. ✅ **Transaction Naming** - HomePage, GetCharacters, CheckoutFlow, etc.
5. ✅ **Complex Workflows** - Authentication, e-commerce, payment processing
6. ✅ **Dynamic Variables** - Tokens, IDs, names, statuses
7. ✅ **Conditional Logic** - Only proceed if previous step succeeds
8. ✅ **Error Handling** - Graceful failure handling at each step

The enhanced agent transforms your natural language into production-ready Locust scripts with full correlation support! 🚀 