from fastapi.testclient import TestClient
from unittest import TestCase

from main import app


class TestGetNetworkCoverage(TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        return super().setUp()

    def test_get_network_coverage_no_address(self):
        response = self.client.get("/get_network_coverage")
        expected_json_result = {
            "detail": [
                {
                    "type": "missing",
                    "loc": ["query", "address"],
                    "msg": "Field required",
                    "input": None,
                    "url": "https://errors.pydantic.dev/2.4/v/missing",
                }
            ]
        }

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json(), expected_json_result)

    def test_get_network_coverage_address_too_short(self):
        response = self.client.get("/get_network_coverage?address=12")
        expected_json_result = {
            "detail": [
                {
                    "type": "string_too_short",
                    "loc": ["query", "address"],
                    "msg": "String should have at least 3 characters",
                    "input": "12",
                    "ctx": {"min_length": 3},
                    "url": "https://errors.pydantic.dev/2.4/v/string_too_short",
                }
            ]
        }

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json(), expected_json_result)

    def test_get_network_coverage_address_too_long(self):
        address = (
            "qwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiop"
            "qwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiop"
            "qwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiop"
        )
        response = self.client.get(f"/get_network_coverage?address={address}")
        expected_json_result = {
            "detail": [
                {
                    "type": "string_too_long",
                    "loc": ["query", "address"],
                    "msg": "String should have at most 200 characters",
                    "input": "qwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiop",
                    "ctx": {"max_length": 200},
                    "url": "https://errors.pydantic.dev/2.4/v/string_too_long",
                }
            ]
        }

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json(), expected_json_result)

    def test_get_network_coverage_address_invalid(self):
        response = self.client.get(f"/get_network_coverage?address=123~!")
        expected_json_result = {
            "detail": [
                {
                    "type": "string_pattern_mismatch",
                    "loc": ["query", "address"],
                    "msg": "String should match pattern '^[a-zA-Z0-9 ]*$'",
                    "input": "123~!",
                    "ctx": {"pattern": "^[a-zA-Z0-9 ]*$"},
                    "url": "https://errors.pydantic.dev/2.4/v/string_pattern_mismatch",
                }
            ]
        }

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json(), expected_json_result)

    def test_get_network_coverage_valid(self):
        response = self.client.get(
            f"/get_network_coverage?address=123+rue+des+pyrenees+paris"
        )

        expected_json_result = {
            "Bouygues Telecom": {"2G": True, "3G": True, "4G": True},
            "Free mobile": {"2G": False, "3G": True, "4G": True},
            "Orange": {"2G": True, "3G": True, "4G": True},
            "SFR": {"2G": True, "3G": True, "4G": True},
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_json_result)
