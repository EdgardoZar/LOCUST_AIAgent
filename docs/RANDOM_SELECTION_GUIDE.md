# Random Selection Guide

This guide explains how to use random selection features in your Locust AI Agent scenarios to create more dynamic and realistic test scenarios.

## Overview

Random selection helps create more realistic test scenarios by:
- Reducing predictable patterns in API calls
- Distributing load across different resources
- Simulating real user behavior more accurately
- Avoiding overuse of the same correlated values

## Available Random Functions

### 1. `{{random(min, max)}}`
Generates a random integer between `min` and `max` (inclusive).

**Example:**
```json
{
  "params": {
    "page": "{{random(1, 10)}}",
    "limit": "{{random(5, 20)}}"
  }
}
```

**Use Cases:**
- Random page numbers for pagination
- Random limits for API calls
- Random IDs within a known range
- Random timeouts or delays

### 2. `{{random_from_array(variable_name)}}`
Selects a random element from an array stored in a variable.

**Example:**
```json
{
  "steps": [
    {
      "id": "get_users",
      "extract": {
        "user_ids": {
          "type": "json_path",
          "expression": "$.users[*].id"
        }
      }
    },
    {
      "id": "get_random_user",
      "url": "/api/users/{{random_from_array(user_ids)}}"
    }
  ]
}
```

**Use Cases:**
- Selecting random users from a list
- Choosing random products from a catalog
- Picking random items from search results
- Selecting random categories or tags

### 3. `{{random_subset_from_array(variable_name, n)}}`
Selects a random subset of `n` elements from an array.

**Example:**
```json
{
  "params": {
    "product_ids": "{{random_subset_from_array(user_products, 3)}}"
  }
}
```

**Use Cases:**
- Batch operations with random items
- Selecting multiple random products for comparison
- Creating random shopping carts
- Testing bulk operations

### 4. `{{random_index_from_array(variable_name)}}`
Returns a random index (position) from an array.

**Example:**
```json
{
  "url": "/api/products/by-index/{{random_index_from_array(product_ids)}}"
}
```

**Use Cases:**
- Accessing items by position rather than value
- Testing index-based APIs
- Random navigation through lists
- Stress testing with random positions

## Array Extraction Support

### JSONPath Array Extraction
The framework supports extracting arrays using JSONPath expressions with wildcards:

```json
{
  "extract": {
    "user_ids": {
      "type": "json_path",
      "expression": "$.users[*].id"
    },
    "product_names": {
      "type": "json_path",
      "expression": "$.products[*].name"
    },
    "categories": {
      "type": "json_path",
      "expression": "$.categories[*]"
    }
  }
}
```

### Array Storage
- Arrays are automatically stored as JSON strings in variables
- The random functions can parse these JSON arrays
- Fallback support for comma-separated strings

## Complete Example Scenarios

### 1. E-commerce Flow with Random Selection

```json
{
  "name": "E-commerce Random Flow",
  "steps": [
    {
      "id": "get_products",
      "method": "GET",
      "url": "/api/products",
      "extract": {
        "product_ids": {
          "type": "json_path",
          "expression": "$.products[*].id"
        },
        "category_ids": {
          "type": "json_path",
          "expression": "$.categories[*].id"
        }
      }
    },
    {
      "id": "search_random_category",
      "method": "GET",
      "url": "/api/products/search",
      "params": {
        "category": "{{random_from_array(category_ids)}}",
        "limit": "{{random(5, 15)}}"
      }
    },
    {
      "id": "add_random_products",
      "method": "POST",
      "url": "/api/cart/add",
      "body": {
        "products": "{{random_subset_from_array(product_ids, 3)}}"
      }
    }
  ]
}
```

### 2. User Management with Random Selection

