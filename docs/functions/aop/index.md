# AOP (Remote Sensing) Data Functions

This section covers functions designed to work with NEON's Airborne Observation Platform (AOP) data products. These functions help you access, download, and work with remote sensing data collected by NEON's airborne sensors.

## Available Functions

| Function | Description |
|----------|-------------|
| [`by_file_aop()`](by_file_aop.md) | Downloads all files for an AOP product at a specified site and year |
| [`by_tile_aop()`](by_tile_aop.md) | Downloads specific geographic tiles of AOP data based on UTM coordinates |
| [`get_aop_tile_extents()`](get_aop_tile_extents.md) | Displays and returns the boundaries of available AOP tiles |
| [`list_available_dates()`](list_available_dates.md) | Lists available data collection dates for a product and site |

## When to Use Each Function

- **`list_available_dates()`**: Use first to determine what data is available for your site and product of interest.

- **`get_aop_tile_extents()`**: Use to determine the geographic coverage of available data and to plan which tiles you need.

- **`by_tile_aop()`**: Use when you need data for specific locations within a NEON site, which can save considerable storage space compared to downloading the entire site.

- **`by_file_aop()`**: Use when you need complete coverage of a site, or when you're not sure which specific tiles you need.

## Common AOP Data Products

| Data Product ID | Name | Description |
|-----------------|------|-------------|
| DP3.30015.001 | Canopy Height Model | Raster of vegetation height above ground |
| DP3.30010.001 | RGB Camera Mosaic | High-resolution true-color imagery |
| DP3.30006.001 | Spectrometer Orthorectified Surface Directional Reflectance | Hyperspectral imagery |
| DP3.30024.001 | Lidar Classified Point Cloud | 3D point cloud with classification labels |
| DP3.30025.001 | Lidar Elevation - Digital Terrain Model | Raster of ground elevation |
| DP3.30026.001 | Ecosystem Structure | Maps of vegetation structure metrics |

## Typical Workflow

A common workflow for working with NEON AOP data involves:

1. **Check availability**: Use `list_available_dates()` to see what years have data for your site
2. **Determine coverage**: Use `get_aop_tile_extents()` to see what tiles are available
3. **Download data**: Use either `by_tile_aop()` for specific areas or `by_file_aop()` for complete coverage
4. **Process data**: Load and analyze the data using geospatial libraries like rasterio, GDAL, or LiDAR processing tools

## Example

```python
from neon_utilities import list_available_dates, get_aop_tile_extents, by_tile_aop
import os

# Step 1: Check what dates are available
list_available_dates(
    dpid="DP3.30015.001",  # Canopy Height Model
    site="HARV"            # Harvard Forest
)

# Step 2: Get tile extents for a specific year
tile_coords = get_aop_tile_extents(
    dpid="DP3.30015.001",
    site="HARV",
    year="2019"
)

# Step 3: Download a specific tile containing my study plot
by_tile_aop(
    dpid="DP3.30015.001",
    site="HARV",
    year="2019",
    easting=732500,        # UTM easting coordinate
    northing=4713200,      # UTM northing coordinate
    savepath="./data"
)
```

## Data Organization

NEON AOP data is organized into 1km × 1km tiles based on UTM coordinates. Each tile is named according to the UTM coordinates of its southwest corner (e.g., `731000_4712000` for a tile with its southwest corner at easting 731000, northing 4712000).

Because of this organization, it's often more efficient to download just the tiles you need rather than the entire dataset for a site, which can be very large (hundreds of GB to several TB).

## Related Resources

- [NEON AOP Data Overview](https://www.neonscience.org/data-collection/airborne-remote-sensing)
- [Working with NEON AOP Data Tutorial](../../tutorials/download-process-aop.md)
- [NEON AOP Data Products Catalog](https://www.neonscience.org/data-collection/airborne-remote-sensing)
- [Basic Usage Guide](../../getting-started/basic-usage.md)
