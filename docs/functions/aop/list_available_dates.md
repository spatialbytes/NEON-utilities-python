# Check Available Dates

The `list_available_dates` function displays the available releases and dates for a specified NEON data product at a particular site. This function is particularly useful for determining what data is available before attempting to download it.

## Function Signature

```python
def list_available_dates(dpid, site):
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `dpid` | str | The data product identifier in the form DP#.#####.###, e.g., "DP3.30015.001" |
| `site` | str | The four-letter code of a NEON site, e.g., "HARV" |

## Returns

This function does not return any values. It prints the release tag (or "PROVISIONAL") and the corresponding available dates (YYYY-MM) for each release tag to the console.

## Description

The `list_available_dates` function queries the NEON API to determine what data is available for a specified data product at a particular site. It displays this information organized by release tag, listing all available months for each release.

This function is essential for planning data downloads, especially for AOP data where availability can vary significantly across sites and years. By checking availability before attempting to download, you can avoid errors and save time.

## Examples

### Basic Usage

```python
from neonutilities import list_available_dates

# Check available dates for Canopy Height Model at Harvard Forest
list_available_dates(
    dpid="DP3.30015.001",  # Canopy Height Model
    site="HARV"            # Harvard Forest
)
```

Output:
```
RELEASE-2023 Available Dates: 2017-06, 2019-08, 2021-07
```

### Check Multiple Sites

```python
from neonutilities import list_available_dates

# Create a list of sites to check
sites = ["HARV", "BART", "SCBI", "GRSM"]

# Check available dates for each site
for site in sites:
    print(f"\n{site}:")
    list_available_dates(
        dpid="DP3.30015.001",
        site=site
    )
```

Output:
```
HARV:
RELEASE-2023 Available Dates: 2017-06, 2019-08, 2021-07

BART:
RELEASE-2023 Available Dates: 2017-07, 2018-07, 2019-07, 2021-08

SCBI:
RELEASE-2023 Available Dates: 2017-05, 2019-07, 2021-06

GRSM:
RELEASE-2023 Available Dates: 2018-05, 2019-05, 2021-06
```

### Check Before Downloading

It's good practice to check data availability before attempting to download:

```python
from neonutilities import list_available_dates, by_file_aop

# Check available dates
list_available_dates(
    dpid="DP3.30015.001",
    site="HARV"
)

# Based on the results, download the most recent data
by_file_aop(
    dpid="DP3.30015.001",
    site="HARV",
    year="2021",
    savepath="./data"
)
```

### Check Provisional Data

You can see if provisional data is available:

```python
from neonutilities import list_available_dates

# Check available dates including provisional data
list_available_dates(
    dpid="DP3.30015.001",
    site="HOPB"
)
```

Output:
```
PROVISIONAL Available Dates: 2023-07
RELEASE-2023 Available Dates: 2017-08, 2019-08, 2021-08
```

## Notes

### Handling of Provisional and Released Data

The function displays data availability organized by release tag. There are two types of release tags:

1. **RELEASE-YYYY**: Official releases of data, which have undergone quality control and validation
2. **PROVISIONAL**: Data that has been processed but not yet officially released

### Data Product Validation

The function validates that the specified data product ID is properly formatted and that the site code is a valid four-letter NEON site code. If either is invalid, an appropriate error message is displayed.

### No Data Available

If no data is available for the specified product and site, the function will raise a ValueError:

```
ValueError: There are no data available for the data product DP1.10098.001 at the site HOPB.
```

### Usage with Other Functions

This function is often used in conjunction with data download functions to determine what data is available before downloading:

- For AOP data: [`by_file_aop()`](by_file_aop.md) or [`by_tile_aop()`](by_tile_aop.md)
- For tabular data: [`zips_by_product()`](../tabular/zips_by_product.md) or [`load_by_product()`](../tabular/load_by_product.md)

## Related Functions

- [`get_aop_tile_extents()`](get_aop_tile_extents.md): Get the boundaries of AOP data tiles
- [`by_file_aop()`](by_file_aop.md): Download all files for an AOP data product
- [`by_tile_aop()`](by_tile_aop.md): Download specific tiles of AOP data
