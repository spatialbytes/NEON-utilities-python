# Tabular Data Functions

This section covers the functions designed to work with NEON's tabular data products, which include Observational (OS) and Instrumented (IS) data. These functions allow you to download, process, and analyze data from NEON's ground-based collection systems.

## Available Functions

| Function | Description |
|----------|-------------|
| [`zips_by_product()`](zips_by_product.md) | Downloads data packages for specified products, sites, and dates |
| [`load_by_product()`](load_by_product.md) | Downloads and loads data directly into memory as pandas DataFrames |
| [`stack_by_table()`](stack_by_table.md) | Stacks downloaded data files into unified tables |

## When to Use Each Function

- **`zips_by_product()`**: Use when you want to download data for long-term storage or when working with very large datasets that would be challenging to load entirely into memory.

- **`load_by_product()`**: Use for interactive data analysis when you want to download data and immediately begin working with it. This is the most convenient option for most users.

- **`stack_by_table()`**: Use when you already have data downloaded (either from `zips_by_product()` or from the NEON Data Portal) and need to combine the files into unified tables.

## Typical Workflow

A common workflow for working with NEON tabular data involves:

1. **Identify data product**: Determine which NEON data product contains the data you need
2. **Download data**: Use `zips_by_product()` or `load_by_product()` to acquire the data
3. **Process data**: If using `zips_by_product()`, use `stack_by_table()` to organize the data
4. **Analyze data**: Work with the unified data tables

## Example

```python
from neon_utilities import load_by_product
import matplotlib.pyplot as plt
import pandas as pd

# Download and load soil temperature data
soil_temp_data = load_by_product(
    dpid="DP1.00041.001",  # Soil temperature
    site="HARV",           # Harvard Forest
    startdate="2019-01",
    enddate="2019-12"
)

# Access the 30-minute data
soil_temp_30min = soil_temp_data["ST_30_minute"]

# Calculate daily averages
soil_temp_30min['date'] = pd.to_datetime(soil_temp_30min['endDateTime']).dt.date
daily_avg = soil_temp_30min.groupby('date')['soilTempMean'].mean().reset_index()

# Plot the data
plt.figure(figsize=(12, 6))
plt.plot(daily_avg['date'], daily_avg['soilTempMean'])
plt.title('Daily Average Soil Temperature at Harvard Forest (2019)')
plt.xlabel('Date')
plt.ylabel('Temperature (°C)')
plt.grid(True)
plt.tight_layout()
plt.show()
```

## Data Product Types

NEON tabular data falls into two main categories:

### Observational Data (OS)

- Collected by field staff
- Examples: bird surveys, plant diversity, tree measurements
- Typically organized by collection event
- Often has associated field notes and contextual information

### Instrumented Data (IS)

- Collected by automated sensors
- Examples: temperature, precipitation, soil moisture
- Organized by time interval (1-minute, 30-minute, daily)
- Usually has multiple quality flags

## Related Resources

- [NEON Data Portal](https://data.neonscience.org/)
- [NEON Data Product Catalog](https://data.neonscience.org/data-products/explore)
- [Basic Usage Guide](../../getting-started/basic-usage.md)
- [Downloading and Processing Tabular Data Tutorial](../../tutorials/download-process-tabular.md)
