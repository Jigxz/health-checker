#!/usr/bin/env python3
"""
Example usage script for Spring Actuator Checker
Demonstrates how to use the SpringActuatorChecker class programmatically
"""

import sys
import os
import json

# Add the current directory to the path so we can import our module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from spring_actuator_checker import SpringActuatorChecker


def example_basic_health_check():
    """Example: Basic deployment health check"""
    print("=== Example 1: Basic Deployment Health Check ===")

    # Initialize the checker
    checker = SpringActuatorChecker(
        base_url="https://httpbin.org",  # Using httpbin.org for demo (has no actuator endpoints)
        timeout=10,
        verify_ssl=True
    )

    # Check deployment status (this will fail since httpbin doesn't have actuator endpoints)
    # In real usage, replace with your Spring Boot application URL
    try:
        module_status = checker.check_deployment_status("demo-module")
        print(f"Module: {module_status.module_name}")
        print(f"Status: {module_status.deployment_status}")
        print(f"Overall: {module_status.overall_status}")
    except Exception as e:
        print(f"Expected error (no actuator endpoints): {e}")

    print()


def example_custom_api_check():
    """Example: Custom API endpoint checking"""
    print("=== Example 2: Custom API Endpoint Check ===")

    checker = SpringActuatorChecker(
        base_url="https://httpbin.org",
        timeout=10,
        verify_ssl=True
    )

    # Test a simple GET endpoint
    result = checker.check_custom_api(
        endpoint="/get",
        method="GET",
        expected_status=200
    )

    print(f"Endpoint: {result.endpoint}")
    print(f"Status Code: {result.status_code}")
    print(f"Success: {result.success}")
    print(f"Response Time: {result.response_time:.2f}s")

    if result.response_body:
        print(f"Response Keys: {list(result.response_body.keys())}")

    print()


def example_api_with_data():
    """Example: API check with request data"""
    print("=== Example 3: API Check with Request Data ===")

    checker = SpringActuatorChecker(
        base_url="https://httpbin.org",
        timeout=10,
        verify_ssl=True
    )

    # Test a POST endpoint with data
    test_data = {
        "name": "Spring Boot App",
        "version": "2.7.0",
        "status": "running"
    }

    result = checker.check_custom_api(
        endpoint="/post",
        method="POST",
        json_data=test_data,
        expected_status=200
    )

    print(f"Endpoint: {result.endpoint}")
    print(f"Method: {result.method}")
    print(f"Status Code: {result.status_code}")
    print(f"Success: {result.success}")
    print(f"Response Time: {result.response_time:.2f}s")

    if result.response_body:
        # Show that the request data was received
        received_data = result.response_body.get("json")
        if received_data:
            print(f"Request data received: {received_data}")

    print()


def example_contract_validation():
    """Example: Request/Response contract validation"""
    print("=== Example 4: Contract Validation ===")

    checker = SpringActuatorChecker(
        base_url="https://httpbin.org",
        timeout=10,
        verify_ssl=True
    )

    # Define expected response schema
    expected_schema = {
        "url": "str",
        "headers": "dict",
        "origin": "str"
    }

    # Test contract validation
    contract_result = checker.validate_request_response_contract(
        endpoint="/get",
        method="GET",
        expected_response_schema=expected_schema
    )

    print(f"Contract Valid: {contract_result['contract_valid']}")
    print(f"Errors: {contract_result['errors']}")

    if contract_result['contract_valid']:
        print("✅ API response matches expected contract!")
    else:
        print("❌ API response doesn't match expected contract")

    print()


def example_error_handling():
    """Example: Error handling demonstration"""
    print("=== Example 5: Error Handling ===")

    checker = SpringActuatorChecker(
        base_url="https://nonexistent-domain-12345.com",
        timeout=5,
        verify_ssl=True
    )

    # Try to check a non-existent endpoint
    result = checker.check_custom_api(
        endpoint="/test",
        method="GET",
        expected_status=200
    )

    print(f"Endpoint: {result.endpoint}")
    print(f"Status Code: {result.status_code}")
    print(f"Success: {result.success}")
    print(f"Error: {result.error_message}")

    print()


def example_cli_simulation():
    """Example: Simulating command line usage"""
    print("=== Example 6: CLI Usage Simulation ===")

    # Simulate command line arguments
    class Args:
        def __init__(self):
            self.url = "https://httpbin.org"
            self.module = "example-service"
            self.timeout = 10
            self.no_ssl_verify = False
            self.api_endpoint = "/get"
            self.api_method = "GET"
            self.api_data = None
            self.verbose = True

    args = Args()

    # Initialize checker
    checker = SpringActuatorChecker(
        base_url=args.url,
        timeout=args.timeout,
        verify_ssl=not args.no_ssl_verify
    )

    print(f"Checking deployment status for module: {args.module}")

    # Run deployment check
    module_status = checker.check_deployment_status(args.module)

    print(f"Module: {module_status.module_name}")
    print(f"Overall Status: {module_status.overall_status}")
    print(f"Deployment Status: {module_status.deployment_status}")

    # Check additional API if provided
    if args.api_endpoint:
        print(f"\nChecking additional API: {args.api_endpoint}")
        api_result = checker.check_custom_api(
            args.api_endpoint,
            args.api_method,
            json_data=json.loads(args.api_data) if args.api_data else None
        )

        print(f"API Status Code: {api_result.status_code}")
        print(f"API Success: {api_result.success}")
        print(f"API Response Time: {api_result.response_time:.2f}s")

    print()


def main():
    """Run all examples"""
    print("Spring Actuator Checker - Example Usage")
    print("=" * 50)
    print()

    try:
        example_basic_health_check()
        example_custom_api_check()
        example_api_with_data()
        example_contract_validation()
        example_error_handling()
        example_cli_simulation()

        print("✅ All examples completed successfully!")

    except Exception as e:
        print(f"❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
