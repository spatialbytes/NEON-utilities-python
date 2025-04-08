# Frequently Asked Questions

This page answers common questions about using the NEON Utilities Python package and working with NEON data.

## General Questions

### What is NEON?

The National Ecological Observatory Network (NEON) is a continental-scale ecological observation facility sponsored by the National Science Foundation and operated by Battelle. NEON collects and provides open data from 81 field sites across the United States that characterize and quantify how our nation's ecosystems are changing.

### What types of data does NEON collect?

NEON collects three main types of data:
- **Observational data (OS)**: Field observations collected by staff (e.g., bird surveys, plant diversity)
- **Instrumented data (IS)**: Automated sensor measurements (e.g., temperature, precipitation)
- **Airborne Observation Platform (AOP) data**: Remote sensing data collected from aircraft (e.g., LiDAR, hyperspectral imagery)

### How do I cite NEON data in my research?

Citations for NEON data should include both the data product and the specific release used. You can get the proper citation using the `get_citation()` function:

```python
from neonutilities import get_citation

citation = get_citation(dpid="DP1.10003.001", release="RELEASE-2023")
print(citation)
```

Additionally, please cite the NEON Utilities package:

```
National Ecological Observatory Network. 2024. NEON Utilities Python: Tools to download and work with NEON data, Python version x.x.x. https://github.com/neonscience/neon-utilities-python
```

## Installation and Setup

### Why am I getting "Permission denied" errors during installation?

If you're getting permission errors, try installing with the `--user` flag:

```bash
pip install --user neon-utilities
```

Alternatively, consider using a virtual environment or conda environment.

### How do I update to the latest version?

```bash
pip install --upgrade neon-utilities
```

### Do I need an API token to use the package?

An API token is not required, but it's highly recommended, especially for downloading large amounts of data. With an API token, your rate limit increases from 200 to 10,000 requests per hour. See the [API token guide](getting-started/api-token.md) for setup instructions.

## Working with NEON Data

### How do I find what data products are available?

