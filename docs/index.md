# NEON Utilities Python

Welcome to the documentation for the NEON Utilities Python package, a collection of tools designed to help you access, download, and process data from the [National Ecological Observatory Network (NEON)](https://www.neonscience.org/).

## About NEON

The National Ecological Observatory Network (NEON) is a continental-scale ecological observation facility sponsored by the National Science Foundation and operated by Battelle. NEON collects and provides open data from 81 field sites across the United States that characterize and quantify how our nation's ecosystems are changing. The data collected by NEON enable a better understanding and more accurate forecasting of how ecosystems are responding to land use changes and climate change.

## Package Overview

This Python package provides functions that make it easier to download and work with NEON data. The tools fall into several categories:

### Tabular Data Functions

- **`zips_by_product()`**: Download zip files for a specified data product
- **`load_by_product()`**: Download and load data directly into memory  
- **`stack_by_table()`**: Stack downloaded data into a single file for each data table

### AOP (Remote Sensing) Data Functions

- **`by_file_aop()`**: Download all files for a given AOP (Airborne Observation Platform) data product
- **`by_tile_aop()`**: Download AOP files for specific geographic tiles 
- **`get_aop_tile_extents()`**: Get the tile boundaries for available AOP data
- **`list_available_dates()`**: List dates for which data are available

### Metadata Functions

- **`get_citation()`**: Get citation information for NEON data
- **`get_issue_log()`**: Get the issue log for a data product

### Data Processing Functions

- **`read_table_neon()`**: Read NEON data tables with the correct data types
- **`unzip_and_stack`**: Helper functions for processing downloaded data

## Getting Started

To get started with the NEON Utilities Python package:

1. [Install the package](getting-started/installation.md)
2. [Set up an API token](getting-started/api-token.md) (optional but recommended)
3. Follow the [basic usage guide](getting-started/basic-usage.md)

## Example Usage

```python
from neon_utilities import zips_by_product, stack_by_table

# Download bird data from Harvard Forest in 2019
zips_by_product(
    dpid="DP1.10003.001",  # Breeding landbird point counts
    site="HARV",           # Harvard Forest
    startdate="2019-01",   
    enddate="2019-12",
    savepath="./data"
)

# Stack the downloaded data
bird_data = stack_by_table(
    filepath="./data/filesToStack10003", 
    savepath="envt"
)

# Access the stacked data
bird_counts = bird_data["brd_countdata"]
print(bird_counts.head())
```

## Citation

Please cite both the NEON data product and the NEON Utilities package when you use these tools:

```
National Ecological Observatory Network. 2024. NEON Utilities Python: Tools to download and work with NEON data, Python version x.x.x. https://github.com/neonscience/neon-utilities-python
```

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/neonscience/neon-utilities-python/blob/main/LICENSE) file for details.
