# Download & Load Data

The `load_by_product` function downloads NEON data files, unzips and stacks them, and directly loads the data tables into memory as pandas DataFrames.

## Function Signature

```python
def load_by_product(dpid,
                   site="all",
                   startdate=None,
                   enddate=None,
                   package="basic",
                   release="current",
                   timeindex="all",
                   tabl="all",
                   check_size=True,
                   include_provisional=False,
                   cloud_mode=False,
                   progress=True,
                   token=None):
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

## Returns

A dictionary of pandas DataFrames containing the data tables and metadata.

## Description

The `load_by_product` function is an all-in-one solution that combines the functionality of [`zips_by_product()`](zips_by_product.md) and [`stack_by_table()`](stack_by_table.md). It downloads data packages, unzips the files, stacks the data tables, and loads them directly into memory as pandas DataFrames.

This function is ideal for interactive analysis sessions, where you want to quickly access and start working with NEON data without managing intermediate files.

## Examples

### Basic Usage

Download, stack, and load bird data from Harvard Forest in 2019:

```python
from neonutilities import load_by_product

bird_data = load_by_product(
    dpid="DP1.10003.001",  # Breeding landbird point counts
    site="HARV",           # Harvard Forest
    startdate="2019-01",
    enddate="2019-12"
)

# Access the data tables
bird_counts = bird_data["brd_countdata"]
bird_perpoint = bird_data["brd_perpoint"]

# Print the first few rows of the count data
print(bird_counts.head())
```

### Download Soil Temperature Data at Multiple Sites

```python
soil_temp_data = load_by_product(
    dpid="DP1.00041.001",        # Soil temperature
    site=["HARV", "BART", "SCBI"],  # Harvard Forest, Bartlett, Smithsonian Conservation Biology Institute
    startdate="2020-01",
    enddate="2020-12"
)

# Access the 30-minute averaged data
soil_temp_30min = soil_temp_data["ST_30_minute"]
```

### Download Only a Specific Table

If you only need one specific table from a data product:

```python
# Only download the count data table from bird observations
bird_count_only = load_by_product(
    dpid="DP1.10003.001",
    site="HARV",
    startdate="2019-01",
    enddate="2019-12",
    tabl="brd_countdata"  # Specify just one table
)
```

### With an API Token and No Size Check

For batch processing where you don't want interactive prompts:

```python
data = load_by_product(
    dpid="DP1.10003.001",
    site="HARV",
    startdate="2019-01",
    enddate="2019-12",
    check_size=False,  # Don't prompt for size confirmation
    token="your-api-token-here"
)
```

## Data Structure

The returned dictionary contains:

- One entry for each data table in the product, with the table name as the key
- Metadata entries with keys like `variables_10003`, `issueLog_10003`, etc.

For example, a complete bird data download might include:

- `brd_countdata`: Bird count observations
- `brd_perpoint`: Data for each sampling point
- `brd_personnel`: Personnel who collected the data
- `variables_10003`: Variable definitions
- `validation_10003`: Data validation rules
- `issueLog_10003`: Known issues with the data
- `categoricalCodes_10003`: Definitions for categorical values
- `readme_10003`: General information about the data product
- `citation_10003_RELEASE-20XX`: Citation information

## Notes

- This function will temporarily use disk space during the download and stacking process, even though the final output is in memory.
- For very large datasets, consider using `zips_by_product()` and `stack_by_table()` separately to manage the process more explicitly.
- Windows has a default maximum path length of 260 characters, which can cause download functions to fail if this limit is exceeded. If you encounter this issue, either change your working or savepath directory to be closer to the root directory, or enable long paths on Windows.
- The `cloud_mode` parameter should only be used when your destination environment is in the cloud, such as in Google Colab or similar services.

## Related Functions

- [`zips_by_product()`](zips_by_product.md): Download data packages without loading them
- [`stack_by_table()`](stack_by_table.md): Stack downloaded data files into tables
- [`read_table_neon()`](../processing/read_table_neon.md): Read NEON tables with correct data types
