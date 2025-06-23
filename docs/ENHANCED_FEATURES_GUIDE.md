# Enhanced Script Generator Features Guide

## Overview

The Enhanced Script Generator extends the Locust AI Agent with powerful capabilities for creating sophisticated end-to-end test scenarios. This guide covers all the new features that enable dynamic data-driven testing with comprehensive assertions and variable correlation.

## 🎯 Key Features

### 1. Dynamic Parameters (Data-Driven Testing)

#### CSV Data Sources
Load test data from CSV files to parameterize your tests:

```json
{
  "parameters": {
    "data_sources": [
      {
        "name": "user_credentials",
        "type": "csv",
        "file": "test_data/users.csv",
        "columns": ["username", "password", "email"]
      }
    ]
  }
}
```

**Generated Code:**
- Each virtual user gets a random row from the CSV
- Variables are automatically replaced: `{{username}}`, `{{password}}`, `{{email}}`

#### JSON Data Sources
Load structured data from JSON files:

```json
{
  "parameters": {
    "data_sources": [
      {
        "name": "product_catalog",
        "type": "json",
        "file": "test_data/products.json",
        "path": "$.products[*]"
      }
    ]
  }
}
```

**Generated Code:**
- Extracts array elements using JSONPath-like expressions
- Supports wildcards like `$.products[*]` for array iteration

### 2. Variable Extraction & Correlation

#### JSONPath Extraction
Extract values from JSON responses using JSONPath expressions:

```json
{
  "extract": {
    "auth_token": {
      "type": "json_path",
      "expression": "$.data.token"
    },
    "user_id": {
      "type": "json_path",
      "expression": "$.data.user.id"
    }
  }
}
```

#### Regex Extraction
Extract values using regular expressions:

```json
{
  "extract": {
    "session_id": {
      "type": "regex",
      "expression": "session_id=([a-zA-Z0-9]+)"
    }
  }
}
```

#### Boundary Extraction
Extract text between left and right boundaries:

```json
{
  "extract": {
    "csrf_token": {
      "type": "boundary",
      "left_boundary": "name=\"csrf_token\" value=\"",
      "right_boundary": "\""
    }
  }
}
```

### 3. Comprehensive Assertions

#### Status Code Assertions
```json
{
  "assertions": [
    {
      "type": "status_code",
      "expected": 200,
      "description": "Login should return 200 status"
    }
  ]
}
```

#### Response Time Assertions
```json
{
  "assertions": [
    {
      "type": "response_time_ms",
      "max": 2000,
      "description": "Login should complete within 2 seconds"
    }
  ]
}
```

#### JSONPath Assertions
```json
{
  "assertions": [
    {
      "type": "json_path",
      "expression": "$.success",
      "expected": true,
      "description": "Login should be successful"
    },
    {
      "type": "json_path",
      "expression": "$.total",
      "min": 1,
      "description": "Should find at least one product"
    }
  ]
}
```

#### Text Content Assertions
```json
{
  "assertions": [
    {
      "type": "body_contains_text",
      "text": "token",
      "description": "Response should contain token"
    }
  ]
}
```

#### Regex Pattern Assertions
```json
{
  "assertions": [
    {
      "type": "regex",
      "pattern": "ORD-\\d{8}",
      "description": "Order ID should match expected format"
    }
  ]
}
```

## 📋 Complete Example Scenario

```json
{
  "name": "Enhanced E-commerce API Test",
  "description": "Comprehensive end-to-end test scenario",
  "base_url": "https://api.example.com",
  "min_wait": 1000,
  "max_wait": 5000,
  "parameters": {
    "data_sources": [
      {
        "name": "user_credentials",
        "type": "csv",
        "file": "test_data/users.csv",
        "columns": ["username", "password", "email"]
      },
      {
        "name": "product_catalog",
        "type": "json",
        "file": "test_data/products.json",
        "path": "$.products[*]"
      }
    ]
  },
  "steps": [
    {
      "id": "login_step",
      "name": "User Login",
      "method": "POST",
      "url": "/api/auth/login",
      "headers": {
        "Content-Type": "application/json"
      },
      "body": {
        "username": "{{username}}",
        "password": "{{password}}"
      },
      "extract": {
        "auth_token": {
          "type": "json_path",
          "expression": "$.data.token"
        }
      },
      "assertions": [
        {
          "type": "status_code",
          "expected": 200
        },
        {
          "type": "response_time_ms",
          "max": 2000
        },
        {
          "type": "json_path",
          "expression": "$.success",
          "expected": true
        }
      ]
    },
    {
      "id": "search_products",
      "name": "Search Products",
      "method": "GET",
      "url": "/api/products/search",
      "headers": {
        "Authorization": "Bearer {{auth_token}}"
      },
      "params": {
        "query": "{{name}}",
        "category": "{{category}}"
      },
      "extract": {
        "first_product_id": {
          "type": "json_path",
          "expression": "$.products[0].id"
        }
      },
      "assertions": [
        {
          "type": "status_code",
          "expected": 200
        },
        {
          "type": "json_path",
          "expression": "$.total",
          "min": 1
        }
      ]
    }
  ]
}
```