You can browse the [NEON Data Portal](https://data.neonscience.org/data-products/explore) or use the API:

```python
from neonutilities.helper_mods.api_helpers import get_api
import pandas as pd

response = get_api("https://data.neonscience.org/api/v0/products")
products = pd.DataFrame(response.json()['data'])
print(products[['productCode', 'productName']])
```

### How do I check what sites and dates are available for a specific product?

For most data products, you can check through the API:

```python
from neonutilities.helper_mods.api_helpers import get_api

response = get_api("https://data.neonscience.org/api/v0/products/DP1.10003.001")
site_data = response.json()['data']['siteCodes']

for site in site_data:
    site_code = site['siteCode']
    months = []
    for release in site['availableReleases']:
        months.extend(release['availableMonths'])
    print(f"{site_code}: {sorted(months)}")
```

For AOP data, use the `list_available_dates()` function:

```python
from neonutilities import list_available_dates

list_available_dates(dpid="DP3.30015.001", site="HARV")
```

### What's the difference between `zips_by_product()`, `load_by_product()`, and `stack_by_table()`?

- **`zips_by_product()`**: Downloads data files to your local system but doesn't process them
- **`load_by_product()`**: Downloads, processes, and loads data directly into memory as pandas DataFrames
- **`stack_by_table()`**: Takes previously downloaded data and stacks it into unified tables

If you're doing interactive analysis, `load_by_product()` is usually most convenient. For batch processing or very large datasets, use `zips_by_product()` followed by `stack_by_table()`.

### How do I download data from multiple sites or multiple years?

For multiple sites, pass a list of site codes:

```python
from neonutilities import load_by_product

data = load_by_product(
    dpid="DP1.10003.001",
    site=["HARV", "BART", "SCBI"],
    startdate="2019-01",
    enddate="2019-12"
)
```

For multiple years, specify the date range:

```python
data = load_by_product(
    dpid="DP1.10003.001",
    site="HARV",
    startdate="2018-01",
    enddate="2020-12"
)
```

### How do I deal with very large datasets?

For large datasets:

1. **Download selectively**:
   - Download specific time intervals: `timeindex="30"` (30-minute data)
   - Download specific tables: `tabl="tablename"`
   - Download specific AOP tiles: Use `by_tile_aop()` instead of `by_file_aop()`

2. **Process in chunks**:
   - Download by year or site
   - Use `stack_by_table()` with chunked inputs

3. **Use cloud-based processing**:
   - Consider cloud-based tools like Google Colab
   - Use `cloud_mode=True` for cloud-to-cloud transfers

### Why do I get a warning about bundled data products?

Some data products have been bundled with others and are no longer available independently. The package will redirect you to the bundled product. For example, root chemistry data has been bundled with root biomass data.

## Troubleshooting

### I'm getting API rate limit errors. What should I do?

If you're hitting rate limits:

1. Use an API token (increases from 200 to 10,000 requests per hour)
2. Add delays between requests
3. Batch your downloads by site or date

### Why can't I download certain AOP data products?

Some common reasons:

1. The data product might not be available for that site/year
2. The product might be suspended (e.g., DP3.30016.001 - Biomass maps)
3. You might be using the wrong function (e.g., using `zips_by_product()` instead of `by_file_aop()`)

Check availability with `list_available_dates()` first.

### I'm getting path length errors on Windows. How do I fix this?

Windows has a default maximum path length of 260 characters. To resolve this:

1. **Option 1**: Move your working directory closer to the root
2. **Option 2**: Enable long path support in Windows:
   - Run `regedit.exe`
   - Navigate to `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem`
   - Set `LongPathsEnabled` to `1`
   - Restart your computer

### Why are some sites showing warnings about being collocated sites?

NEON has both terrestrial and aquatic sites. Some sites are collocated, meaning data for an aquatic site is collected under a nearby terrestrial site. The package automatically handles this and will inform you when it's downloading data from a collocated site.

Example message:
```
TREE is part of the flight box for STEI. Downloading data from STEI.
```

### Why are certain date formats or data types incorrect in my output?

Use the `read_table_neon()` function to ensure proper data types:

```python
from neonutilities import read_table_neon

data = read_table_neon(
    data_file="path/to/your/data.csv",
    var_file="path/to/your/variables.csv"
)
```

This function uses the NEON variables file to assign correct data types to each column.

## Advanced Usage

### How do I combine NEON data with external datasets?

NEON data can be combined with other datasets using common identifiers:

1. **Spatial data**: Use site coordinates or UTM information
2. **Temporal data**: Use timestamp columns
3. **Taxonomic data**: Use NEON's taxon IDs or scientific names

Example with MODIS data:
```python
# Steps to join NEON data with MODIS by site coordinates
# 1. Get NEON site coordinates
# 2. Extract MODIS data for those coordinates
# 3. Join datasets by date and location
```

### How can I optimize my workflow for regular NEON data processing?

For regular processing:

1. Create a configuration file for common parameters
2. Use environment variables for your API token
3. Consider creating a processing pipeline with tools like Airflow or Luigi
4. Cache downloaded data to avoid redundant downloads

### How do I report issues or contribute to the package?

- **Report issues**: Visit the [GitHub issues page](https://github.com/neonscience/neon-utilities-python/issues)
- **Contribute**: Fork the repository, make changes, and submit a pull request
- **Contact NEON**: For data-specific questions, contact NEON at info@neonscience.org

## Additional Resources

- [NEON Data Portal](https://data.neonscience.org/)
- [NEON GitHub Repository](https://github.com/neonscience)
- [NEON Learning Hub](https://www.neonscience.org/resources/learning-hub)
- [NEON API Documentation](https://data.neonscience.org/data-api)
- [NEON Utilities R Package](https://github.com/NEONScience/NEON-utilities)
- [Scientific Publications Using NEON Data](https://www.neonscience.org/impact/scientific-publications)
