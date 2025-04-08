# Core Functions

The NEON Utilities Python package provides a suite of functions designed to help you access, download, and process NEON data. These core functions are organized into four categories based on their purpose and the type of data they work with.

## Tabular Data Functions

These functions are designed to work with NEON's observational (OS) and instrumented (IS) data products, which are typically delivered as tabular data in CSV format.

| Function | Description |
|----------|-------------|
| [`zips_by_product()`](tabular/zips_by_product.md) | Downloads data packages for specified products, sites, and dates |
| [`load_by_product()`](tabular/load_by_product.md) | Downloads and loads data directly into memory as pandas DataFrames |
| [`stack_by_table()`](tabular/stack_by_table.md) | Stacks downloaded data files into unified tables |

## AOP (Remote Sensing) Data Functions

These functions handle NEON's Airborne Observation Platform (AOP) data products, which include LiDAR, hyperspectral imagery, and derived products like canopy height models.

| Function | Description |
|----------|-------------|
| [`by_file_aop()`](aop/by_file_aop.md) | Downloads all files for an AOP product at a specified site and year |
| [`by_tile_aop()`](aop/by_tile_aop.md) | Downloads specific geographic tiles of AOP data based on UTM coordinates |
| [`get_aop_tile_extents()`](aop/get_aop_tile_extents.md) | Displays and returns the boundaries of available AOP tiles |
| [`list_available_dates()`](aop/list_available_dates.md) | Lists available data collection dates for a product and site |

## Metadata Functions

These functions help you access metadata about NEON data products, which is crucial for proper data interpretation and citation.

| Function | Description |
|----------|-------------|
| [`get_citation()`](metadata/get_citation.md) | Retrieves proper citation information for NEON data in BibTeX format |
| [`get_issue_log()`](metadata/get_issue_log.md) | Retrieves the issue log for a data product to understand known issues |

## Data Processing Functions

These functions assist with processing NEON data after it has been downloaded, ensuring proper data types and organization.

| Function | Description |
|----------|-------------|
| [`read_table_neon()`](processing/read_table_neon.md) | Reads NEON data tables with correct data types based on the variables file |
| [`unzip_and_stack`](processing/unzip_and_stack.md) | Helper functions for processing downloaded data packages |

## Typical Workflow

A typical workflow using these functions might look like:

1. **Check data availability**:
   ```python
   from neon_utilities import list_available_dates
   list_available_dates(dpid="DP1.10003.001", site="HARV")
   ```

2. **Download and load data**:
   ```python
   from neon_utilities import load_by_product
   bird_data = load_by_product(
       dpid="DP1.10003.001",
       site="HARV",
       startdate="2019-01",
       enddate="2019-12"
   )
   ```

3. **Check for known issues**:
   ```python
   issue_log = bird_data["issueLog_10003"]
   print(issue_log[issue_log['locationAffected'].str.contains('HARV', na=False)])
   ```

4. **Cite the data properly**:
   ```python
   from neon_utilities import get_citation
   citation = get_citation(dpid="DP1.10003.001", release="RELEASE-2023")
   print(citation)
   ```

For more detailed instructions and examples, see the individual function documentation pages linked above, or explore the [Tutorials](../tutorials/download-process-tabular.md) section for comprehensive workflows.
