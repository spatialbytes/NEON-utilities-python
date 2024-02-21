#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
import sys
from .get_api import get_api

def zips_by_product(dpID, site="all", startdate=None, enddate=None, 
                    package="basic", release="current", 
                    include_provisional=False, 
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
        print(f"{dpID} is not a properly formatted data product ID. The correct format is DP#.#####.00#")
        return None
    
    # error message if package is not basic or expanded
    if not package in ["basic","expanded"]:
        print(f"{package} is not a valid package name. Package must be basic or expanded")
        return None
        
    # many more error messages and special handling needed here - see R package
    
    # query the /products endpoint for the product requested
    if release=="current" or release=="PROVISIONAL":
        prodreq = get_api(api_url="http://data.neonscience.org/api/v0/products/"
                          +dpID, token=token)
    else:
        prodreq = get_api(api_url="http://data.neonscience.org/api/v0/products/"
                          +dpID+"?release="+release, token=token)
    
    if prodreq==None:
        if release=="LATEST":
            print(f"No data found for product {dpID}. LATEST data requested; check that token is valid for LATEST access.")
            return None
        else:
            if release!="current" and release!="PROVISIONAL":
                rels = get_api(api_url="http://data.neonscience.org/api/v0/releases/", 
                               token=token)
                relj=rels.json()
                reld=relj["data"]
                rellist=[]
                for i in range(0, len(reld)):
                    rellist.append(reld[i]["release"])
                if not release in rellist:
                    print(f"Release not found. Valid releases are {rellist}")
                    return None
                else:
                    print("Data product was not found or API was unreachable.")
                    return None
            else:
                print("Data product was not found or API was unreachable.")
                return None
        
    avail=prodreq.json()
    
    # error message if product or data not found
    # I think this would never be called due to the way get_api() is set up
    try:
        avail["error"]["status"]
        print(f"No data found for product {dpID}")
        return None
    except:
        pass
    
    # check that token was used
    if 'x-ratelimit-limit' in prodreq.headers and not token==None:
        if prodreq.headers.get('x-ratelimit-limit')==200:
            print("API token was not recognized. Public rate limit applied.\n")
    
    # get data urls
    month_urls=[]
    for i in range(0, len(avail["data"]["siteCodes"])):
        month_urls.append(avail["data"]["siteCodes"][i]["availableDataUrls"])
    
    # check for no results
    if len(month_urls)==0:
        print("There are no data matching the search criteria.")
        return None
    
    # un-nest list
    month_urls=sum(month_urls, [])
            
    # subset by site
    if site!="all":
        site_urls=[]
        for si in site:
            se=re.compile(si)
            month_sub=[s for s in month_urls if se.search(s)]
            site_urls.append(month_sub)
        site_urls=sum(site_urls, [])
    else:
        site_urls=month_urls
    
    # check for no results
    if len(site_urls)==0:
        print("There are no data at the selected sites.")
        return None
    
    # subset by start date
    if startdate!=None:
        start_urls=[]
        ste=re.compile("20[0-9]{2}-[0-9]{2}")
        dateset=[ste.findall(st) for st in site_urls if ste.findall(st)]
        dateset=sum(dateset, [])
        start_urls=[site_urls for ds in dateset if ds>=startdate]
        # I think I need to un-nest again here
    else:
        start_urls=site_urls
        
    # check for no results
    if len(start_urls)==0:
        print("There are no data at the selected date(s).")
        return None

    
    # temporary output for testing
    return(start_urls)

