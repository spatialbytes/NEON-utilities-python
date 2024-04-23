#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
import sys
import os
import importlib_resources
import pandas as pd
from .helper_mods.api_helpers import get_api
from .helper_mods.api_helpers import get_api_headers
from .helper_mods.api_helpers import get_zip_urls
from .helper_mods.api_helpers import get_tab_urls
from .helper_mods.api_helpers import download_urls
from .helper_mods.metadata_helpers import convert_byte_size
from . import __resources__


def zips_by_product(dpID, site="all", startdate=None, enddate=None, 
                    package="basic", release="current", 
                    timeindex="all", tabl="all", check_size=True,
                    include_provisional=False, progress=True,
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
    progress: Should the function display progress bars as it runs? Defaults to True
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

    @author: Claire Lunch
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
    
    # error messages for products that can't be downloaded by zips_by_product()
    # AOP products
    if dpID[4:5:1]==3 and dpID!="DP1.30012.001":
        print(f"{dpID} is a remote sensing data product. Use the by_file_aop() or by_tile_aop() function.")
        return None

    # Phenocam products
    if dpID=="DP1.00033.001" or dpID=="DP1.00042.001":
        print(f"{dpID} is a phenological image product, data are hosted by Phenocam.")
        return None
    
    # Aeronet product
    if dpID=="DP1.00043.001":
        print(f"Spectral sun photometer ({dpID}) data are hosted by Aeronet.")
        return None
    
    # DHP expanded package
    if dpID=="DP1.10017.001" and package=="expanded":
        print("Digital hemispherical images expanded file packages exceed programmatic download limits. Either download from the data portal, or download the basic package and use the URLs in the data to download the images themselves. Follow instructions in the Data Product User Guide for image file naming.")
        return None
    
    # individual SAE products
    if dpID in ['DP1.00007.001','DP1.00010.001','DP1.00034.001','DP1.00035.001',
                'DP1.00036.001','DP1.00037.001','DP1.00099.001','DP1.00100.001',
                'DP2.00008.001','DP2.00009.001','DP2.00024.001','DP3.00008.001',
                'DP3.00009.001','DP3.00010.001','DP4.00002.001','DP4.00007.001',
                'DP4.00067.001','DP4.00137.001','DP4.00201.001','DP1.00030.001']:
        print(f"{dpID} is only available in the bundled eddy covariance data product. Download DP4.00200.001 to access these data.")
        return None

    # allow for single sites
    if not isinstance(site, list):
        site=[site]

    # redirect for aqu met products and bundles
    shared_aquatic_file=(importlib_resources.files(__resources__)/"shared_aquatic.csv")
    shared_aquatic_df = pd.read_csv(shared_aquatic_file, index_col="site")
    
    if site!=["all"]:
        siter=[]
        indx=0
        for s in site:
            if s in shared_aquatic_df.index:
                ss=shared_aquatic_df.loc[s]
                if dpID in list(ss["product"]):
                    indx=indx+1
                    sx=list(ss["towerSite"][ss["product"]==dpID])
                    siter.append(sx)
                    if indx==1:
                        print(f"Some sites in your download request are aquatic sites where {dpID} is collected at a nearby terrestrial site. The sites you requested, and the sites that will be accessed instead, are listed below.")
                    print(f"{s} -> {''.join(sx)}")
                else:
                    siter.append([s])
            else:
                siter.append([s])
        siter=sum(siter, [])
    else:
        siter=site

    # error message if dates aren't formatted correctly
    # separate logic for each, to easily allow only one to be NA
    if startdate!=None:
        if re.search(pattern="[0-9]{4}-[0-9]{2}", string=startdate)==None:
            print("startdate and enddate must be either None or valid dates in the form YYYY-MM")
            return None
        
    if enddate!=None:
        if re.search(pattern="[0-9]{4}-[0-9]{2}", string=enddate)==None:
            print("startdate and enddate must be either None or valid dates in the form YYYY-MM")
            return None
        
    # can only specify timeindex xor tabl
    if timeindex!="all" and tabl!="all":
        print("Only one of timeindex or tabl can be specified, not both.")
        return None
    # consider adding warning message about using tabl=
    
    
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
    if siter!=["all"]:
        site_urls=[]
        for si in siter:
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
        ste=re.compile("20[0-9]{2}-[0-9]{2}")
        start_urls=[st for st in site_urls if ste.search(st).group(0)>=startdate]
    else:
        start_urls=site_urls
        
    # check for no results
    if len(start_urls)==0:
        print("There are no data at the selected date(s).")
        return None

    # subset by end date
    if enddate!=None:
        ete=re.compile("20[0-9]{2}-[0-9]{2}")
        end_urls=[et for et in start_urls if ete.search(et).group(0)<=enddate]
    else:
        end_urls=start_urls
    
    # check for no results
    if len(end_urls)==0:
        print("There are no data at the selected date(s).")
        return None
    
    # if downloading entire site-months, pass to get_zip_urls to query each month for url
    if timeindex=="all" and tabl=="all":
        durls=get_zip_urls(url_set=end_urls, package=package, release=release,
                             include_provisional=include_provisional, 
                             token=token, progress=progress)
    else:
        # if downloading by table or averaging interval, pass to get_tab_urls
        durls=get_tab_urls(url_set=end_urls, package=package, release=release,
                             include_provisional=include_provisional, 
                             timeindex=timeindex, tabl=tabl,
                             token=token, progress=progress)
    
    # check download size
    download_size=convert_byte_size(sum(durls["sz"]))
    if check_size:
        if input(f"Continuing will download {len(durls['z'])} files totaling approximately {download_size}. Do you want to proceed? (y/n) ") != "y":
            print("Download halted.")
            return None
    else:
        print(f"Downloading {len(durls['z'])} files totaling approximately {download_size}.")
    
    # set up folder to save to
    if savepath is None:
        savepath=os.getcwd()
    outpath=savepath+"/filesToStack"+dpID[4:9]+"/"
    
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    
    # download data from each url
    download_urls(url_set=durls, outpath=outpath,
                  token=token, progress=progress)
    
