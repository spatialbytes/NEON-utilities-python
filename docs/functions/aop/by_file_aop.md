# Download Complete Site Data

The `by_file_aop` function is used to download all Airborne Observation Platform (AOP) data files for a specific data product, site, and year. This function downloads the complete site coverage, preserving the original file organization.

## Function Signature

```python
def by_file_aop(dpid,
                site,
                year,
                include_provisional=False,
                check_size=True,
                savepath=None,
                chunk_size=1024,
                token=None):
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `dpid` | str | The data product identifier in the form DP#.#####.###, e.g., "DP3.30015.001" |
| `site` | str | The four-letter code of a NEON site, e.g., "HARV" |
| `year` | str or int | The four-digit year of data collection, e.g., "2019" or 2019 |
| `include_provisional` | bool, optional | If `True`, includes provisional data; defaults to `False` |
| `check_size` | bool, optional | If `True`, prompts the user to confirm download size before proceeding; defaults to `True` |
| `savepath` | str, optional | Path to save the downloaded files; if `None`, uses the current working directory |
| `chunk_size` | int, optional | Size in bytes of chunks for chunked download; defaults to 1024 |
| `token` | str, optional | User-specific API token; if omitted, uses the public rate limit |

## Returns

This function does not return any values. All data files are downloaded to the local directory specified in `savepath` or to the current working directory if `savepath` is not provided.

## Description

The function queries the NEON API for all available AOP data files of the specified data product at the specified site and year. It then downloads these files, preserving the original folder structure. Files are downloaded serially to avoid API rate-limit overload, which may take some time for large datasets.

The function automatically handles collocated sites (e.g., where data for an aquatic site is published under an adjacent terrestrial site) and will inform you when this occurs.

## Examples

### Basic Usage

Download the 2019 Canopy Height Model (CHM) data for Harvard Forest:

```python
from neon_utilities import by_file_aop

by_file_aop(
    dpid="DP3.30015.001",  # Canopy Height Model
    site="HARV",           # Harvard Forest
    year="2019",
    savepath="./data"
)
```

### Download without Size Confirmation

When working in batch mode or other non-interactive workflows, you can disable the size confirmation prompt:

```python
by_file_aop(
    dpid="DP3.30015.001",
    site="HARV",
    year="2019",
    check_size=False,
    savepath="./data"
)
```

### Include Provisional Data

To include provisional data in your download:

```python
by_file_aop(
    dpid="DP3.30015.001",
    site="HARV",
    year="2019",
    include_provisional=True,
    savepath="./data"
)
```

### Use with API Token

To use your personal API token for increased rate limits:

```python
by_file_aop(
    dpid="DP3.30015.001",
    site="HARV",
    year="2019",
    token="your-api-token-here",
    savepath="./data"
)
```

## Notes

- For most AOP data, file sizes can be very large (several GB to several TB depending on the product, site, and year). Make sure you have sufficient storage space before downloading.
- If you only need data for a specific area within a site, consider using `by_tile_aop()` instead to download only the tiles covering your area of interest.
- Windows has a default maximum path length of 260 characters, which can cause download functions to fail if this limit is exceeded. If you encounter this issue, either change your working or savepath directory to be closer to the root directory, or enable long paths on Windows.

## Related Functions

- [`by_tile_aop()`](by_tile_aop.md): Download specific tiles of AOP data
- [`get_aop_tile_extents()`](get_aop_tile_extents.md): Get the boundaries of the AOP data tiles
- [`list_available_dates()`](list_available_dates.md): List available data collection dates for a product and site
