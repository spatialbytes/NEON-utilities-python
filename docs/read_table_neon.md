# read_table_neon

The `read_table_neon` function reads a NEON data table with correct data types for each variable based on the NEON variables file. This ensures that dates, numeric values, and other fields are properly typed in your analysis.

## Function Signature

```python
def read_table_neon(data_file,
                    var_file):
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `data_file` | str | Filepath to a data table to load |
| `var_file` | str | Filepath to a variables file matching the data table |

## Returns

A pandas DataFrame of the NEON data table, with column data types assigned according to the information in the variables file.

## Description

The `read_table_neon` function solves a common problem when working with NEON data: ensuring that each column has the correct data type. NEON data tables contain various types of data (e.g., strings, integers, floating-point numbers, dates), and standard CSV reading functions typically don't assign optimal data types.

This function reads a NEON data table and a corresponding variables file, which contains metadata about each field's data type. It then uses this information to assign the appropriate data type to each column in the resulting pandas DataFrame.

Data types handled include:
- Floating-point numbers (`real` type in variables file)
- Integers (`integer`, `unsigned integer`, `signed integer` types)
- Strings (`string`, `uri` types)
- Dates and timestamps (`dateTime` type with various formats)

## Examples

### Basic Usage

```python
from neon_utilities import read_table_neon

# Read a data table with correct data types
bird_counts = read_table_neon(
    data_file="./data/stacked/stackedFiles/brd_countdata.csv",
    var_file="./data/stacked/stackedFiles/variables_10003.csv"
)

print(bird_counts.dtypes)  # Check the data types
print(bird_counts.head())  # Display the first few rows
```

### After Downloading with load_by_product

This function is particularly useful when working with data that wasn't loaded using `load_by_product()`, which automatically handles data types:

```python
from neon_utilities import zips_by_product, stack_by_table, read_table_neon
import os

# Download data
zips_by_product(
    dpid="DP1.10003.001",
    site="HARV",
    startdate="2019-01",
    enddate="2019-12",
    savepath="./data"
)

# Stack the data
stack_by_table(
    filepath="./data/filesToStack10003",
    savepath="./data/stacked"
)

# Read with correct data types
output_dir = "./data/stacked/stackedFiles"
bird_counts = read_table_neon(
    data_file=os.path.join(output_dir, "brd_countdata.csv"),
    var_file=os.path.join(output_dir, "variables_10003.csv")
)

# Check data types
print(bird_counts.dtypes)
```

### For Time Series Analysis

Proper data typing is especially important for time series analysis:

```python
from neon_utilities import read_table_neon
import matplotlib.pyplot as plt
import pandas as pd

# Read temperature data with correct types
temp_data = read_table_neon(
    data_file="./data/stacked/stackedFiles/TAAT_30min.csv",
    var_file="./data/stacked/stackedFiles/variables_00002.csv"
)

# Confirm datetime type
print(type(temp_data["startDateTime"].iloc[0]))  # Should be pandas.Timestamp

# Plot time series data
plt.figure(figsize=(12, 6))
plt.plot(temp_data["startDateTime"], temp_data["tempSingleMean"])
plt.title("Air Temperature at Harvard Forest")
plt.xlabel("Date")
plt.ylabel("Temperature (°C)")
plt.grid(True)
plt.tight_layout()
plt.show()
```

## Error Handling

The function performs several checks to ensure correct operation:

1. Validates that the variables file is a NEON variables file
2. Checks that most fields in the data table have a corresponding entry in the variables file
3. Falls back to reading as strings if data types can't be assigned correctly

If the variables file doesn't match the data file, the function will return an error message.

## Notes

### Date Handling

The function handles various date and time formats:

- ISO 8601 timestamps (`yyyy-MM-dd'T'HH:mm:ss'Z'`)
- Date-only formats (`yyyy-MM-dd`)
- Year-only formats (`yyyy`)

All timestamps are converted to UTC timezone.

### Performance

This function uses PyArrow for efficient reading of CSV files and data type conversion, which provides better performance than standard pandas CSV reading functions, especially for large files.

### When to Use

Although `load_by_product()` and `stack_by_table(savepath="envt")` automatically handle data types, you should use `read_table_neon()` when:

1. Reading individual files from a stacked dataset
2. Reading NEON data files from other sources
3. Re-reading data that might have lost its correct typing

## Related Functions

- [`load_by_product()`](../tabular/load_by_product.md): Download and load data with correct types
- [`stack_by_table()`](../tabular/stack_by_table.md): Stack data with option to return typed data
- [`cast_table_neon()`](./cast_table_neon.md): Cast an existing table to correct data types
