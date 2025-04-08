# Basic Usage

This guide provides an overview of the key functions in the NEON Utilities package and examples of common usage patterns. After reading this guide, you should have a good understanding of how to download and work with NEON data.

## Understanding NEON Data Products

Before diving into the code, it's helpful to understand the structure of NEON data products:

- **Data Product ID (DPID)**: Each NEON data product has a unique identifier in the form `DP#.#####.###` (e.g., `DP1.10003.001`)
- **Data Product Types**:
  - **Observational (OS)**: Data collected by field staff (e.g., bird surveys, vegetation structure)
  - **Instrument (IS)**: Data collected by sensors (e.g., precipitation, temperature)
  - **Airborne Observation Platform (AOP)**: Remote sensing data (e.g., LiDAR, hyperspectral imagery)
- **Sites**: NEON operates 81 field sites across the US, each with a 4-letter code (e.g., `HARV` for Harvard Forest)
- **Data Availability**: Data availability varies by product, site, and time period

## Finding Data Products

You can browse available data products on the [NEON Data Portal](https://data.neonscience.org/data-products/explore) or through API calls.

```python
from neon_utilities.helper_mods.api_helpers import get_api
import pandas as pd

# Get all NEON data products
response = get_api("https://data.neonscience.org/api/v0/products")
products = pd.DataFrame(response.json()['data'])

# Display data products (showing first 5)
print(products[['productCode', 'productName']].head(5))
```

## Key Functions Overview

The NEON Utilities package provides several main functions depending on the type of data you're working with:

### For Tabular Data (OS and IS)

- `zips_by_product()`: Download zip files for a data product
- `load_by_product()`: Download and load data into memory
- `stack_by_table()`: Stack downloaded data into unified tables

### For AOP Data (Remote Sensing)

- `list_available_dates()`: Check dates for which AOP data are available
- `get_aop_tile_extents()`: Get tile boundaries for AOP data
- `by_file_aop()`: Download all files for an AOP product at a site
- `by_tile_aop()`: Download specific tiles for an AOP product

### For Data Processing

- `read_table_neon()`: Read NEON tables with correct data types
- `get_citation()`: Get citation information for data products
- `get_issue_log()`: Get the issue log for a data product

## Working with Tabular Data

### Example 1: Download and Stack Bird Survey Data

To download and work with bird survey data:

```python
from neon_utilities import zips_by_product, stack_by_table

# Download bird survey data for Harvard Forest in 2019
zips_by_product(
    dpid="DP1.10003.001",  # Breeding landbird point counts
    site="HARV",           # Harvard Forest
    startdate="2019-01",   
    enddate="2019-12",
    check_size=True,       # Prompt before downloading
    savepath="./data"      # Directory to save the data
)

# Stack the downloaded data into tables
stack_by_table(
    filepath="./data/filesToStack10003",
    savepath="./data/stacked"
)
```

This creates a directory `./data/stacked/stackedFiles` containing CSV files for each table in the data product.

### Example 2: Load Data Directly into Memory

For interactive analysis, you can load data directly into memory:

```python
from neon_utilities import load_by_product

# Download and load bird survey data
bird_data = load_by_product(
    dpid="DP1.10003.001",  # Breeding landbird point counts
    site="HARV",           # Harvard Forest
    startdate="2019-01",   
    enddate="2019-12"
)

# Access the data tables
bird_counts = bird_data["brd_countdata"]
bird_perpoint = bird_data["brd_perpoint"]

# Print the first few rows of count data
print(bird_counts.head())

# Get information about variables
print(bird_data["variables_10003"][bird_data["variables_10003"]["table"] == "brd_countdata"])
```

### Example 3: Working with Sensor Data

To download sensor data with a specific time interval:

```python
from neon_utilities import load_by_product

# Download 30-minute precipitation data
precip_data = load_by_product(
    dpid="DP1.00006.001",  # Precipitation
    site="HARV",           # Harvard Forest
    startdate="2019-01",   
    enddate="2019-01",     # Just one month
    timeindex="30"         # 30-minute intervals
)

# Access the precipitation data
precip_30min = precip_data["PRIPRE_30min"]

# Basic time series plot
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 5))
plt.plot(precip_30min["endDateTime"], precip_30min["priPrecipBulk"])
plt.title("Precipitation at Harvard Forest - January 2019")
plt.xlabel("Date")
plt.ylabel("Precipitation (mm)")
plt.grid(True)
plt.tight_layout()
plt.show()
```

## Working with AOP Data

### Example 4: Download Specific AOP Tiles

If you're interested in a specific area within a NEON site:

```python
from neon_utilities import list_available_dates, get_aop_tile_extents, by_tile_aop

# Check available dates
list_available_dates(
    dpid="DP3.30015.001",  # Canopy Height Model
    site="HARV"            # Harvard Forest
)

# Get tile extents
tile_coords = get_aop_tile_extents(
    dpid="DP3.30015.001",  # Canopy Height Model
    site="HARV",           # Harvard Forest
    year="2019"
)

# Download tiles for a specific location
by_tile_aop(
    dpid="DP3.30015.001",   # Canopy Height Model
    site="HARV",            # Harvard Forest
    year="2019",
    easting=732500,         # UTM Easting coordinate
    northing=4713200,       # UTM Northing coordinate
    buffer=0,               # No buffer
    savepath="./data"       # Directory to save the data
)
```

### Example 5: Download Complete AOP Dataset

To download all data for a product, site, and year:

```python
from neon_utilities import by_file_aop

# Download all CHM data for Harvard Forest in 2019
by_file_aop(
    dpid="DP3.30015.001",  # Canopy Height Model
    site="HARV",           # Harvard Forest
    year="2019",
    savepath="./data"
)
```

## Working with Multiple Sites and Products

### Example 6: Download Data for Multiple Sites

```python
from neon_utilities import load_by_product

# Download temperature data for three sites
temp_data = load_by_product(
    dpid="DP1.00002.001",           # Air temperature
    site=["HARV", "BART", "SCBI"],  # Three different sites
    startdate="2019-01",
    enddate="2019-03"
)

# Compare mean temperatures by site
import pandas as pd

# Get the 30-minute data
temp_30min = temp_data["TAAT_30min"]

# Calculate monthly means by site
monthly_means = temp_30min.groupby(
    [temp_30min["siteID"], pd.to_datetime(temp_30min["endDateTime"]).dt.to_period("M")]
)["tempSingleMean"].mean().unstack()

# Plot the results
monthly_means.plot(kind="bar", figsize=(10, 6))
plt.title("Mean Monthly Temperature by Site (Q1 2019)")
plt.ylabel("Temperature (°C)")
plt.xlabel("Site")
plt.grid(True, axis="y")
plt.tight_layout()
plt.show()
```

## Best Practices and Tips

### Handling Large Downloads

When working with large datasets:

1. Use `check_size=True` to verify the download size before proceeding
2. Consider downloading specific tables with the `tabl` parameter
3. For sensor data, use the `timeindex` parameter to download only specific time aggregations
4. For AOP data, use `by_tile_aop()` to download only the tiles you need

### Using API Tokens

Always use an API token for better performance and higher rate limits:

```python
from neon_utilities import load_by_product
import os

# Get API token from environment variable
token = os.environ.get("NEON_API_TOKEN")

# Use token in function call
data = load_by_product(
    dpid="DP1.10003.001",
    site="HARV",
    token=token
)
```

### Citing NEON Data

Always cite NEON data in your publications:

```python
from neon_utilities import get_citation

# Get citation for a data product
citation = get_citation(dpid="DP1.10003.001", release="RELEASE-2023")
print(citation)
```

## Next Steps

Now that you understand the basics of using NEON Utilities, you can:

- Explore the [full API reference](../api/reference.md) for detailed function documentation
- Follow the [tutorials](../tutorials/download-process-tabular.md) for step-by-step workflows
- Check the [FAQ](../faq.md) for answers to common questions
