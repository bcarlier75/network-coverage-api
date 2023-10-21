import logging
import pandas as pd
import requests

from fastapi import Response

DATA_GOUV_BASE_API_URL = "https://api-adresse.data.gouv.fr"


def fetch_data_gouv_search_api(address: str) -> Response:
    """Search for the address in data.gouv adresse search API.

    Parameters
    ----------
    address : str

    Returns
    -------
    Response
    """
    search_url = f"{DATA_GOUV_BASE_API_URL}/search/?q={address}"
    response = requests.get(search_url)

    return response


def get_matching_citycode(response_data: dict) -> str | None:
    """
    Get the matching citycode (INSEE code) using response data from data.gouv search API.

    Return None if the address was not matched to any citycode.

    Parameters
    ----------
    response_data: dict

    Returns
    -------
    str | None
    """
    if not response_data.get("features"):
        return None
    else:
        properties = response_data.get("features")[0]["properties"]
        citycode, city = properties["citycode"], properties["city"]
        logging.info(f"Looking at network coverage for {city} (Insee code {citycode})")
        return citycode


def compute_city_network_coverage(
    network_coverage_df: pd.DataFrame, citycode: str | None
) -> dict[str, dict[str, bool]]:
    """Determine the network coverage for the requested citycode.

    Parameters
    ----------
    network_coverage_df : pd.DataFrame
    citycode : str | None


    Returns
    -------
    dict[str, dict[str,bool]]
        Citycode network coverage dict with:
        - keys: operator name
        - values: network coverage dict with network(str)->availability(bool)
    """
    if citycode is None:
        return {}

    # Preserve only operator network coverage with matching citycode
    city_network_coverage_df = network_coverage_df[
        network_coverage_df["citycode"] == citycode
    ]

    city_network_coverage = (
        city_network_coverage_df.groupby("operator_name")
        .agg({"2G": any, "3G": any, "4G": any})
        .to_dict(orient="index")
    )

    return city_network_coverage
