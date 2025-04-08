# Installation

This guide will walk you through the process of installing the NEON Utilities Python package and its dependencies.

## Requirements

The NEON Utilities package requires:

- Python 3.8 or higher
- pip (Python package installer)

The package has the following dependencies:
- pandas
- numpy
- requests
- pyarrow
- tqdm
- importlib_resources

For working with remote sensing data, additional packages may be useful:
- rasterio
- matplotlib
- geopandas

## Installation Methods

### Installing from PyPI (Recommended)

The simplest way to install the NEON Utilities package is using pip:

```bash
pip install neon-utilities
```

To include optional dependencies for working with geospatial data:

```bash
pip install neon-utilities[geo]
```

### Installing from GitHub

To install the latest development version directly from GitHub:

```bash
pip install git+https://github.com/neonscience/neon-utilities-python.git
```

### Installing in a Virtual Environment (Recommended)

It's good practice to install Python packages in a virtual environment to avoid conflicts with other packages:

```bash
# Create a virtual environment
python -m venv neon-env

# Activate the virtual environment
# On Windows
neon-env\Scripts\activate
# On macOS/Linux
source neon-env/bin/activate

# Install the package
pip install neon-utilities
```

## Installation in Jupyter/Google Colab

To install directly in a Jupyter notebook or Google Colab:

```python
# Run this in a cell
!pip install neon-utilities
```

After installation, restart the kernel to ensure the package is properly loaded.

## Verifying Installation

You can verify the installation by importing the package:

```python
from neon_utilities import zips_by_product, by_file_aop

# Check the version
import neon_utilities
print(neon_utilities.__version__)
```

## Troubleshooting

### Common Issues

#### ImportError: Missing Dependencies

If you see an error like `ImportError: No module named 'some_dependency'`, install the missing dependency:

```bash
pip install some_dependency
```

#### Path Length Issues on Windows

Windows has a default maximum path length of 260 characters, which can cause issues when working with nested directory structures. If you encounter path-related errors:

1. Either move your working directory closer to the root directory
2. Or enable long path support in Windows by:
   - Running `regedit.exe`
   - Navigating to `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem`
   - Setting `LongPathsEnabled` to `1`
   - Restarting your computer

#### SSL Certificate Issues

If you encounter SSL certificate errors, update your certificates:

```bash
pip install --upgrade certifi
```

### Getting Help

If you encounter any issues that aren't covered here:

1. Check the [FAQ](../faq.md) page
2. Look for similar issues in the [GitHub repository](https://github.com/neonscience/neon-utilities-python/issues)
3. Open a new issue on GitHub with details about your problem

## Next Steps

Now that you have installed the NEON Utilities package, learn about:

- [Setting up an API token](api-token.md) (recommended for frequent use)
- [Basic usage examples](basic-usage.md)
- [Core functions](../functions/tabular/zips_by_product.md)
