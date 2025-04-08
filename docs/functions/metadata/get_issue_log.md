# Check Known Issues

The `get_issue_log` function retrieves the issue log for a specified NEON data product. This is important for understanding any known issues, corrections, or changes that may affect data interpretation.

## Function Signature

```python
def get_issue_log(dpid, token=None):
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `dpid` | str | The data product identifier in the form DP#.#####.###, e.g., "DP1.10003.001" |
| `token` | str, optional | User-specific API token; if omitted, uses the public rate limit |

## Returns

A pandas DataFrame containing the issue log for the specified data product. The DataFrame columns vary depending on the data product type:

For most data products, the columns are:
- `id`: Unique identifier for the issue
- `parentIssueID`: Identifier for a parent issue, if applicable
- `issueDate`: Date the issue was identified
- `resolvedDate`: Date the issue was resolved, if applicable
- `dateRangeStart`: Start date for the affected data
- `dateRangeEnd`: End date for the affected data
- `locationAffected`: Sites or locations affected by the issue
- `issue`: Description of the issue
- `resolution`: Description of how the issue was resolved, if applicable

For bundled eddy covariance data products (DP4.00200.001), an additional column is included:
- `dpid`: The data product ID of the sub-data product affected by the issue

## Description

The `get_issue_log` function queries the NEON API to retrieve the changelog for a specified data product, which serves as an issue log. This issue log contains information about known issues, corrections, updates, or changes to the data product that may affect data interpretation and analysis.

This function is particularly valuable when working with NEON data in scientific research, as it provides transparency about data quality and processing decisions. Always check the issue log when working with NEON data to understand any limitations or special considerations for your analysis.

## Examples

### Basic Usage

Retrieve the issue log for bird survey data:

```python
from neonutilities import get_issue_log

# Get the issue log for breeding landbird point counts
issue_log = get_issue_log(dpid="DP1.10003.001")

# Display the first few issues
print(issue_log.head())

# Count issues by site
site_counts = issue_log['locationAffected'].value_counts()
print(site_counts)
```

### With API Token

Use an API token for better performance and higher rate limits:

```python
import os
from neonutilities import get_issue_log

# Get token from environment variable
token = os.environ.get('NEON_API_TOKEN')

# Get issue log with token
issue_log = get_issue_log(
    dpid="DP1.10003.001",
    token=token
)
```

### Find Issues for a Specific Site

Filter the issue log to find issues affecting a specific site:

```python
from neonutilities import get_issue_log

# Get the issue log
issue_log = get_issue_log(dpid="DP1.10003.001")

# Filter for a specific site (Harvard Forest)
harv_issues = issue_log[issue_log['locationAffected'].str.contains('HARV', na=False)]
print(f"Found {len(harv_issues)} issues for Harvard Forest:")
for i, issue in harv_issues.iterrows():
    print(f"Issue: {issue['issue']}")
    print(f"Resolution: {issue['resolution']}")
    print(f"Date range: {issue['dateRangeStart']} to {issue['dateRangeEnd']}")
    print("---")
```

### Find Unresolved Issues

Find issues that have not yet been resolved:

```python
from neonutilities import get_issue_log
import pandas as pd

# Get the issue log
issue_log = get_issue_log(dpid="DP1.10003.001")

# Find unresolved issues (where resolvedDate is NaN)
unresolved = issue_log[pd.isna(issue_log['resolvedDate'])]
print(f"Found {len(unresolved)} unresolved issues")
```

### Working with Bundled Eddy Covariance Data

For the bundled eddy covariance data product, the issue log includes issues from all component products:

```python
from neonutilities import get_issue_log

# Get the issue log for bundled eddy covariance data
issue_log = get_issue_log(dpid="DP4.00200.001")

# Group by sub-product and count issues
issue_counts = issue_log.groupby('dpid').size()
print("Issue counts by component product:")
print(issue_counts)
```

## Integration with Data Analysis

The issue log can be crucial for cleaning and filtering data appropriately:

```python
from neonutilities import load_by_product, get_issue_log
import pandas as pd

# Download bird survey data
bird_data = load_by_product(
    dpid="DP1.10003.001",
    site="HARV",
    startdate="2019-01",
    enddate="2019-12"
)

# Get the issue log
issue_log = get_issue_log(dpid="DP1.10003.001")

# Filter for issues affecting Harvard Forest in 2019
harv_2019_issues = issue_log[
    (issue_log['locationAffected'].str.contains('HARV', na=False)) &
    (pd.to_datetime(issue_log['dateRangeStart']) <= pd.Timestamp('2019-12-31')) &
    ((pd.isna(issue_log['dateRangeEnd'])) |
     (pd.to_datetime(issue_log['dateRangeEnd']) >= pd.Timestamp('2019-01-01')))
]

# Display relevant issues before analyzing data
if len(harv_2019_issues) > 0:
    print("Warning: The following issues affect this dataset:")
    for i, issue in harv_2019_issues.iterrows():
        print(f"- {issue['issue']}")
        if not pd.isna(issue['resolution']):
            print(f"  Resolution: {issue['resolution']}")

# Now analyze data with awareness of the issues
bird_counts = bird_data["brd_countdata"]
```

## Notes

- The issue log is automatically included when you use `stack_by_table()` or `load_by_product()`, saved as `issueLog_XXXXX.csv` or as an entry in the returned dictionary.
- The issue log is an important resource for data quality assurance and should be consulted when making scientific interpretations.
- For some data products, especially newer ones, the issue log may be empty if no issues have been reported.
- The timestamps in the issue log are typically in UTC time.

## Related Functions

- [`get_citation()`](get_citation.md): Get citation information for NEON data
- [`load_by_product()`](../tabular/load_by_product.md): Download and load data directly into memory
- [`stack_by_table()`](../tabular/stack_by_table.md): Stack downloaded data into unified tables
