from fastapi import Query, HTTPException
from typing import Annotated
from dependencies import (
    fetch_data_gouv_search_api,
    get_matching_citycode,
    compute_city_network_coverage,
    DATA_GOUV_BASE_API_URL,
)
from main import app, network_coverage_df
from fastapi import status


@app.get("/get_network_coverage")
def get_network_coverage(
    address: Annotated[
        str, Query(min_length=3, max_length=200, pattern="^[a-zA-Z0-9 ]*$")
    ]
) -> dict[str, dict[str, bool]]:
    """
    The network coverage of an address is determined by checking the availability of
    operators and their coverage in the city associated with the address.

    Parameters
    ----------
    **address** : str

    Address on which we want to test the network coverage. Should be at least 3 character
    up to 200 characters and start with a letter or a number.

    Returns
    -------
    dict[str, dict[str,bool]]

    Network coverage for the city associated to the address.

    **Example**:

        {
            "Orange": {"2G": true, "3G": true, "4G": false},
            "SFR": {"2G": true, "3G": true, "4G": true}
        }

    Raises
    ------
    HTTPException
    """
    try:
        response = fetch_data_gouv_search_api(address)
        citycode = get_matching_citycode(response.json())
        city_network_coverage = compute_city_network_coverage(
            network_coverage_df, citycode
        )
    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"Error fetching {DATA_GOUV_BASE_API_URL}, got the following exception {exception}"
            ),
        )
    else:
        return city_network_coverage
