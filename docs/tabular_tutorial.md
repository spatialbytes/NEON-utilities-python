# Tutorial: Downloading and Processing Tabular Data

This tutorial provides a comprehensive walkthrough of how to download, process, and analyze NEON tabular data using the NEON Utilities Python package. We'll focus on a complete workflow that includes data acquisition, cleaning, visualization, and basic analysis.

## Overview

In this tutorial, we'll:

1. Download bird observation data from multiple NEON sites
2. Process and clean the data
3. Explore the data structure and metadata
4. Visualize species diversity across sites
5. Perform a simple temporal trend analysis

## Prerequisites

- NEON Utilities package installed
- Basic familiarity with Python and pandas
- Optional: An API token from the NEON data portal

Additionally, you'll need these Python packages for data analysis:

```python
# Install required packages if you don't have them
# pip install pandas numpy matplotlib seaborn scipy
```

## Step 1: Download Bird Observation Data

Let's start by downloading breeding landbird point count data (DP1.10003.001) from three NEON sites over a three-year period:

```python
import os
from neon_utilities import load_by_product

# Set your API token (optional but recommended)
token = os.environ.get('NEON_API_TOKEN')  # You can also enter your token directly

# Download bird observation data
bird_data = load_by_product(
    dpid="DP1.10003.001",  # Breeding landbird point counts
    site=["HARV", "BART", "SCBI"],  # Harvard Forest, Bartlett, Smithsonian Conservation Biology Institute
    startdate="2019-01",
    enddate="2021-12",
    token=token
)

print("Downloaded data tables:")
for key in bird_data.keys():
    print(f"- {key}")
```

This will download all data for the breeding landbird point counts product from the three sites for the years 2019-2021 and load them directly into memory as pandas DataFrames.

## Step 2: Understand the Data Structure

The bird data product contains several tables. Let's examine what each contains:

```python
# Check the count data structure
print("Count data columns:")
print(bird_data["brd_countdata"].columns.tolist())
print(f"Count data shape: {bird_data['brd_countdata'].shape}")

# Check the per-point data structure
print("\nPer-point data columns:")
print(bird_data["brd_perpoint"].columns.tolist())
print(f"Per-point data shape: {bird_data['brd_perpoint'].shape}")

# Look at the variable definitions
var_subset = bird_data["variables_10003"][
    (bird_data["variables_10003"]["table"] == "brd_countdata") &
    (bird_data["variables_10003"]["fieldName"].isin(["taxonID", "taxonRank", "scientificName", "observationCount"]))
]
print("\nVariable definitions:")
print(var_subset[["fieldName", "description"]])
```

The main tables in this dataset are:
- `brd_countdata`: Individual bird observations
- `brd_perpoint`: Metadata about each sampling point
- `variables_10003`: Definitions of all variables in the dataset

## Step 3: Clean and Prepare the Data

Now, let's clean the data and prepare it for analysis:

```python
import pandas as pd
import numpy as np

# Extract the main tables we need
count_data = bird_data["brd_countdata"]
point_data = bird_data["brd_perpoint"]

# Check for missing values
print("Missing values in count data:")
print(count_data.isnull().sum()[count_data.isnull().sum() > 0])

# Convert dates to datetime
count_data["startDate"] = pd.to_datetime(count_data["startDate"])
point_data["startDate"] = pd.to_datetime(point_data["startDate"])

# Extract year for easier analysis
count_data["year"] = count_data["startDate"].dt.year
point_data["year"] = point_data["startDate"].dt.year

# Merge count data with point data to get more context
merged_data = pd.merge(
    count_data,
    point_data[["pointID", "siteID", "elevation", "nlcdClass", "startDate", "year"]],
    on=["pointID", "siteID", "startDate", "year"],
    how="left"
)

# Display the first few rows of the merged data
print("\nMerged data sample:")
print(merged_data.head())
```

## Step 4: Explore Species Diversity

Let's analyze bird species diversity across the three sites:

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Set up the plot style
plt.style.use('seaborn-whitegrid')
sns.set_palette("colorblind")

# Count species by site
species_by_site = merged_data.groupby(["siteID", "scientificName"]).size().reset_index(name="count")
unique_species_by_site = species_by_site.groupby("siteID").size().reset_index(name="unique_species")

