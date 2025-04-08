# API Token Setup

The NEON Data Portal uses API tokens to manage access rates to data resources. While tokens are optional, using a personal API token is highly recommended, especially if you plan to download large amounts of data or use the API frequently.

## Benefits of Using an API Token

- **Higher Rate Limits**: Authenticated users get 10,000 requests per hour compared to 200 requests per hour for anonymous users
- **Access to Latest Data**: Some data (particularly LATEST releases) may only be available to authenticated users
- **Improved Performance**: Higher download speeds for large data files

## Creating an API Account and Token

### Step 1: Register for an Account

1. Visit the [NEON Data Portal](https://data.neonscience.org/)
2. Click on "Login" in the top-right corner
3. Click "Register" to create a new account
4. Fill out the registration form and submit

### Step 2: Generate an API Token

1. Log in to your NEON Data Portal account
2. Click on your username in the top-right corner
3. Select "My Profile" from the dropdown menu
4. In your profile page, select the "API Tokens" tab
5. Click "Generate New Token"
6. Enter a description for your token (e.g., "Python API Access")
7. Click "Generate Token"
8. Copy your token and store it securely - you won't be able to view it again!

![API Token Generation](../assets/api-token-generation.png)

## Using Your API Token

### Using the Token in Function Calls

Include your token in API calls by adding the `token` parameter:

```python
from neon_utilities import zips_by_product

# Download data using your API token
zips_by_product(
    dpid="DP1.10003.001",
    site="HARV",
    token="your-api-token-here"
)
```

### Environment Variable (Recommended)

For better security, store your token as an environment variable:

```bash
# On Linux/macOS
export NEON_API_TOKEN="your-api-token-here"

# On Windows (Command Prompt)
set NEON_API_TOKEN=your-api-token-here

# On Windows (PowerShell)
$env:NEON_API_TOKEN = "your-api-token-here"
```

Then use it in your code:

```python
import os
from neon_utilities import zips_by_product

# Get token from environment variable
token = os.environ.get('NEON_API_TOKEN')

# Use the token in function calls
zips_by_product(
    dpid="DP1.10003.001",
    site="HARV",
    token=token
)
```

### Configuration File (For Local Development)

Create a configuration file (e.g., `config.py`) to store your token:

```python
# config.py
NEON_API_TOKEN = "your-api-token-here"
```

Make sure to add this file to `.gitignore` to avoid accidentally sharing your token:

```
# .gitignore
config.py
```

Then import the token in your code:

```python
from config import NEON_API_TOKEN
from neon_utilities import zips_by_product

zips_by_product(
    dpid="DP1.10003.001",
    site="HARV",
    token=NEON_API_TOKEN
)
```

## Verifying Token Usage

To check if your token is being recognized correctly:

```python
from neon_utilities.helper_mods.api_helpers import get_api

# Test with a simple API call
response = get_api(
    api_url="https://data.neonscience.org/api/v0/products/DP1.10003.001",
    token="your-api-token-here"
)

# Check rate limit headers
print(f"Rate limit: {response.headers.get('x-ratelimit-limit')}")
```

If your token is recognized, you should see `"Rate limit: 10000"` in the output. If it shows `"Rate limit: 200"`, the token was not recognized.

## Token Security Best Practices

1. **Never hardcode tokens** directly in scripts you share with others
2. **Don't commit tokens** to version control systems like Git
3. **Treat your token like a password** - if compromised, generate a new one
4. **Rotate tokens periodically**, especially for production applications
5. **Set environment variables** via a secure process in production environments

## Troubleshooting

### Token Not Recognized

If your token isn't being recognized:

1. Verify you're using the correct token by generating a new one
2. Check for leading/trailing whitespace in your token string
3. Ensure your token hasn't expired or been revoked

### Rate Limit Exceeded

If you encounter rate limit errors despite using a token:

1. Check if multiple processes are sharing the same token
2. Implement exponential backoff for retries
3. Consider spacing out your requests

## Next Steps

With your API token set up, you're ready to:

- Learn about [basic usage](basic-usage.md) of the package
- Explore the [core functions](../functions/tabular/zips_by_product.md)
- Try the [tutorials](../tutorials/download-process-tabular.md)
