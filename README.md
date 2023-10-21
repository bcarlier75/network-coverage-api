# Installation

Clone this repository:

```
git clone https://github.com/bcarlier75/network-coverage-api.git
```

I recommand to use python 3.11.0 to run this project and poetry to install the required packages.

Poetry docs -> https://python-poetry.org/docs/#installation 

```
cd src
poetry install
```

# Usage

## 1. Create an enriched network coverage csv file
Run the following commands to enrich the csv file in data/raw folder by adding GPS
coordinates, city and operator name to it. This new file will be used by the API to retrieve the
network coverage for each operator.

The file will be exported to data/result folder.

```
cd src
poetry shell
python scripts/enrich_data.py
```

## 2. Launch server
Make sure your virtual environment is well initialized and the necessary packages are installed.

```
uvicorn main:app --reload
```


# Run test

```
python -m pytest
```