# Create a bar plot
plt.figure(figsize=(10, 6))
ax = sns.barplot(x="siteID", y="unique_species", data=unique_species_by_site)
ax.set_title("Bird Species Richness by NEON Site (2019-2021)", fontsize=16)
ax.set_xlabel("Site", fontsize=14)
ax.set_ylabel("Number of Unique Species", fontsize=14)

# Add value labels
for i, v in enumerate(unique_species_by_site["unique_species"]):
    ax.text(i, v + 1, str(v), ha="center")

plt.tight_layout()
plt.savefig("species_richness_by_site.png", dpi=300)
plt.show()

# Top 10 most common species across all sites
top_species = merged_data.groupby("scientificName").size().reset_index(name="count")
top_species = top_species.sort_values("count", ascending=False).head(10)

plt.figure(figsize=(12, 6))
ax = sns.barplot(x="count", y="scientificName", data=top_species)
ax.set_title("Top 10 Most Common Bird Species Across All Sites (2019-2021)", fontsize=16)
ax.set_xlabel("Count", fontsize=14)
ax.set_ylabel("Species", fontsize=14)
plt.tight_layout()
plt.savefig("top_10_species.png", dpi=300)
plt.show()
```

## Step 5: Analyze Temporal Trends

Now, let's analyze how bird observations change over time:

```python
# Count observations by site and year
yearly_counts = merged_data.groupby(["siteID", "year"]).size().reset_index(name="observations")

# Create a line plot
plt.figure(figsize=(12, 6))
ax = sns.lineplot(x="year", y="observations", hue="siteID", data=yearly_counts, marker="o", markersize=10)
ax.set_title("Bird Observations by Year and Site", fontsize=16)
ax.set_xlabel("Year", fontsize=14)
ax.set_ylabel("Number of Observations", fontsize=14)
plt.xticks(yearly_counts["year"].unique())
plt.legend(title="Site")
plt.tight_layout()
plt.savefig("observations_by_year.png", dpi=300)
plt.show()

# Calculate species diversity (Shannon index) by site and year
def shannon_diversity(data, site, year):
    site_year_data = data[(data["siteID"] == site) & (data["year"] == year)]
    species_counts = site_year_data.groupby("scientificName").size()
    total = species_counts.sum()
    proportions = species_counts / total
    return -np.sum(proportions * np.log(proportions))

# Calculate diversity for each site and year
diversity_data = []
for site in yearly_counts["siteID"].unique():
    for year in yearly_counts["year"].unique():
        if len(merged_data[(merged_data["siteID"] == site) & (merged_data["year"] == year)]) > 0:
            diversity = shannon_diversity(merged_data, site, year)
            diversity_data.append({"siteID": site, "year": year, "diversity": diversity})

diversity_df = pd.DataFrame(diversity_data)

# Plot diversity trends
plt.figure(figsize=(12, 6))
ax = sns.lineplot(x="year", y="diversity", hue="siteID", data=diversity_df, marker="o", markersize=10)
ax.set_title("Shannon Diversity Index by Year and Site", fontsize=16)
ax.set_xlabel("Year", fontsize=14)
ax.set_ylabel("Shannon Diversity Index", fontsize=14)
plt.xticks(diversity_df["year"].unique())
plt.legend(title="Site")
plt.tight_layout()
plt.savefig("diversity_by_year.png", dpi=300)
plt.show()
```

## Step 6: Examine Environmental Factors

Let's analyze how elevation and land cover (NLCD class) might influence bird diversity:

```python
# Boxplot of observation counts by NLCD class
nlcd_counts = merged_data.groupby(["nlcdClass", "pointID"]).size().reset_index(name="count")

plt.figure(figsize=(14, 6))
ax = sns.boxplot(x="nlcdClass", y="count", data=nlcd_counts)
ax.set_title("Bird Observations by NLCD Land Cover Class", fontsize=16)
ax.set_xlabel("NLCD Class", fontsize=14)
ax.set_ylabel("Observations per Point", fontsize=14)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("observations_by_nlcd.png", dpi=300)
plt.show()

# Scatter plot of elevation vs. observations
elevation_counts = merged_data.groupby(["pointID", "elevation"]).size().reset_index(name="count")

plt.figure(figsize=(10, 6))
ax = sns.scatterplot(x="elevation", y="count", data=elevation_counts)
ax.set_title("Bird Observations vs. Elevation", fontsize=16)
ax.set_xlabel("Elevation (m)", fontsize=14)
ax.set_ylabel("Observations per Point", fontsize=14)

