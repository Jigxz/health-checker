#!/usr/bin/env python3
"""
Spring Actuator API Checker
A comprehensive tool to check Spring Boot application deployment status,
API health, and request/response contracts.
"""

import requests
import json
import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import argparse
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('spring_actuator_checker.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class APICheckResult:
    """Data class to store API check results"""
    endpoint: str
    method: str
    status_code: int
    response_time: float
    success: bool
    response_body: Optional[Dict] = None
    error_message: Optional[str] = None

@dataclass
class ModuleHealthStatus:
    """Data class to store module health status"""
    module_name: str
    overall_status: str
    actuator_health: Dict[str, Any]
    api_checks: List[APICheckResult]
    deployment_status: str
    timestamp: datetime

class SpringActuatorChecker:
    """Main class for checking Spring Boot application health and APIs"""

    def __init__(self, base_url: str, timeout: int = 30, verify_ssl: bool = True):
        """
        Initialize the checker with base URL and configuration

        Args:
            base_url: Base URL of the Spring Boot application
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.session = requests.Session()

        # Common headers for Spring Boot applications
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Spring-Actuator-Checker/1.0'
        })

    def check_actuator_health(self) -> APICheckResult:
        """
        Check the Spring Boot Actuator health endpoint

        Returns:
            APICheckResult with health check details
        """
        endpoint = f"{self.base_url}/actuator/health"
        logger.info(f"Checking actuator health endpoint: {endpoint}")

        start_time = time.time()
        try:
            response = self.session.get(
                endpoint,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response_time = time.time() - start_time

            success = response.status_code == 200
            result = APICheckResult(
                endpoint=endpoint,
                method="GET",
                status_code=response.status_code,
                response_time=response_time,
                success=success,
                response_body=response.json() if success else None,
                error_message=None if success else f"HTTP {response.status_code}: {response.text}"
            )

            logger.info(f"Health check completed - Status: {response.status_code}, Time: {response_time:.2f}s")
            return result

        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            logger.error(f"Health check failed: {str(e)}")
            return APICheckResult(
                endpoint=endpoint,
                method="GET",
                status_code=0,
                response_time=response_time,
                success=False,
                error_message=str(e)
            )

    def check_actuator_info(self) -> APICheckResult:
        """
        Check the Spring Boot Actuator info endpoint

        Returns:
            APICheckResult with info details
        """
        endpoint = f"{self.base_url}/actuator/info"
        logger.info(f"Checking actuator info endpoint: {endpoint}")

        start_time = time.time()
        try:
            response = self.session.get(
                endpoint,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response_time = time.time() - start_time

            success = response.status_code == 200
            result = APICheckResult(
                endpoint=endpoint,
                method="GET",
                status_code=response.status_code,
                response_time=response_time,
                success=success,
                response_body=response.json() if success else None,
                error_message=None if success else f"HTTP {response.status_code}: {response.text}"
            )

            logger.info(f"Info check completed - Status: {response.status_code}, Time: {response_time:.2f}s")
            return result

        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            logger.error(f"Info check failed: {str(e)}")
            return APICheckResult(
                endpoint=endpoint,
                method="GET",
                status_code=0,
                response_time=response_time,
                success=False,
                error_message=str(e)
            )

    def check_custom_api(self, endpoint: str, method: str = "GET",
                        headers: Optional[Dict[str, str]] = None,
                        json_data: Optional[Dict] = None,
                        expected_status: int = 200) -> APICheckResult:
        """
        Check a custom API endpoint

        Args:
            endpoint: API endpoint (relative to base_url)
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            headers: Additional headers to send
            json_data: JSON data to send in request body
            expected_status: Expected HTTP status code

        Returns:
            APICheckResult with API check details
        """
        full_url = f"{self.base_url}{endpoint}" if not endpoint.startswith('http') else endpoint
        logger.info(f"Checking API endpoint: {full_url} ({method})")

        start_time = time.time()

        # Prepare request headers
        request_headers = {}
        if headers:
            request_headers.update(headers)

        try:
            response = self.session.request(
                method=method.upper(),
                url=full_url,
                headers=request_headers,
                json=json_data,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response_time = time.time() - start_time

            # Check if response status matches expected
            success = response.status_code == expected_status

            # Try to parse JSON response
            response_body = None
            try:
                response_body = response.json()
            except json.JSONDecodeError:
                logger.warning(f"Response is not JSON: {response.text[:200]}...")

            result = APICheckResult(
                endpoint=full_url,
                method=method.upper(),
                status_code=response.status_code,
                response_time=response_time,
                success=success,
                response_body=response_body,
                error_message=None if success else f"Expected {expected_status}, got {response.status_code}"
            )

            logger.info(f"API check completed - Status: {response.status_code}, Expected: {expected_status}, Time: {response_time:.2f}s")
            return result

        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            logger.error(f"API check failed: {str(e)}")
            return APICheckResult(
                endpoint=full_url,
                method=method.upper(),
                status_code=0,
                response_time=response_time,
                success=False,
                error_message=str(e)
            )

    def check_deployment_status(self, module_name: str) -> ModuleHealthStatus:
        """
        Comprehensive deployment status check for a module

        Args:
            module_name: Name of the module being checked

        Returns:
            ModuleHealthStatus with complete health information
        """
        logger.info(f"Starting comprehensive deployment check for module: {module_name}")

        # Check actuator health
        health_result = self.check_actuator_health()

        # Check actuator info
        info_result = self.check_actuator_info()

        # Determine overall deployment status
        deployment_status = "UNKNOWN"
        if health_result.success and info_result.success:
            deployment_status = "HEALTHY"
        elif health_result.success:
            deployment_status = "DEGRADED"
        else:
            deployment_status = "DOWN"

        # Create module health status
        module_status = ModuleHealthStatus(
            module_name=module_name,
            overall_status=deployment_status,
            actuator_health=health_result.response_body or {},
            api_checks=[health_result, info_result],
            deployment_status=deployment_status,
            timestamp=datetime.now()
        )

        logger.info(f"Deployment check completed for {module_name} - Status: {deployment_status}")
        return module_status

    def validate_request_response_contract(self, endpoint: str, method: str = "GET",
                                         request_data: Optional[Dict] = None,
                                         expected_response_schema: Optional[Dict] = None,
                                         headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Validate that API request/response follows expected contract

        Args:
            endpoint: API endpoint to test
            method: HTTP method
            request_data: Expected request structure
            expected_response_schema: Expected response structure
            headers: Additional headers to send with the request

        Returns:
            Dictionary with contract validation results
        """
        logger.info(f"Validating contract for {method} {endpoint}")

        # Make the API call
        api_result = self.check_custom_api(endpoint, method, headers=headers, json_data=request_data)

        contract_result = {
            "endpoint": endpoint,
            "method": method,
            "contract_valid": False,
            "request_validation": {},
            "response_validation": {},
            "errors": []
        }

        # Validate response status
        if not api_result.success:
            contract_result["errors"].append(f"API call failed: {api_result.error_message}")
            return contract_result

        # Basic response validation
        if expected_response_schema:
            response_body = api_result.response_body

            # Check if response has expected structure
            for key, expected_type in expected_response_schema.items():
                if key not in response_body:
                    contract_result["errors"].append(f"Missing expected field: {key}")
                else:
                    actual_type = type(response_body[key]).__name__
                    if actual_type != expected_type:
                        contract_result["errors"].append(
                            f"Type mismatch for {key}: expected {expected_type}, got {actual_type}"
                        )

        # If no errors, contract is valid
        contract_result["contract_valid"] = len(contract_result["errors"]) == 0

        logger.info(f"Contract validation completed - Valid: {contract_result['contract_valid']}")
        return contract_result

def main():
    """Main function to run the Spring Actuator checker"""
    parser = argparse.ArgumentParser(description="Spring Boot Actuator API Checker")
    parser.add_argument("--url", required=True, help="Base URL of the Spring Boot application")
    parser.add_argument("--module", required=True, help="Name of the module to check")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")
    parser.add_argument("--no-ssl-verify", action="store_true", help="Disable SSL certificate verification")
    parser.add_argument("--api-endpoint", help="Additional API endpoint to check")
    parser.add_argument("--api-method", default="GET", help="HTTP method for additional API check")
    parser.add_argument("--api-data", help="JSON data for API request (as string)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Parse JSON data if provided
    json_data = None
    if args.api_data:
        try:
            json_data = json.loads(args.api_data)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON data: {e}")
            sys.exit(1)

    # Initialize checker
    checker = SpringActuatorChecker(
        base_url=args.url,
        timeout=args.timeout,
        verify_ssl=not args.no_ssl_verify
    )

    # Run comprehensive deployment check
    logger.info(f"Starting deployment check for module: {args.module}")
    module_status = checker.check_deployment_status(args.module)

    # Print results
    print(f"\n{'='*60}")
    print(f"DEPLOYMENT STATUS CHECK RESULTS")
    print(f"{'='*60}")
    print(f"Module: {module_status.module_name}")
    print(f"Overall Status: {module_status.overall_status}")
    print(f"Deployment Status: {module_status.deployment_status}")
    print(f"Timestamp: {module_status.timestamp}")
    print(f"\nActuator Health Details:")
    print(json.dumps(module_status.actuator_health, indent=2))

    # Check additional API if provided
    if args.api_endpoint:
        print(f"\n{'-'*40}")
        print(f"ADDITIONAL API CHECK")
        print(f"{'-'*40}")

        api_result = checker.check_custom_api(
            args.api_endpoint,
            args.api_method,
            json_data=json_data
        )

        print(f"Endpoint: {api_result.endpoint}")
        print(f"Method: {api_result.method}")
        print(f"Status Code: {api_result.status_code}")
        print(f"Response Time: {api_result.response_time:.2f}s")
        print(f"Success: {api_result.success}")

        if api_result.response_body:
            print(f"Response Body: {json.dumps(api_result.response_body, indent=2)}")

        if api_result.error_message:
            print(f"Error: {api_result.error_message}")

    print(f"\n{'='*60}")

    # Exit with appropriate code
    if module_status.deployment_status == "HEALTHY":
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
