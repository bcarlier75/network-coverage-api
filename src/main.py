import logging
from fastapi import FastAPI
import pandas as pd

# Load enriched network coverage file before starting API
network_coverage_df = pd.read_csv(
    "data/result/enriched_network_coverage.csv", dtype={"citycode": str}
)

# Set logging level to INFO
logging.getLogger().setLevel(logging.INFO)

# Load app
app = FastAPI()


@app.get("/")
def get_all_urls():
    url_list = [{"path": route.path, "name": route.name} for route in app.routes]
    return url_list


import router
