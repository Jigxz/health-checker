#!/usr/bin/env python3
"""
Test script for Spring Actuator Checker
Tests the core functionality without requiring a live Spring Boot application
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import sys
import os

# Add the current directory to the path so we can import our module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from spring_actuator_checker import (
    SpringActuatorChecker,
    APICheckResult,
    ModuleHealthStatus
)


class TestSpringActuatorChecker(unittest.TestCase):
    """Test cases for SpringActuatorChecker"""

    def setUp(self):
        """Set up test fixtures"""
        self.base_url = "https://test-app.com"
        self.checker = SpringActuatorChecker(
            base_url=self.base_url,
            timeout=10,
            verify_ssl=False
        )

    def test_initialization(self):
        """Test that the checker initializes correctly"""
        self.assertEqual(self.checker.base_url, self.base_url)
        self.assertEqual(self.checker.timeout, 10)
        self.assertFalse(self.checker.verify_ssl)
        self.assertIsNotNone(self.checker.session)

    @patch('spring_actuator_checker.requests.Session.get')
    def test_check_actuator_health_success(self, mock_get):
        """Test successful actuator health check"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "UP",
            "components": {
                "diskSpace": {"status": "UP"},
                "ping": {"status": "UP"}
            }
        }
        mock_get.return_value = mock_response

        result = self.checker.check_actuator_health()

        # Verify the result
        self.assertTrue(result.success)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.endpoint, f"{self.base_url}/actuator/health")
        self.assertEqual(result.method, "GET")
        self.assertIsNotNone(result.response_body)
        self.assertIsNone(result.error_message)
        self.assertGreaterEqual(result.response_time, 0)

    @patch('spring_actuator_checker.requests.Session.get')
    def test_check_actuator_health_failure(self, mock_get):
        """Test failed actuator health check"""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 503
        mock_response.text = "Service Unavailable"
        mock_get.return_value = mock_response

        result = self.checker.check_actuator_health()

        # Verify the result
        self.assertFalse(result.success)
        self.assertEqual(result.status_code, 503)
        self.assertIsNone(result.response_body)
        self.assertIsNotNone(result.error_message)

    @patch('spring_actuator_checker.requests.Session.get')
    def test_check_actuator_info_success(self, mock_get):
        """Test successful actuator info check"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "app": {
                "name": "test-app",
                "version": "1.0.0",
                "description": "Test application"
            }
        }
        mock_get.return_value = mock_response

        result = self.checker.check_actuator_info()

        # Verify the result
        self.assertTrue(result.success)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.endpoint, f"{self.base_url}/actuator/info")
        self.assertIsNotNone(result.response_body)

    @patch('spring_actuator_checker.requests.Session.request')
    def test_check_custom_api_post_success(self, mock_request):
        """Test successful custom API check with POST method"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 123, "name": "Test User"}
        mock_request.return_value = mock_response

        test_data = {"name": "Test User", "email": "test@example.com"}
        result = self.checker.check_custom_api(
            endpoint="/api/users",
            method="POST",
            json_data=test_data,
            expected_status=201
        )

        # Verify the result
        self.assertTrue(result.success)
        self.assertEqual(result.status_code, 201)
        self.assertEqual(result.method, "POST")
        self.assertEqual(result.endpoint, f"{self.base_url}/api/users")
        self.assertIsNotNone(result.response_body)

        # Verify the request was made correctly
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        self.assertEqual(call_args[1]['method'], 'POST')
        self.assertEqual(call_args[1]['json'], test_data)

    @patch('spring_actuator_checker.requests.Session.request')
    def test_check_custom_api_with_headers(self, mock_request):
        """Test custom API check with additional headers"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "success"}
        mock_request.return_value = mock_response

        custom_headers = {"Authorization": "Bearer token123"}
        result = self.checker.check_custom_api(
            endpoint="/api/protected",
            headers=custom_headers
        )

        # Verify headers were passed correctly
        call_args = mock_request.call_args
        request_headers = call_args[1]['headers']
        self.assertIn("Authorization", request_headers)
        self.assertEqual(request_headers["Authorization"], "Bearer token123")

    def test_deployment_status_healthy(self):
        """Test deployment status when both health and info are successful"""
        # Mock the health and info check methods
        with patch.object(self.checker, 'check_actuator_health') as mock_health, \
             patch.object(self.checker, 'check_actuator_info') as mock_info:

            # Mock successful responses
            health_result = APICheckResult(
                endpoint=f"{self.base_url}/actuator/health",
                method="GET",
                status_code=200,
                response_time=0.1,
                success=True,
                response_body={"status": "UP"}
            )
            info_result = APICheckResult(
                endpoint=f"{self.base_url}/actuator/info",
                method="GET",
                status_code=200,
                response_time=0.1,
                success=True,
                response_body={"app": {"name": "test"}}
            )

            mock_health.return_value = health_result
            mock_info.return_value = info_result

            # Test the deployment status
            module_status = self.checker.check_deployment_status("test-module")

            # Verify results
            self.assertEqual(module_status.module_name, "test-module")
            self.assertEqual(module_status.deployment_status, "HEALTHY")
            self.assertEqual(module_status.overall_status, "HEALTHY")
            self.assertEqual(len(module_status.api_checks), 2)
            self.assertIsNotNone(module_status.timestamp)

    def test_deployment_status_down(self):
        """Test deployment status when health check fails"""
        # Mock the health and info check methods
        with patch.object(self.checker, 'check_actuator_health') as mock_health, \
             patch.object(self.checker, 'check_actuator_info') as mock_info:

            # Mock failed health response
            health_result = APICheckResult(
                endpoint=f"{self.base_url}/actuator/health",
                method="GET",
                status_code=503,
                response_time=0.1,
                success=False,
                error_message="Service Unavailable"
            )
            info_result = APICheckResult(
                endpoint=f"{self.base_url}/actuator/info",
                method="GET",
                status_code=200,
                response_time=0.1,
                success=True,
                response_body={"app": {"name": "test"}}
            )

            mock_health.return_value = health_result
            mock_info.return_value = info_result

            # Test the deployment status
            module_status = self.checker.check_deployment_status("test-module")

            # Verify results
            self.assertEqual(module_status.deployment_status, "DOWN")
            self.assertEqual(module_status.overall_status, "DOWN")

    def test_validate_contract_success(self):
        """Test successful contract validation"""
        # Mock the custom API check
        with patch.object(self.checker, 'check_custom_api') as mock_api:

            # Mock successful API response
            api_result = APICheckResult(
                endpoint=f"{self.base_url}/api/test",
                method="GET",
                status_code=200,
                response_time=0.1,
                success=True,
                response_body={
                    "users": [
                        {"id": 1, "name": "John"},
                        {"id": 2, "name": "Jane"}
                    ],
                    "totalCount": 2
                }
            )
            mock_api.return_value = api_result

            # Define expected schema
            expected_schema = {
                "users": "list",
                "totalCount": "int"
            }

            # Test contract validation
            contract_result = self.checker.validate_request_response_contract(
                endpoint="/api/test",
                expected_response_schema=expected_schema
            )

            # Verify results
            self.assertTrue(contract_result["contract_valid"])
            self.assertEqual(len(contract_result["errors"]), 0)
            self.assertEqual(contract_result["endpoint"], "/api/test")
            self.assertEqual(contract_result["method"], "GET")

    def test_validate_contract_failure(self):
        """Test failed contract validation"""
        # Mock the custom API check
        with patch.object(self.checker, 'check_custom_api') as mock_api:

            # Mock API response missing expected fields
            api_result = APICheckResult(
                endpoint=f"{self.base_url}/api/test",
                method="GET",
                status_code=200,
                response_time=0.1,
                success=True,
                response_body={
                    "users": [
                        {"id": 1, "name": "John"}
                    ]
                    # Missing totalCount field
                }
            )
            mock_api.return_value = api_result

            # Define expected schema
            expected_schema = {
                "users": "list",
                "totalCount": "int"  # This field is missing from response
            }

            # Test contract validation
            contract_result = self.checker.validate_request_response_contract(
                endpoint="/api/test",
                expected_response_schema=expected_schema
            )

            # Verify results
            self.assertFalse(contract_result["contract_valid"])
            self.assertGreater(len(contract_result["errors"]), 0)
            self.assertIn("Missing expected field: totalCount", contract_result["errors"])

    def test_validate_contract_api_failure(self):
        """Test contract validation when API call fails"""
        # Mock the custom API check
        with patch.object(self.checker, 'check_custom_api') as mock_api:

            # Mock failed API response
            api_result = APICheckResult(
                endpoint=f"{self.base_url}/api/test",
                method="GET",
                status_code=500,
                response_time=0.1,
                success=False,
                error_message="Internal Server Error"
            )
            mock_api.return_value = api_result

            # Test contract validation
            contract_result = self.checker.validate_request_response_contract(
                endpoint="/api/test"
            )

            # Verify results
            self.assertFalse(contract_result["contract_valid"])
            self.assertIn("API call failed", contract_result["errors"][0])

    @patch('spring_actuator_checker.requests.Session.request')
    def test_check_custom_api_non_json_response(self, mock_request):
        """Test custom API check with non-JSON response"""
        # Mock response that raises JSON decode error
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Not JSON", "", 0)
        mock_response.text = "<html>Not JSON response</html>"
        mock_request.return_value = mock_response

        result = self.checker.check_custom_api("/api/html-endpoint")

        # Verify the result handles non-JSON gracefully
        self.assertTrue(result.success)
        self.assertEqual(result.status_code, 200)
        self.assertIsNone(result.response_body)  # Should be None for non-JSON


class TestAPICheckResult(unittest.TestCase):
    """Test cases for APICheckResult data class"""

    def test_api_check_result_creation(self):
        """Test APICheckResult can be created with all fields"""
        result = APICheckResult(
            endpoint="https://test.com/api",
            method="GET",
            status_code=200,
            response_time=0.5,
            success=True,
            response_body={"test": "data"},
            error_message=None
        )

        self.assertEqual(result.endpoint, "https://test.com/api")
        self.assertEqual(result.method, "GET")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.response_time, 0.5)
        self.assertTrue(result.success)
        self.assertEqual(result.response_body, {"test": "data"})
        self.assertIsNone(result.error_message)


class TestModuleHealthStatus(unittest.TestCase):
    """Test cases for ModuleHealthStatus data class"""

    def test_module_health_status_creation(self):
        """Test ModuleHealthStatus can be created with all fields"""
        from datetime import datetime

        status = ModuleHealthStatus(
            module_name="test-module",
            overall_status="HEALTHY",
            actuator_health={"status": "UP"},
            api_checks=[],
            deployment_status="HEALTHY",
            timestamp=datetime.now()
        )

        self.assertEqual(status.module_name, "test-module")
        self.assertEqual(status.overall_status, "HEALTHY")
        self.assertEqual(status.deployment_status, "HEALTHY")
        self.assertIsNotNone(status.timestamp)


def run_tests():
    """Run all tests"""
    # Create test suite
    test_classes = [
        TestSpringActuatorChecker,
        TestAPICheckResult,
        TestModuleHealthStatus
    ]

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    if not success:
        sys.exit(1)
