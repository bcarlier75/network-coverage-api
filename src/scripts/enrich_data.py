import pandas as pd
import pyproj
from pyproj import Transformer
import requests
from io import BytesIO

LAMBERT93_PROJ_PARAM = "+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"
WSG84_PROJ_PARAM = "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"

PATH_TO_FILE_TO_REVERSE = f"data/result/file_to_reverse.csv"
REVERSE_CSV_URL = "https://api-adresse.data.gouv.fr/reverse/csv/"

BASE_COVERAGE_FILE = "2018_01_Sites_mobiles_2G_3G_4G_France_metropolitaine_L93.csv"


def get_lambert93_to_gps_transformer() -> Transformer:
    """Get Lambert 93 to WSG 84 (GPS) transformer.

    Returns
    -------
    Transformer
        Lambert 93 to WSG 84 (GPS) transformer.
    """
    lambert = pyproj.Proj(LAMBERT93_PROJ_PARAM)
    wgs84 = pyproj.Proj(WSG84_PROJ_PARAM)
    return Transformer.from_proj(lambert, wgs84)


def add_gps_coordinates_to_network_coverage_df(
    network_coverage_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Use a pyproj Tranformer to convert Lambert 93 coordinates to WSG 84 coordinates.

    Parameters
    ----------
    network_coverage_df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
    """
    # Initiate transformer
    transformer = get_lambert93_to_gps_transformer()

    # Tranform each lambert93 coordinates to WSG 84 (GPS) coordinates
    lon, lat = transformer.transform(
        network_coverage_df["x"].values, network_coverage_df["y"].values
    )

    # Assign GPS coordinates to network coverage DataFrame
    network_coverage_df = network_coverage_df.assign(
        **{
            "lon": lon,
            "lat": lat,
        }
    )

    return network_coverage_df


def add_citycode_to_network_coverage_df(
    network_coverage_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Use the reverse csv API from data.gouv to retrieve the citycode from GPS coordinates
    (longitude and latitude, respectively lon and lat).

    Parameters
    ----------
    network_coverage_df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
    """
    # Export file to reverse to result folder
    network_coverage_df[["lon", "lat"]].to_csv(PATH_TO_FILE_TO_REVERSE, index=False)
    files = {"data": open(PATH_TO_FILE_TO_REVERSE, "rb")}

    # Call reverse csv api and assign result_citycode values to network coverage DataFrame
    print(f"Calling {REVERSE_CSV_URL}, this might take a few seconds ...")
    reverse_response = requests.post(REVERSE_CSV_URL, files=files)
    reversed_df = pd.read_csv(BytesIO(reverse_response.content))

    # Format citycode to have a 5 digit number as a string or an empty string
    citycodes = (
        reversed_df["result_citycode"]
        .fillna("")
        .astype(str)
        .apply(lambda v: v.replace(".0", ""))
        .str.zfill(5)
        .replace("00000", "")
    )

    network_coverage_df = network_coverage_df.assign(**{"citycode": citycodes})

    return network_coverage_df


def add_operator_name_to_network_coverage(
    network_coverage_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Use a mobile network code files exported from Wikipedia to extract the operator name from
    MCC and MNC codes combined.

    Parameters
    ----------
    network_coverage_df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
    """
    # Compute mapping: operator code (MCC + MNC) -> operator name
    mobile_network_code_df = pd.read_csv(
        "data/external/mobile_network_code.csv"
    ).assign(
        **{
            "operator_code": lambda df: df["MCC"].astype(str)
            + df["MNC"].astype(str).str.zfill(2)
        }
    )
    operator_code_to_operator_name = mobile_network_code_df.set_index("operator_code")[
        "Opérateur"
    ]

    # Assign operator name to network coverage DataFrame
    network_coverage_df = network_coverage_df.assign(
        **{
            "operator_name": lambda df: df["Operateur"]
            .astype(str)
            .map(operator_code_to_operator_name)
            .fillna("")
        }
    )

    return network_coverage_df


# 1 - Read base coverage file from raw folder
# 2 - Enrich it with GPS coordinates (lon and lat)
# 3 - Enrich it with citycode
# 4 - Enrich it with operator name
# 5 - Export it for further use

network_coverage_df = (
    pd.read_csv(f"data/raw/{BASE_COVERAGE_FILE}", sep=";")
    .pipe(add_gps_coordinates_to_network_coverage_df)
    .pipe(add_citycode_to_network_coverage_df)
    .pipe(add_operator_name_to_network_coverage)
    .to_csv("data/result/enriched_network_coverage.csv", index=False)
)
