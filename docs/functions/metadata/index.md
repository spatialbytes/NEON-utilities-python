# Metadata Functions

This section covers functions designed to work with NEON data metadata. These functions help you access important contextual information about NEON data products, including citation information and known data quality issues.

## Available Functions

| Function | Description |
|----------|-------------|
| [`get_citation()`](get_citation.md) | Retrieves proper citation information for NEON data in BibTeX format |
| [`get_issue_log()`](get_issue_log.md) | Retrieves the issue log for a data product to understand known issues |

## When to Use Each Function

- **`get_citation()`**: Use when preparing to cite NEON data in scientific publications, reports, or other academic work. Proper citation is essential for giving credit to data providers and supporting research reproducibility.

- **`get_issue_log()`**: Use to check for any known issues with the data product you're working with. This can help you understand limitations in the data and make informed decisions about data filtering or interpretation.

## Importance of Metadata

Metadata is critical for proper data usage and interpretation. By understanding the context in which data was collected, any known issues, and how to properly attribute the data, you can:

1. **Ensure research reproducibility** by clearly documenting data sources
2. **Account for data quality issues** in your analysis
3. **Give proper credit** to the organizations and individuals who collected the data
4. **Understand data collection methods** and limitations

## Example

```python
from neonutilities import get_citation, get_issue_log
import pandas as pd

# Get citation information for a data product
citation = get_citation(
    dpid="DP1.10003.001",  # Breeding landbird point counts
    release="RELEASE-2023"
)
print("Citation for publications:")
print(citation)

# Get the issue log to check for known issues
issue_log = get_issue_log(dpid="DP1.10003.001")

# Filter issues for a specific site
site_issues = issue_log[issue_log['locationAffected'].str.contains('HARV', na=False)]
if len(site_issues) > 0:
    print("\nKnown issues for Harvard Forest:")
    for i, issue in site_issues.iterrows():
        print(f"- {issue['issue']}")
        if pd.notna(issue['resolution']):
            print(f"  Resolution: {issue['resolution']}")
else:
    print("\nNo known issues for Harvard Forest")
```

## Included in Data Downloads

These metadata functions are particularly useful when working with data that didn't come directly from the `load_by_product()`, `zips_by_product()`, `by_file_aop()`, or `by_tile_aop()` functions, which automatically include citation and issue log information in the downloaded data.

## Related Resources

- [NEON Data Product Catalog](https://data.neonscience.org/data-products/explore)
- [NEON Data Citations Policy](https://www.neonscience.org/data-samples/data-policies-citation)
- [NEON Data Revisions & Releases](https://www.neonscience.org/data-samples/data-management/data-revisions-releases)