```json
{
  "name": "User Management Random Test",
  "steps": [
    {
      "id": "get_all_users",
      "method": "GET",
      "url": "/api/users",
      "extract": {
        "user_ids": {
          "type": "json_path",
          "expression": "$.users[*].id"
        }
      }
    },
    {
      "id": "get_random_user",
      "method": "GET",
      "url": "/api/users/{{random_from_array(user_ids)}}",
      "extract": {
        "user_orders": {
          "type": "json_path",
          "expression": "$.orders[*].id"
        }
      }
    },
    {
      "id": "get_random_order",
      "method": "GET",
      "url": "/api/orders/{{random_from_array(user_orders)}}"
    }
  ]
}
```

### 3. Rick and Morty API Example

```json
{
  "name": "Rick and Morty Random Test",
  "steps": [
    {
      "id": "get_characters_page",
      "method": "GET",
      "url": "/api/character",
      "params": {
        "page": "{{random(1, 42)}}"
      },
      "extract": {
        "character_ids": {
          "type": "json_path",
          "expression": "$.results[*].id"
        }
      }
    },
    {
      "id": "get_random_character",
      "method": "GET",
      "url": "/api/character/{{random_from_array(character_ids)}}"
    },
    {
      "id": "get_multiple_characters",
      "method": "GET",
      "url": "/api/character/{{random_subset_from_array(character_ids, 3)}}"
    }
  ]
}
```

## Best Practices

### 1. Extract Arrays First
Always extract arrays in one step before using them in random selection:

```json
{
  "steps": [
    {
      "id": "extract_data",
      "extract": {
        "items": {
          "type": "json_path",
          "expression": "$.items[*].id"
        }
      }
    },
    {
      "id": "use_random",
      "url": "/api/items/{{random_from_array(items)}}"
    }
  ]
}
```

### 2. Use Meaningful Variable Names
Choose descriptive variable names for better readability:

```json
{
  "extract": {
    "active_user_ids": {
      "type": "json_path",
      "expression": "$.users[?(@.status=='active')].id"
    }
  }
}
```

### 3. Combine with Other Dynamic Features
Use random selection with other dynamic features:

```json
{
  "params": {
    "user_id": "{{random_from_array(user_ids)}}",
    "page": "{{random(1, total_pages)}}",
    "limit": "{{random(10, 50)}}"
  }
}
```

### 4. Handle Empty Arrays
Always provide fallbacks for empty arrays:

```json
{
  "url": "/api/users/{{random_from_array(user_ids) || 1}}"
}
```

## Error Handling

The framework includes robust error handling for random functions:

- **Invalid arrays**: Returns fallback values (1 for random_from_array, [] for random_subset_from_array)
- **Invalid ranges**: Uses safe defaults for random(min, max)
- **JSON parsing errors**: Falls back to comma-separated string parsing
- **Empty arrays**: Returns appropriate fallback values

## Performance Considerations

- Random selection adds minimal overhead
- Arrays are cached in variables for reuse
- JSON parsing is optimized for common cases
- Fallback mechanisms ensure test stability

## Troubleshooting

### Common Issues

1. **Array not found**: Ensure the array is extracted before use
2. **Invalid JSON**: Check that the JSONPath expression returns valid arrays
3. **Empty results**: Add fallback values for empty arrays
4. **Type errors**: Ensure arrays contain compatible data types

### Debug Tips

- Use logging to see extracted arrays: `self.logger.info(f'Extracted array {var_name} with {len(array)} items')`
- Check variable values in the generated script
- Verify JSONPath expressions return expected data
- Test with smaller datasets first

## Advanced Usage

### Custom Random Functions
You can extend the framework with custom random functions:

```python
def _custom_random_function(self, text):
    # Add your custom random logic here
    pass
```

### Random Seeds
For reproducible tests, you can set random seeds:

```python
import random
random.seed(42)  # For reproducible results
```

### Weighted Random Selection
For more sophisticated scenarios, consider implementing weighted random selection based on business rules.

---

This guide covers all the random selection features available in the Locust AI Agent framework. Use these features to create more dynamic, realistic, and comprehensive test scenarios. 