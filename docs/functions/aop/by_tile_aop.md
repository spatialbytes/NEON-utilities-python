# Download Specific Tiles

The `by_tile_aop` function downloads Airborne Observation Platform (AOP) data for specific geographic tiles based on UTM coordinates. It's a more targeted alternative to [`by_file_aop()`](by_file_aop.md) when you only need data for specific locations within a NEON site.

## Function Signature

```python
def by_tile_aop(dpid,
                site,
                year,
                easting,
                northing,
                buffer=0,
                include_provisional=False,
                check_size=True,
                savepath=None,
                chunk_size=1024,
                token=None,
                verbose=False):
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `dpid` | str | The data product identifier in the form DP#.#####.###, e.g., "DP3.30015.001" |
| `site` | str | The four-letter code of a NEON site, e.g., "HARV" |
| `year` | str or int | The four-digit year of data collection, e.g., "2019" or 2019 |
| `easting` | int or list of int | UTM easting coordinate(s) of the locations to download |
| `northing` | int or list of int | UTM northing coordinate(s) of the locations to download |
| `buffer` | int, optional | Size in meters of the buffer around coordinates; defaults to 0 |
| `include_provisional` | bool, optional | If `True`, includes provisional data; defaults to `False` |
| `check_size` | bool, optional | If `True`, prompts for download size confirmation; defaults to `True` |
| `savepath` | str, optional | Path to save the downloaded files; if `None`, uses the current working directory |
| `chunk_size` | int, optional | Size in bytes of chunks for chunked download; defaults to 1024 |
| `token` | str, optional | User-specific API token; if omitted, uses the public rate limit |
| `verbose` | bool, optional | If `True`, prints extra information about downloaded tiles; defaults to `False` |

## Returns

This function does not return any values. All data files are downloaded to the local directory specified in `savepath` or to the current working directory if `savepath` is not provided.

## Description

The `by_tile_aop` function queries the NEON API for AOP data files that cover specific UTM coordinates within a NEON site. Unlike [`by_file_aop()`](by_file_aop.md) which downloads all files for an entire site, this function allows you to download only the data tiles that cover your specific area of interest.

NEON AOP data is organized into 1km × 1km tiles based on UTM coordinates. Each tile is named according to the UTM coordinates of its southwest corner (e.g., `731000_4712000` for a tile with its southwest corner at easting 731000, northing 4712000).

The function determines which tiles cover the specified coordinates (plus any buffer), and downloads only those tiles. This can significantly reduce the download size compared to downloading data for an entire site.

## Examples

### Basic Usage

Download Canopy Height Model (CHM) data for a single location at Harvard Forest:

```python
from neon_utilities import by_tile_aop

by_tile_aop(
    dpid="DP3.30015.001",  # Canopy Height Model
    site="HARV",           # Harvard Forest
    year="2019",
    easting=732500,        # UTM easting coordinate
    northing=4713200,      # UTM northing coordinate
    savepath="./data"
)
```

### Multiple Locations with Buffer

Download data for multiple locations with a buffer zone:

```python
by_tile_aop(
    dpid="DP3.30015.001",
    site="HARV",
    year="2019",
    easting=[732500, 733100],     # Multiple easting coordinates
    northing=[4713200, 4712700],  # Multiple northing coordinates
    buffer=100,                   # 100m buffer around each point
    savepath="./data"
)
```

### Download Without Size Confirmation

For batch processing or automation:

```python
by_tile_aop(
    dpid="DP3.30015.001",
    site="HARV",
    year="2019",
    easting=732500,
    northing=4713200,
    check_size=False,  # Skip size confirmation
    savepath="./data"
)
```

### Use with API Token and Verbose Output

```python
import os

# Get token from environment variable
token = os.environ.get("NEON_API_TOKEN")

by_tile_aop(
    dpid="DP3.30015.001",
    site="HARV",
    year="2019",
    easting=732500,
    northing=4713200,
    token=token,
    verbose=True,  # Print detailed information about tiles
    savepath="./data"
)
```

### Include Provisional Data

```python
by_tile_aop(
    dpid="DP3.30015.001",
    site="HARV",
    year="2019",
    easting=732500,
    northing=4713200,
    include_provisional=True,  # Include provisional data
    savepath="./data"
)
```

## Notes

### UTM Zones

NEON sites are located in different UTM zones, and the function handles this appropriately. For example, the Blandy Experimental Farm (BLAN) site spans two UTM zones (17N and 18N), but all flight data are processed in 17N. The function will automatically convert coordinates from zone 18N to 17N for the BLAN site.

### Tile Boundaries

NEON AOP data is organized into 1km × 1km tiles. Each tile file name contains the UTM coordinates of its southwest corner, for example:
- `NEON_D01_HARV_DP3_732000_4713000_CHM.tif` is the Canopy Height Model tile with its southwest corner at easting 732000, northing 4713000.

### Getting Tile Extents

Before downloading data, you might want to check the available tile extents for a site using the [`get_aop_tile_extents()`](get_aop_tile_extents.md) function:

```python
from neon_utilities import get_aop_tile_extents

# Get tile extents for CHM data at Harvard Forest in 2019
tile_coordinates = get_aop_tile_extents(
    dpid="DP3.30015.001",
    site="HARV",
    year="2019"
)

print("Available tile coordinates:")
for coord in tile_coordinates:
    print(f"{coord[0]}_{coord[1]}")
```

### Data Products

This function only works with Level 3 (L3) AOP data products. If you try to use it with other products, it will return an error.

### Windows Path Length Limitations

Windows has a default maximum path length of 260 characters, which can cause download functions to fail if this limit is exceeded. If you encounter this issue, either change your working or savepath directory to be closer to the root directory, or enable long paths on Windows.

## Related Functions

- [`by_file_aop()`](by_file_aop.md): Download all files for an AOP data product
- [`get_aop_tile_extents()`](get_aop_tile_extents.md): Get the boundaries of AOP data tiles
- [`list_available_dates()`](list_available_dates.md): List available data collection dates for a product and site
