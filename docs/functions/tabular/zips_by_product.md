# Download Data Packages

The `zips_by_product` function is a core function in the NEON Utilities package used to download NEON data packages for a specified data product, site(s), and time range.

## Function Signature

```python
def zips_by_product(dpid, site="all", startdate=None, enddate=None,
                    package="basic", release="current",
                    timeindex="all", tabl="all", check_size=True,
                    include_provisional=False, cloud_mode=False,
                    progress=True, token=None, savepath=None):
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `dpid` | str | Data product identifier in the form DP#.#####.###, e.g., "DP1.10003.001" |
| `site` | str or list | Either "all" or one or more 4-letter NEON site codes; defaults to "all" |
| `startdate` | str, optional | Earliest date of data to download in the form YYYY-MM |
| `enddate` | str, optional | Latest date of data to download in the form YYYY-MM |
| `package` | str, optional | Download package to access, either "basic" or "expanded"; defaults to "basic" |
| `release` | str, optional | Data release to download; defaults to the most recent release |
| `timeindex` | str, optional | Either "all" or the time index in minutes; only for sensor data; defaults to "all" |
| `tabl` | str, optional | Either "all" or the name of a single data table; only for observational data; defaults to "all" |
| `check_size` | bool, optional | Prompt user to approve download size; defaults to `True` |
| `include_provisional` | bool, optional | Include provisional data; defaults to `False` |
| `cloud_mode` | bool, optional | Transfer files cloud-to-cloud; defaults to `False` |
| `progress` | bool, optional | Display progress bars; defaults to `True` |
| `token` | str, optional | User-specific API token; if omitted, uses the public rate limit |
| `savepath` | str, optional | File path to save downloaded data; defaults to current working directory |

## Returns

None. The function downloads data to the specified `savepath` or the current working directory if no `savepath` is provided.

When `cloud_mode=True`, the function returns a list of file paths meeting the input criteria instead of downloading files.

## Description

The `zips_by_product` function queries the NEON API for the specified data product and criteria, then downloads the corresponding data packages. It is designed to work with NEON's observational (OS) and instrumented (IS) data; for remote sensing data, use the [by_file_aop()](../aop/by_file_aop.md) and [by_tile_aop()](../aop/by_tile_aop.md) functions.

The function handles various special cases, such as:
- Aquatic sites where certain data are collected at nearby terrestrial sites
- Chemistry bundles where data products have been combined
- Vegetation structure and sediment data product bundles

The downloaded data will be saved in a folder named `filesToStack####` where `####` corresponds to the five digits in the middle of the data product ID. For example, data from `DP1.10003.001` will be saved to the `filesToStack10003` folder.

## Examples

### Basic Usage

Download bird survey data for the Harvard Forest site:

```python
from neonutilities import zips_by_product

# Download bird survey data
zips_by_product(
    dpid="DP1.10003.001",  # Breeding landbird point counts
    site="HARV",           # Harvard Forest
    startdate="2019-01",
    enddate="2019-12",
    savepath="./data"      # Directory to save data
)
```

### Download Sensor Data with Specific Time Interval

For instrumented data, you can specify a time interval to download:

```python
# Download 30-minute precipitation data
zips_by_product(
    dpid="DP1.00006.001",  # Precipitation
    site="HARV",           # Harvard Forest
    startdate="2019-01",
    enddate="2019-12",
    timeindex="30",        # 30-minute data
    savepath="./data"
)
```

### Download Data for Multiple Sites

```python
# Download bird data from three sites
zips_by_product(
    dpid="DP1.10003.001",
    site=["HARV", "BART", "SCBI"],  # Harvard Forest, Bartlett Forest, Smithsonian Conservation Biology Institute
    startdate="2019-01",
    enddate="2019-12",
    savepath="./data"
)
```

### Download a Specific Table

If you only need a specific table from a data product:

```python
# Download only the count data table from bird observations
zips_by_product(
    dpid="DP1.10003.001",
    site="HARV",
    startdate="2019-01",
    enddate="2019-12",
    tabl="brd_countdata",  # Specify just one table
    savepath="./data"
)
```

### Use with API Token

For better performance and higher rate limits:

```python
import os

# Get token from environment variable
token = os.environ.get("NEON_API_TOKEN")

# Download data with token
zips_by_product(
    dpid="DP1.10003.001",
    site="HARV",
    startdate="2019-01",
    enddate="2019-12",
    token=token,
    savepath="./data"
)
```

### Download Without Size Confirmation

For batch processing or automation:

```python
# Download without size confirmation
zips_by_product(
    dpid="DP1.10003.001",
    site="HARV",
    startdate="2019-01",
    enddate="2019-12",
    check_size=False,  # Skip size confirmation
    savepath="./data"
)
```

### Include Provisional Data

To include provisional data in your download:

```python
# Download including provisional data
zips_by_product(
    dpid="DP1.10003.001",
    site="HARV",
    startdate="2019-01",
    enddate="2019-12",
    include_provisional=True,  # Include provisional data
    savepath="./data"
)
```

### Cloud Mode for Cloud-to-Cloud Transfers

For use in cloud environments:

```python
# Get file list without downloading
file_list = zips_by_product(
    dpid="DP1.10003.001",
    site="HARV",
    startdate="2019-01",
    enddate="2019-12",
    cloud_mode=True  # Return file list instead of downloading
)

print(f"Found {len(file_list[0])} files to download")
```

## Notes

### Unsupported Products

The function will raise an error for data products that cannot be downloaded using `zips_by_product`:

- AOP (remote sensing) products: Use `by_file_aop()` or `by_tile_aop()` instead
- Phenocam products: Data hosted by PhenoCam
- Aeronet products: Data hosted by Aeronet
- Digital hemispherical images (expanded package): Exceeds download limits
- Individual SAE (Surface-Atmosphere Exchange) products: Only available in bundled product (DP4.00200.001)

### Windows Path Length Limitations

Windows has a default maximum path length of 260 characters, which can cause download functions to fail if this limit is exceeded. If the file path exceeds 260 characters on a Windows system, the package will issue a warning.

To avoid this issue:
- Move your working or savepath directory closer to the root directory
- Enable long paths on Windows

## Related Functions

- [load_by_product()](load_by_product.md): Download and load data directly into memory
- [stack_by_table()](stack_by_table.md): Stack downloaded data into unified tables
- [by_file_aop()](../aop/by_file_aop.md): Download AOP (remote sensing) data
- [by_tile_aop()](../aop/by_tile_aop.md): Download specific tiles of AOP data
