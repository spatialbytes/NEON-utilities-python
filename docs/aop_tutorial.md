# Tutorial: Downloading and Processing AOP Data

This tutorial demonstrates how to work with NEON Airborne Observation Platform (AOP) data using the NEON Utilities Python package. We'll walk through a complete workflow for downloading and processing remote sensing data for a research project.

## Overview

In this tutorial, we'll:

1. Check available dates for a site
2. Explore the tile extents
3. Download specific tiles for our area of interest
4. Load and visualize the data

Let's imagine we're studying forest structure at the NEON Harvard Forest (HARV) site, and we want to analyze the canopy height model (CHM) data for a specific research plot within the site.

## Prerequisites

- NEON Utilities package installed
- Basic knowledge of Python and geospatial data analysis
- Sufficient disk space for the AOP data (can be several GB)
- Optional: An API token from the NEON data portal

Additionally, for data visualization you'll need:

```python
# Install required packages
# pip install rasterio matplotlib numpy
```

## Step 1: Check Available Dates

First, let's check what dates are available for the Canopy Height Model (CHM) data at Harvard Forest:

```python
from neon_utilities import list_available_dates

# Check available dates for CHM data at Harvard Forest
list_available_dates(
    dpid="DP3.30015.001",  # Canopy Height Model
    site="HARV"            # Harvard Forest
)
```

Output:
```
RELEASE-2023 Available Dates: 2017-06, 2019-08, 2021-07
```

We can see the CHM data is available for three years: 2017, 2019, and 2021. Let's work with the most recent data from 2021.

## Step 2: Explore Tile Extents

Now, let's check the tile extents for the 2021 CHM data:

```python
from neon_utilities import get_aop_tile_extents

# Get tile extents for CHM data at Harvard Forest in 2021
tile_coordinates = get_aop_tile_extents(
    dpid="DP3.30015.001",  # Canopy Height Model
    site="HARV",           # Harvard Forest
    year="2021"
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

This shows us that there are 6 tiles covering the Harvard Forest site.

## Step 3: Download Specific Tiles

Let's say our research plot is located at UTM coordinates (732500, 4713200). We'll download just the tile containing this location:

```python
from neon_utilities import by_tile_aop

# Download the specific tile containing our coordinates
by_tile_aop(
    dpid="DP3.30015.001",  # Canopy Height Model
    site="HARV",           # Harvard Forest
    year="2021",
    easting=732500,        # UTM Easting coordinate
    northing=4713200,      # UTM Northing coordinate
    buffer=0,              # No buffer around the coordinates
    savepath="./data"      # Directory to save the data
)
```

The function will report the total file size and ask for confirmation before downloading. After confirming, it will download the tile containing our coordinates (732000_4713000).

If you want to download multiple tiles or add a buffer around your coordinates, you can do so:

```python
# Download multiple tiles with a buffer
by_tile_aop(
    dpid="DP3.30015.001",
    site="HARV",
    year="2021",
    easting=[732500, 733200],     # Multiple UTM Easting coordinates
    northing=[4713200, 4712800],  # Multiple UTM Northing coordinates
    buffer=100,                   # 100m buffer around each coordinate
    savepath="./data"
)
```

## Step 4: Load and Visualize the Data

Now that we've downloaded the data, let's load and visualize it using rasterio and matplotlib:

```python
import os
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
import numpy as np

# Find the downloaded CHM file
data_dir = "./data/DP3.30015.001"
chm_files = []

for root, dirs, files in os.walk(data_dir):
    for file in files:
        if file.endswith('.tif') and '2021' in file and 'CHM' in file:
            chm_files.append(os.path.join(root, file))

# Load and display the CHM data
if chm_files:
    with rasterio.open(chm_files[0]) as src:
        chm_data = src.read(1)
        
        # Mask no-data values
        chm_data = np.ma.masked_where(chm_data <= 0, chm_data)
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 10))
        img = ax.imshow(chm_data, cmap='viridis')
        cbar = plt.colorbar(img, ax=ax)
        cbar.set_label('Canopy Height (m)')
        ax.set_title('NEON Canopy Height Model - Harvard Forest (2021)')
        plt.axis('off')
        plt.tight_layout()
        plt.show()
        
        # Basic statistics
        valid_data = chm_data[~chm_data.mask]
        print(f"Min height: {valid_data.min():.2f} m")
        print(f"Max height: {valid_data.max():.2f} m")
        print(f"Mean height: {valid_data.mean():.2f} m")
else:
    print("No CHM files found. Check the download path and file names.")
```

This will display a visualization of the canopy height model and print some basic statistics about the canopy heights in our area of interest.

## Step 5: Download a Full Site (Optional)

If you need all the data for a site, you can use `by_file_aop` instead:

```python
from neon_utilities import by_file_aop

# Download all CHM data for Harvard Forest in 2021
by_file_aop(
    dpid="DP3.30015.001",  # Canopy Height Model
    site="HARV",           # Harvard Forest
    year="2021",
    savepath="./data"
)
```

Be aware that this will download all tiles for the entire site, which will be much larger than downloading specific tiles.

## Advanced Analysis

Once you have the CHM data, you can perform various analyses such as:

- Forest structure characterization
- Biomass estimation
- Change detection (if you download data from multiple years)
- Identification of canopy gaps
- Integration with field data

Here's a simple example of extracting height profiles for a transect:

```python
# Define a transect line from (x1, y1) to (x2, y2) in pixel coordinates
# This is just an example - adjust for your actual data
x1, y1 = 100, 100
x2, y2 = 400, 400

# Extract the profile
n_points = 500
x = np.linspace(x1, x2, n_points).astype(np.int)
y = np.linspace(y1, y2, n_points).astype(np.int)
z = chm_data[y, x]

# Plot the profile
plt.figure(figsize=(10, 6))
plt.plot(np.arange(len(z)), z)
plt.title('Canopy Height Profile Along Transect')
plt.xlabel('Distance along transect (pixels)')
plt.ylabel('Canopy Height (m)')
plt.grid(True)
plt.show()
```

## Combining with Other NEON Products

For a comprehensive analysis, you might want to integrate the AOP data with ground-based observations. For example, you could download vegetation structure data:

```python
from neon_utilities import load_by_product

# Download vegetation structure data for the same site and time period
veg_data = load_by_product(
    dpid="DP1.10098.001",  # Vegetation structure
    site="HARV",           # Harvard Forest
    startdate="2021-01",
    enddate="2021-12"
)

# Access the data tables
veg_structure = veg_data["vst_apparentindividual"]
```

This allows you to validate remote sensing measurements with field observations.

## Conclusion

In this tutorial, we've demonstrated how to:

1. Check available dates for AOP data at a NEON site
2. Explore tile extents to locate our area of interest
3. Download specific tiles to save storage space
4. Load and visualize the canopy height model
5. Perform basic analysis on the data

For more complex analyses, you might want to use specialized geospatial packages like GeoPandas, GDAL, or ArcPy depending on your specific research questions.

## Resources

- [NEON Data Portal](https://data.neonscience.org/)
- [NEON AOP Data Products Catalog](https://www.neonscience.org/data-collection/airborne-remote-sensing)
- [Rasterio Documentation](https://rasterio.readthedocs.io/)
- [Google Earth Engine](https://earthengine.google.com/) (alternative platform for working with geospatial data)
