# Find Available Tiles

The `get_aop_tile_extents` function displays and returns the tile extents (UTM coordinates) for a specified NEON Airborne Observation Platform (AOP) data product at a given site and year.

## Function Signature

```python
def get_aop_tile_extents(dpid,
                         site,
                         year,
                         token=None):
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `dpid` | str | The data product identifier in the form DP#.#####.###, e.g., "DP3.30015.001" |
| `site` | str | The four-letter code of a NEON site, e.g., "HARV" |
| `year` | str or int | The four-digit year of data collection, e.g., "2019" or 2019 |
| `token` | str, optional | User-specific API token; if omitted, uses the public rate limit |

## Returns

A sorted list of tuples containing the UTM easting and northing coordinates of all tiles available for the specified data product, site, and year. The function also prints the minimum and maximum UTM easting and northing values (the boundaries of the available data).

## Description

The `get_aop_tile_extents` function is designed to help users determine what AOP data tiles are available for a specific product, site, and year. This is particularly useful before using [`by_tile_aop()`](by_tile_aop.md) to download specific tiles.

NEON AOP data is organized into 1km × 1km tiles based on UTM coordinates. Each tile is named according to the UTM coordinates of its southwest corner (e.g., `731000_4712000` for a tile with its southwest corner at easting 731000, northing 4712000).

The function queries the NEON API for the available tiles and returns a list of their UTM coordinates. It also prints the minimum and maximum easting and northing values, providing the overall extents of the available data.

## Examples

### Basic Usage

```python
from neonutilities import get_aop_tile_extents

# Get tile extents for Canopy Height Model at Harvard Forest in 2019
tile_coordinates = get_aop_tile_extents(
    dpid="DP3.30015.001",  # Canopy Height Model
    site="HARV",           # Harvard Forest
    year="2019"
)

print("Available tile coordinates (UTM Easting_Northing):")
for coord in tile_coordinates:
    print(f"{coord[0]}_{coord[1]}")
```

Output:
```
Easting Bounds: (731000, 733000)
Northing Bounds: (4712000, 4714000)
Available tile coordinates (UTM Easting_Northing):
731000_4712000
731000_4713000
732000_4712000
732000_4713000
733000_4712000
733000_4713000
```

### Check Availability Before Downloading

Use this function to check tile availability before downloading with `by_tile_aop()`:

```python
from neonutilities import get_aop_tile_extents, by_tile_aop
import matplotlib.pyplot as plt
import numpy as np

# Get available tile coordinates
tile_coordinates = get_aop_tile_extents(
    dpid="DP3.30015.001",
    site="HARV",
    year="2019"
)

# Visualize the available tiles
eastings = [coord[0] for coord in tile_coordinates]
northings = [coord[1] for coord in tile_coordinates]

# Create a tile grid visualization
plt.figure(figsize=(10, 8))
plt.scatter(eastings, northings, s=1000, marker='s', alpha=0.5)

# Add tile labels
for e, n in zip(eastings, northings):
    plt.text(e + 500, n + 500, f"{e}_{n}", ha='center', va='center')

# Add a point of interest
poi_easting = 732500
poi_northing = 4713200
plt.scatter(poi_easting, poi_northing, color='red', s=100, marker='*')
plt.text(poi_easting, poi_northing - 100, "Point of Interest", ha='center', color='red')

plt.title("Available AOP Tiles and Point of Interest")
plt.xlabel("UTM Easting")
plt.ylabel("UTM Northing")
plt.grid(True)
plt.axis('equal')
plt.tight_layout()
plt.show()

# Download the tile containing the point of interest
by_tile_aop(
    dpid="DP3.30015.001",
    site="HARV",
    year="2019",
    easting=poi_easting,
    northing=poi_northing,
    savepath="./data"
)
```

### Use with API Token

```python
import os

# Get token from environment variable
token = os.environ.get("NEON_API_TOKEN")

# Get tile extents with token
tile_coordinates = get_aop_tile_extents(
    dpid="DP3.30015.001",
    site="HARV",
    year="2019",
    token=token
)
```

## Notes

### Data Product Requirements

This function only works with Level 3 (L3) AOP data products. If you attempt to use it with other products, it will raise an error.

### Blandy Experimental Farm (BLAN)

The Blandy Experimental Farm (BLAN) site spans two UTM zones (17N and 18N), but all flight data are processed in 17N. If working with data from this site, be aware that you may need to convert coordinates between UTM zones.

### No Data Available

If no data is available for the specified product, site, and year, the function will return an appropriate message. You can check available dates using [`list_available_dates()`](list_available_dates.md).

### Usage with by_tile_aop

The coordinates returned by this function represent the southwest corners of 1km × 1km tiles. When using [`by_tile_aop()`](by_tile_aop.md), you'll typically provide a coordinate anywhere within the tile you're interested in, and the function will determine which tile contains that coordinate.

## Related Functions

- [`list_available_dates()`](list_available_dates.md): List available data collection dates for a product and site
- [`by_tile_aop()`](by_tile_aop.md): Download specific tiles of AOP data
- [`by_file_aop()`](by_file_aop.md): Download all files for an AOP data product
