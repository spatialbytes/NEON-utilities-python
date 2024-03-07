NEON-utilities-python/nupy
================

<!-- ****** Description ****** -->
Description
-----

A Python version of the neonUtilities R package is currently in development here. DO NOT attempt to install and use the Python package; core functionality is still in development. This README will be updated when the package is ready for public use.


## Package Build Instructions:
https://packaging.python.org/en/latest/tutorials/packaging-projects/

python3 -m pip install --upgrade build

to build: 

- run from external terminal or Anaconda prompt
- cd to directory where pyproject.toml is located, eg.
- cd GitHub/NEON-utilities-python/nupy

### Mac (Claire's configuration)
```
python3 -m build
```
### PC (Bridget's configuration)
```
python -m build --no-isolation
```

Build errored out when not using the --no-isolation, see this post: https://github.com/pypa/pip/issues/7730

The build environment is isolated from the system Python. If you want the build to "see" system installed packages, use --no-isolation.

### To re-build and re-install neonutilities, from the command line
Note: update the neonutilities package version # as needed, this is defined in the pyproject.toml file
```
pip uninstall -y neonutilities
python -m build --no-isolation
pip install "C:\Users\bhass\Documents\GitHubRepos\NEON-utilities-python\nupy\dist\neonutilities-0.0.2-py3-none-any.whl" -vvv
pip show -f neonutilities
```

## Testing Instructions
First, build the latest version of the package, and cd to GitHub/NEON-utilities-python/nupy

To run all tests in the tests directory:
```
pytest ./tests/
```

To run tests in a single test file:
```
pytest ./tests/test_aop_download.py
```

To run specific tests based off key words in a test file:
```
pytest ./tests/test_aop_download.py -k 'test_by_file_aop_invalid or test_by_tile_aop_invalid'
```