from unittest import TestCase
from dependencies import compute_city_network_coverage, get_matching_citycode
import pandas as pd


class TestComputeCityNetworkCoverage(TestCase):
    def test_city_is_none(self):
        network_coverage_df = pd.DataFrame(
            columns=["operator_name", "citycode", "2G", "3G", "4G"]
        )
        citycode = None

        result = compute_city_network_coverage(network_coverage_df, citycode)
        expected_result = {}
        self.assertDictEqual(result, expected_result)

    def test_valid_citycode_empty_network_coverage(self):
        network_coverage_df = pd.DataFrame(
            columns=["operator_name", "citycode", "2G", "3G", "4G"]
        )
        citycode = "Pornic"

        result = compute_city_network_coverage(network_coverage_df, citycode)
        expected_result = {}
        self.assertDictEqual(result, expected_result)

    def test_no_network_coverage_for_city(self):
        network_coverage_df = pd.DataFrame(
            {
                "operator_name": ["Orange", "Orange", "Orange"],
                "citycode": [12345, 44156, 54421],
                "2G": [1, 1, 1],
                "3G": [1, 1, 1],
                "4G": [1, 1, 1],
            }
        )
        citycode = 98444

        result = compute_city_network_coverage(network_coverage_df, citycode)
        expected_result = {}
        self.assertDictEqual(result, expected_result)

    def test_has_network_coverage_for_city(self):
        network_coverage_df = pd.DataFrame(
            {
                "operator_name": ["Orange", "Orange", "Orange", "SFR"],
                "citycode": [12345, 44156, 54421, 54421],
                "2G": [1, 1, 1, 0],
                "3G": [1, 1, 1, 1],
                "4G": [1, 1, 1, 1],
            }
        )
        citycode = 54421

        result = compute_city_network_coverage(network_coverage_df, citycode)
        expected_result = {
            "Orange": {"2G": True, "3G": True, "4G": True},
            "SFR": {"2G": False, "3G": True, "4G": True},
        }
        self.assertDictEqual(result, expected_result)


class TestGetMatchingCity(TestCase):
    def test_valid(self):
        response_data = {
            "type": "FeatureCollection",
            "version": "draft",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-1.292128, 46.979292],
                    },
                    "properties": {
                        "label": "Montaigu-Vendée",
                        "score": 0.9492436363636363,
                        "id": "85146",
                        "type": "municipality",
                        "name": "Montaigu-Vendée",
                        "postcode": "85600",
                        "citycode": "85146",
                        "x": 373891.86,
                        "y": 6662096.09,
                        "population": 20578,
                        "city": "Montaigu-Vendée",
                        "context": "85, Vendée, Pays de la Loire",
                        "importance": 0.44168,
                        "municipality": "Montaigu-Vendée",
                    },
                }
            ],
            "attribution": "BAN",
            "licence": "ETALAB-2.0",
            "query": "montaigu vendee",
            "limit": 5,
        }

        result = get_matching_citycode(response_data)
        expected_result = "85146"
        self.assertEqual(result, expected_result)

    def test_none_with_features_key(self):
        response_data = {
            "type": "FeatureCollection",
            "version": "draft",
            "features": [],
            "attribution": "BAN",
            "licence": "ETALAB-2.0",
            "query": "okaido",
            "limit": 5,
        }

        result = get_matching_citycode(response_data)
        self.assertIsNone(result)

    def test_none_without_features_key(self):
        response_data = {
            "type": "FeatureCollection",
            "version": "draft",
            "attribution": "BAN",
            "licence": "ETALAB-2.0",
            "query": "okaido",
            "limit": 5,
        }

        result = get_matching_citycode(response_data)
        self.assertIsNone(result)
