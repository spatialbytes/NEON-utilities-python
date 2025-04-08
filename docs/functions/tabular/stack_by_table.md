# Combine Data Files

The `stack_by_table` function joins data files in a zipped or unzipped NEON data package into unified tables by data type. This function is a critical part of the workflow after downloading data with [`zips_by_product()`](zips_by_product.md).

## Function Signature

```python
def stack_by_table(filepath,
                   savepath=None,
                   save_unzipped_files=False,
                   progress=True,
                   cloud_mode=False):
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `filepath` | str | The location of the zip file or downloaded files directory |
| `savepath` | str, optional | The location to save the output files; if `None`, outputs to the same location as the input |
| `save_unzipped_files` | bool, optional | Should the unzipped monthly data folders be retained? Defaults to `False` |
| `progress` | bool, optional | Should the function display progress bars? Defaults to `True` |
| `cloud_mode` | bool, optional | Use cloud mode to transfer files cloud-to-cloud? Defaults to `False` |

## Returns

If `savepath="envt"` is specified, the function returns a dictionary of pandas DataFrames, one for each table type. Otherwise, the function saves the stacked files to disk and returns `None`.

## Description

The `stack_by_table` function processes NEON data files downloaded via the NEON data portal or the [`zips_by_product()`](zips_by_product.md) function. It merges all data files by table type, creating one unified file for each table, which makes analysis much more straightforward.

This function handles the complex folder structure and file organization of NEON data packages, dealing with multiple sites, dates, and data tables. It also properly handles metadata files, collapsing them into a single reference.

The output includes not just the data tables, but also:
- Variables definition file
- Validation rules
- Citation information
- Issue log
- Readme file

## Examples

### Basic Usage

Stack files previously downloaded with `zips_by_product()`:

```python
from neonutilities import stack_by_table

# Stack the data files
stack_by_table(
    filepath="./data/filesToStack10003",  # Directory with downloaded bird data
    savepath="./data/stacked"             # Directory to save stacked files
)
```

This will create a directory `./data/stacked/stackedFiles` containing CSV files for each table in the data product.

### Stack and Load into Memory

To stack the data and load it directly into memory:

```python
# Stack and load data into memory
bird_data = stack_by_table(
    filepath="./data/filesToStack10003",
    savepath="envt"  # Special value to return data instead of saving to disk
)

# Access the data tables
bird_counts = bird_data["brd_countdata"]
bird_perpoint = bird_data["brd_perpoint"]

# Print the first few rows of count data
print(bird_counts.head())
```

### Stack a Zip File from the NEON Data Portal

You can also stack a zip file downloaded directly from the NEON data portal:

```python
# Stack a zip file
stack_by_table(
    filepath="./downloads/NEON_bird-data.zip",
    savepath="./data/stacked"
)
```

### Keep the Unzipped Files

If you want to keep the unzipped monthly data folders for reference:

```python
# Stack and keep unzipped files
stack_by_table(
    filepath="./data/filesToStack10003",
    savepath="./data/stacked",
    save_unzipped_files=True  # Keep the unzipped files
)
```

### Use with Cloud Mode

For cloud-to-cloud transfer (e.g., in Google Colab):

```python
# Stack using cloud mode
data = stack_by_table(
    filepath=file_list,  # List of file URLs from zips_by_product(cloud_mode=True)
    savepath="envt",
    cloud_mode=True
)
```

## Structure of the Output

The stacked files are organized by table type:

1. **Data tables**: Each data table from the original dataset is compiled into a single file named after the table
2. **Variables file**: Information about all variables in the dataset (`variables_####.csv`)
3. **Validation file**: Rules for validating data (`validation_####.csv`)
4. **Categorical codes**: Definitions for categorical values (`categoricalCodes_####.csv`)
5. **Issue log**: Known issues with the data (`issueLog_####.csv`)
6. **Readme**: General information about the data product (`readme_####.txt`)
7. **Citation**: Citation information for the data (`citation_####_RELEASE-20XX.txt`)

Where `####` is the five-digit number from the middle of the data product ID.

## Notes

### Data Types

The function uses the NEON variables file to assign the correct data types to each column when possible. If there are issues with data types, it will fall back to string types and provide warnings.

### Table Types

The function identifies different types of tables and handles them appropriately:

- **Site-date tables**: Tables with data from specific sites and dates
- **Site-all tables**: Tables with data for entire sites, regardless of date
- **Lab-specific tables**: Tables with data from specific analytical laboratories

### Windows Path Length Limitations

Windows has a default maximum path length of 260 characters, which can cause issues when working with nested directory structures. If you encounter path-related errors:

1. Move your working directory closer to the root directory
2. Enable long path support in Windows

### Memory Considerations

When using `savepath="envt"` to load data into memory, be aware of potential memory limitations, especially for large datasets. Consider using smaller date ranges or specific tables if memory is a concern.

## Related Functions

- [`zips_by_product()`](zips_by_product.md): Download data packages
- [`load_by_product()`](load_by_product.md): Download and load data directly into memory
- [`read_table_neon()`](../processing/read_table_neon.md): Read NEON tables with correct data types