## 🔧 Usage

### 1. Create Your Scenario JSON
Define your test scenario with the enhanced features above.

### 2. Prepare Test Data Files
Create CSV or JSON files with your test data:

**users.csv:**
```csv
username,password,email
testuser1,password123,test1@example.com
testuser2,password456,test2@example.com
```

**products.json:**
```json
{
  "products": [
    {
      "id": "PROD001",
      "name": "Laptop Computer",
      "category": "electronics"
    }
  ]
}
```

### 3. Generate the Script
```python
from core.enhanced_script_generator import EnhancedScriptGenerator

generator = EnhancedScriptGenerator(
    scenario_file="examples/enhanced_scenario.json",
    output_file="generated_scripts/My_Enhanced_Test.py"
)
generator.generate_script()
```

### 4. Run with Locust
```bash
locust -f generated_scripts/My_Enhanced_Test.py --host=https://api.example.com
```

## 🎨 Advanced Features

### Variable Correlation
Variables extracted in one step are automatically available in subsequent steps:

1. **Step 1:** Login and extract `auth_token`
2. **Step 2:** Use `{{auth_token}}` in Authorization header
3. **Step 3:** Use extracted `product_id` in request body

### Dynamic Data Randomization
- Each virtual user gets different test data
- Data is randomized at user startup
- Supports multiple data sources per scenario

### Comprehensive Error Handling
- Graceful handling of missing data
- Detailed logging of extractions and assertions
- Clear failure messages for debugging

### Flexible Assertion Types
- **Exact matches:** `expected: "value"`
- **Range checks:** `min: 1, max: 100`
- **Pattern matching:** regex and text containment
- **Performance checks:** response time limits

## 🚀 Best Practices

### 1. Data Source Organization
- Keep test data files in a dedicated `test_data/` directory
- Use descriptive names for data sources
- Include enough test data for your load test duration

### 2. Variable Naming
- Use clear, descriptive variable names
- Follow a consistent naming convention
- Document complex JSONPath expressions

### 3. Assertion Strategy
- Start with basic status code assertions
- Add performance assertions for critical paths
- Use JSONPath assertions for business logic validation
- Include regex assertions for format validation

### 4. Error Handling
- Provide descriptive assertion messages
- Use appropriate timeout values
- Handle missing or malformed responses gracefully

## 🔍 Troubleshooting

### Common Issues

1. **Data Source Not Found**
   - Check file paths are relative to scenario file
   - Verify CSV/JSON file format
   - Ensure file encoding is UTF-8

2. **Variable Extraction Fails**
   - Verify JSONPath expressions
   - Check response structure matches expectations
   - Review regex patterns for correctness

3. **Assertions Always Fail**
   - Confirm expected values match actual responses
   - Check data types (string vs number)
   - Verify response format hasn't changed

### Debug Tips

1. **Enable Detailed Logging**
   ```python
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Check Generated Script**
   - Review the generated Python code
   - Verify variable replacements
   - Test assertions manually

3. **Validate JSON Schema**
   - Use JSON schema validators
   - Check for syntax errors
   - Verify all required fields

## 📈 Performance Considerations

- **Data Source Size:** Large CSV/JSON files increase memory usage
- **Complex JSONPath:** Deep nested expressions may impact performance
- **Multiple Assertions:** Each assertion adds processing overhead
- **Variable Storage:** Extracted variables consume memory per user

## 🔮 Future Enhancements

Planned features for upcoming releases:
- Database data sources (MySQL, PostgreSQL)
- API data sources (REST endpoints)
- Conditional assertions based on response content
- Custom assertion functions
- Data source caching and optimization
- Parallel data source loading 