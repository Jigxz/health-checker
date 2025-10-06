# Spring Actuator API Checker

A comprehensive Python tool to check Spring Boot application deployment status, API health, and request/response contracts.

## Features

- **Spring Actuator Health Check**: Validates `/actuator/health` endpoint
- **Spring Actuator Info Check**: Validates `/actuator/info` endpoint
- **Custom API Testing**: Test any API endpoint with configurable HTTP methods
- **Deployment Status Validation**: Comprehensive deployment health assessment
- **Request/Response Contract Validation**: Validate API contracts and response schemas
- **Comprehensive Logging**: Detailed logging to both file and console
- **Command Line Interface**: Easy-to-use CLI with multiple options
- **SSL Support**: Configurable SSL certificate verification

## Installation

1. Ensure you have Python 3.7+ installed
2. Install required dependencies:

```bash
pip install requests
```

## Usage

### Basic Deployment Check

```bash
python spring_actuator_checker.py --url https://your-app.com --module your-module-name
```

### Advanced Usage with Custom API Testing

```bash
python spring_actuator_checker.py \
    --url https://your-app.com \
    --module user-service \
    --api-endpoint /api/users \
    --api-method GET \
    --timeout 60 \
    --verbose
```

### Testing API with Request Data

```bash
python spring_actuator_checker.py \
    --url https://your-app.com \
    --module user-service \
    --api-endpoint /api/users \
    --api-method POST \
    --api-data '{"name": "John Doe", "email": "john@example.com"}'
```

### Disable SSL Verification (for testing environments)

```bash
python spring_actuator_checker.py \
    --url https://localhost:8080 \
    --module local-service \
    --no-ssl-verify
```

## Command Line Options

| Option | Description | Required | Default |
|--------|-------------|----------|---------|
| `--url` | Base URL of the Spring Boot application | Yes | - |
| `--module` | Name of the module to check | Yes | - |
| `--timeout` | Request timeout in seconds | No | 30 |
| `--no-ssl-verify` | Disable SSL certificate verification | No | False |
| `--api-endpoint` | Additional API endpoint to check | No | - |
| `--api-method` | HTTP method for additional API check | No | GET |
| `--api-data` | JSON data for API request (as string) | No | - |
| `--verbose, -v` | Enable verbose logging | No | False |

## Output Example

```
============================================================
DEPLOYMENT STATUS CHECK RESULTS
============================================================
Module: user-service
Overall Status: HEALTHY
Deployment Status: HEALTHY
Timestamp: 2025-01-06 10:45:30.123456

Actuator Health Details:
{
  "status": "UP",
  "components": {
    "diskSpace": {
      "status": "UP",
      "details": {
        "total": 1073741824,
        "free": 536870912,
        "threshold": 10485760
      }
    },
    "ping": {
      "status": "UP"
    }
  }
}

----------------------------------------
ADDITIONAL API CHECK
----------------------------------------
Endpoint: https://your-app.com/api/users
Method: GET
Status Code: 200
Response Time: 0.45s
Success: True
Response Body: {
  "users": [
    {"id": 1, "name": "John Doe"},
    {"id": 2, "name": "Jane Smith"}
  ]
}

============================================================
```

## Exit Codes

- `0`: Deployment is HEALTHY
- `1`: Deployment is DOWN, DEGRADED, or UNKNOWN

## Programmatic Usage

You can also use the `SpringActuatorChecker` class in your own Python code:

```python
from spring_actuator_checker import SpringActuatorChecker

# Initialize checker
checker = SpringActuatorChecker(
    base_url="https://your-app.com",
    timeout=30,
    verify_ssl=True
)

# Check deployment status
module_status = checker.check_deployment_status("user-service")
print(f"Status: {module_status.deployment_status}")

# Check custom API
api_result = checker.check_custom_api(
    endpoint="/api/users",
    method="GET",
    expected_status=200
)
print(f"API Success: {api_result.success}")

# Validate contract
contract_result = checker.validate_request_response_contract(
    endpoint="/api/users",
    method="GET",
    expected_response_schema={
        "users": "list",
        "totalCount": "int"
    }
)
print(f"Contract Valid: {contract_result['contract_valid']}")
```

## Health Status Levels

- **HEALTHY**: Both actuator health and info endpoints return 200 OK
- **DEGRADED**: Only actuator health endpoint returns 200 OK
- **DOWN**: Actuator health endpoint is not accessible or returns non-200 status
- **UNKNOWN**: Unable to determine status due to errors

## Logging

The tool creates a log file `spring_actuator_checker.log` with detailed information about all checks performed. Use the `--verbose` flag for additional debug information.

## Error Handling

The tool handles various error scenarios gracefully:

- Network timeouts
- SSL certificate errors
- Invalid JSON responses
- HTTP errors (4xx, 5xx)
- Connection failures

All errors are logged with detailed information and included in the results.

## Security Considerations

- Use `--no-ssl-verify` only in development/testing environments
- The tool sends requests with a custom User-Agent header for identification
- All requests include standard headers for Spring Boot compatibility
- Sensitive data in logs should be reviewed before sharing

## Troubleshooting

### Common Issues

1. **SSL Certificate Errors**: Use `--no-ssl-verify` for self-signed certificates in development
2. **Timeout Errors**: Increase `--timeout` value for slow networks
3. **Module Not Accessible**: Verify the base URL and actuator endpoints are accessible
4. **Invalid JSON in Response**: The tool will log warnings but continue processing

### Debug Mode

Use the `--verbose` flag to enable detailed logging for troubleshooting:

```bash
python spring_actuator_checker.py --url https://your-app.com --module test --verbose
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all existing tests pass
5. Submit a pull request

## License

This project is open source and available under the MIT License.
