#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import get_api
import re
import json
import sys

def zips_by_product(dpID, site, startdate, enddate, package="basic", 
                    release="current", include_provisional=False, 
                    token=None, savepath=None):
    """
    Download product-site-month data package files from NEON.
    
    Parameters
    --------
    dpID: Data product identifier in the form DP#.#####.###
    site: One or more 4-letter NEON site codes
    package: Download package to access, either basic or expanded
    startdate: Earliest date of data to download, in the form YYYY-MM
    enddate: Latest date of data to download, in the form YYYY-MM
    release: Data release to download. Defaults to the most recent release.
    include_provisional: Should Provisional data be returned in the download? Defaults to False.
    token: User specific API token (generated within neon.datascience user accounts). If omitted, download uses the public rate limit.
    savepath: File path of location to save data.

    Return
    --------
    A folder on the local drive containing the set of data package files meeting the input criteria.

    Example
    --------
    Download water quality data from COMO (Como Creek) in 2018

    >>> zips_by_product(dpID="DP1.20288.001",site="COMO",
                        startdate="2018-01", enddate="2018-12",
                        token=None, savepath="/mypath/Downloads")
    
    Created on Wed Jan 31 14:36:22 2024

    @author: clunch
    """

    # error message if dpID is not formatted correctly
    if not re.search(pattern="DP[1-4]{1}.[0-9]{5}.00[0-9]{1}", 
                 string=dpID):
        sys.exit(f"{dpID} is not a properly formatted data product ID. The correct format is DP#.#####.00#")
    
    # error message if package is not basic or expanded
    if not package in ["basic","expanded"]:
        sys.exit(f"{package} is not a valid package name. Package must be basic or expanded")
        
    # many more error messages and special handling needed here - see R package
    
    # query the /products endpoint for the product requested
    if release=="current" or release=="PROVISIONAL":
        prodreq = get_api(api_url="http://data.neonscience.org/api/v0/products/"+dpID,
                          token=token)
    else:
        prodreq = get_api(api_url="http://data.neonscience.org/api/v0/products/"
                          +dpID+"?release="+release, token=token)
    
    if prodreq==None:
        sys.exit("Data product was not found or API was unreachable.")
        
    avail=prodreq.json()
    
    # error message if product or data not found
    try:
        avail["error"]["status"]
        if release=="LATEST":
            sys.exit(f"No data found for product {dpID}. LATEST data requested; check that token is valid for LATEST access.")
        else:
            if re.search(pattern="Release not found", string=avail["error"]["detail"]):
                sys.exit(f"Release not found. Valid releases for product {dpID} are {avail['data']['validReleases']}")
            else:
                sys.exit(f"No data found for product {dpID}")
    except:
        pass
    
    # check that token was used
    if 'x-ratelimit-limit' in prodreq.headers and not token==None:
        if prodreq.headers.get('x-ratelimit-limit')==200:
            print("API token was not recognized. Public rate limit applied.\n")
    
    