# Add regression line
sns.regplot(x="elevation", y="count", data=elevation_counts, scatter=False, ax=ax)

plt.tight_layout()
plt.savefig("observations_by_elevation.png", dpi=300)
plt.show()

# Calculate correlation
from scipy.stats import pearsonr
corr, p = pearsonr(elevation_counts["elevation"], elevation_counts["count"])
print(f"Correlation between elevation and observation count: {corr:.3f} (p={p:.3f})")
```

## Step 7: Check Data Quality Issues

Before drawing conclusions, let's check the issue log to see if there are any known issues with the data:

```python
# Check the issue log
issue_log = bird_data["issueLog_10003"]

# Filter for issues affecting our sites and dates
our_sites = ["HARV", "BART", "SCBI"]
site_issues = issue_log[
    issue_log["locationAffected"].apply(
        lambda x: any(site in str(x) for site in our_sites)
    )
]

if len(site_issues) > 0:
    print("Found issues affecting our sites:")
    for i, issue in site_issues.iterrows():
        print(f"- {issue['locationAffected']}: {issue['issue']}")
        print(f"  Resolution: {issue['resolution']}")
        print(f"  Date range: {issue['dateRangeStart']} to {issue['dateRangeEnd']}")
        print()
else:
    print("No issues found for our sites and date range.")
```

## Step 8: Export Processed Data

Finally, let's save our processed data for future use:

```python
# Save the merged data
merged_data.to_csv("neon_bird_data_2019_2021.csv", index=False)

# Save the species diversity data
diversity_df.to_csv("neon_bird_diversity_2019_2021.csv", index=False)

print("Data successfully exported to CSV files.")
```

## Advanced Analysis: Species Distribution Models

For a more advanced analysis, we could build a simple species distribution model using environmental variables:

```python
# This is a simplified example - in practice, you would want to use more variables
# and more sophisticated modeling approaches

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Let's predict the presence of one of the top species
top_species_name = top_species.iloc[0]["scientificName"]
print(f"Building distribution model for {top_species_name}")

# Create a binary target variable (present/absent)
species_data = merged_data.copy()
species_data["present"] = (species_data["scientificName"] == top_species_name).astype(int)

# Aggregate by sampling point (since the same point may have multiple observations)
point_species = species_data.groupby(["pointID", "siteID", "elevation", "nlcdClass", "year"]).agg(
    {"present": "max"}
).reset_index()

# Convert NLCD class to dummy variables
point_species_encoded = pd.get_dummies(point_species, columns=["nlcdClass", "siteID", "year"])

# Features and target
X = point_species_encoded.drop(["pointID", "present"], axis=1)
y = point_species_encoded["present"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Train a Random Forest classifier
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

# Make predictions
y_pred = rf.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f"Model accuracy: {accuracy:.3f}")
print("\nClassification report:")
print(classification_report(y_test, y_pred))

# Feature importance
feature_importance = pd.DataFrame({
    "Feature": X.columns,
    "Importance": rf.feature_importances_
}).sort_values("Importance", ascending=False)

plt.figure(figsize=(12, 6))
ax = sns.barplot(x="Importance", y="Feature", data=feature_importance.head(10))
ax.set_title(f"Top 10 Features for Predicting {top_species_name} Presence", fontsize=16)
ax.set_xlabel("Importance", fontsize=14)
ax.set_ylabel("Feature", fontsize=14)
plt.tight_layout()
plt.savefig("feature_importance.png", dpi=300)
plt.show()
```

## Conclusion

In this tutorial, we've demonstrated how to:

1. Download NEON bird observation data using the `load_by_product()` function
2. Understand and clean the data structure
3. Analyze species diversity across sites
4. Examine temporal trends
5. Investigate relationships with environmental factors
6. Check data quality using the issue log
7. Build a simple species distribution model

This workflow can be adapted to other NEON data products and research questions. The NEON Utilities package makes it straightforward to access and work with NEON data, allowing you to focus on scientific analysis rather than data handling.

## Additional Resources

- [NEON Data Portal](https://data.neonscience.org/)
- [Bird Data Product Details](https://data.neonscience.org/data-products/DP1.10003.001)
- [NEON Bird Sampling Protocol](https://www.neonscience.org/data-collection/breeding-landbird-abundance-and-diversity)
- [Avian Conservation and Ecology Journal](https://www.ace-eco.org/) - For publishing research using bird monitoring data
