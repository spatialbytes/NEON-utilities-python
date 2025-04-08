# Data Processing Functions

This section covers functions designed to help process NEON data after it has been downloaded. These functions ensure that data is properly formatted, has the correct data types, and is optimally structured for analysis.

## Available Functions

| Function | Description |
|----------|-------------|
| [`read_table_neon()`](read_table_neon.md) | Reads NEON data tables with correct data types based on the variables file |
| [`unzip_and_stack()`](unzip_and_stack.md) | Helper functions for processing downloaded data packages |

## When to Use Each Function

- **`read_table_neon()`**: Use when you need to read a NEON data table with the correct data types. This is particularly important for working with date/time fields, numeric values, and categorical variables.

- **`unzip_and_stack()`**: This module contains helper functions used by `stack_by_table()` and `load_by_product()`. While you typically won't use these functions directly, understanding them can be helpful for customizing data processing workflows.

## Importance of Proper Data Processing

Proper data processing is critical for accurate analysis. NEON data tables contain various types of data, and ensuring each field has the correct data type is essential for:

1. **Date/Time operations**: Timestamps and dates must be properly formatted for time series analysis
2. **Numeric calculations**: Numeric fields need the correct data type for mathematical operations
3. **Categorical analysis**: Categorical variables should be properly identified for statistical analysis
4. **Data validation**: Proper data types help identify out-of-range or invalid values

## Example

```python
from neon_utilities import read_table_neon
import os
import pandas as pd
import matplotlib.pyplot as plt

# Path to data and variables files
data_file = "./data/stacked/stackedFiles/TAAT_30min.csv"
var_file = "./data/stacked/stackedFiles/variables_00002.csv"

# Read the data with correct data types
temp_data = read_table_neon(
    data_file=data_file,
    var_file=var_file
)

# Check data types
print("Data types:")
print(temp_data.dtypes)

# Confirm datetime type
print("\nType of startDateTime:", type(temp_data["startDateTime"].iloc[0]))

# Plot time series data
plt.figure(figsize=(12, 6))
plt.plot(temp_data["startDateTime"], temp_data["tempSingleMean"])
plt.title("Air Temperature Time Series")
plt.xlabel("Date")
plt.ylabel("Temperature (°C)")
plt.grid(True)
plt.tight_layout()
plt.show()
```

## Working with Large Files

NEON data files can be large, especially for sensor data with high temporal resolution or data spanning multiple sites and years. The processing functions are designed to handle large files efficiently:

- **PyArrow backend**: `read_table_neon()` uses PyArrow for efficient CSV reading
- **Chunked processing**: The stacking functions process files in chunks for better memory management
- **Parallel processing**: Some operations can take advantage of multiple cores for faster processing

## Related Resources

- [NEON Data Structure Tutorial](../../tutorials/working-with-large-files.md)
- [Basic Usage Guide](../../getting-started/basic-usage.md)
- [API Reference](../../api/reference.md)
