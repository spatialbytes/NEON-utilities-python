#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re
import time
import platform
import importlib.metadata
from tqdm import tqdm
from .metadata_helpers import get_recent

# Set global user agent
vers = importlib.metadata.version('neonutilities')
plat = platform.python_version()
osplat = platform.platform()

usera = f"neonutilities/{vers} Python/{plat} {osplat}"


def get_api(api_url,
            token=None):
    """

    Accesses the API with options to use the user-specific API token generated within neon.datascience user accounts.

    Parameters
    --------
    api_url: The API endpoint URL.
    token: User specific API token (generated within neon.datascience user accounts). Optional.

    Return
    --------
    API GET response containing status code and data that can be parsed into a json file

    Example
    --------
    Get the sample class for a surface water particulate stable isotope sample

    >>> sample_get = get_api(api_url='https://data.neonscience.org/api/v0/samples/classes?sampleTag=MCRA.SS.20230425.POM.1',token=None)

    Created on Fri Aug 30 2023

    @author: Zachary Nickerson
    """
    def get_status_code_meaning(status_code):
        return requests.status_codes._codes[status_code][0]
        
    # Check internet connection
    try:
        check_connection = requests.get("https://data.neonscience.org/",
                                        headers={"User-Agent": usera})
        if check_connection.status_code != 200:
            status_code = check_connection.status_code
            status_code_meaning = get_status_code_meaning(status_code)
            print(
                f"Request failed with status code {status_code}, indicating '{status_code_meaning}'\n")
            return None
    except:  # ConnectionError as e
        print("No internet connection detected. Cannot access NEON API.\n")
        return None

    # Make 5 request attempts. If the rate limit is reached, pause for the
    # burst reset time to try again.
    j = 1

    while (j <= 5):

        # Try making the request
        try:
            # Construct URL either with or without token
            if token is None:
                response = requests.get(api_url, 
                                        headers={"accept": "application/json",
                                        "User-Agent": usera})
            else:
                response = requests.get(
                    api_url, headers={"X-API-TOKEN": token, 
                                      "accept": "application/json",
                                      "User-Agent": usera})

            # Check for successful response
            if response.status_code == 200:

                if 'x-ratelimit-limit' in response.headers:
                    # Retry get request if rate limit is reached
                    limit_remain = response.headers.get(
                        'x-ratelimit-remaining')
                    #print(f"x-ratelimit-remaining: {limit_remain}")
                    
                    if int(limit_remain) < 1:
                        # Wait for the reset time
                        time_reset = response.headers.get('x-ratelimit-reset')
                        print(
                            f"Rate limit reached. Pausing for {time_reset} seconds to reset.\n")
                        time.sleep(int(time_reset))
                        # Increment loop to retry request attempt
                        j += 1

                    else:
                        # If rate limit is not reached, exit out of loop
                        j += 5

                else:
                    # If x-ratelimit-limit not found in headers, exit out of
                    # loop (don't need to retry because of rate-limit)
                    j += 5

            else:
                # Return nothing if request failed (status code is not 200)
                # Print the status code and it's meaning
                status_code_meaning = get_status_code_meaning(
                    response.status_code)
                print(
                    f"Request failed with status code {response.status_code}, indicating '{status_code_meaning}'\n")
                return None

            return response

        except:
            print(
                "No response. NEON API may be unavailable, check NEON data portal for outage alerts. If the problem persists and can't be traced to an outage alert, check your computer for firewall or other security settings preventing Python from accessing the internet.")
            return None


def get_api_headers(api_url,
            token=None):
    """

    Accesses the API with options to use the user-specific API token generated within neon.datascience user accounts.

    Parameters
    --------
    api_url: The API endpoint URL.
    token: User specific API token (generated within neon.datascience user accounts). Optional.

    Return
    --------
    The header only from an API GET response

    Created on Feb 26 2024

    Adapted from get_api
    @author: Zachary Nickerson
    @author: Claire Lunch
    """
    def get_status_code_meaning(status_code):
        return requests.status_codes._codes[status_code][0]
        
    # Check internet connection
    try:
        check_connection = requests.head("https://data.neonscience.org/",
                                        headers={"User-Agent": usera})
        if check_connection.status_code != 200:
            status_code = check_connection.status_code
            status_code_meaning = get_status_code_meaning(status_code)
            print(
                f"Request failed with status code {status_code}, indicating '{status_code_meaning}'\n")
            return None
    except:  # ConnectionError as e
        print("No internet connection detected. Cannot access NEON API.\n")
        return None

    # Make 5 request attempts. If the rate limit is reached, pause for the
    # burst reset time to try again.
    j = 1

    while (j <= 5):

        # Try making the request
        try:
            # Construct URL either with or without token
            if token is None:
                response = requests.head(api_url, 
                                        headers={"accept": "application/json",
                                        "User-Agent": usera})
            else:
                response = requests.head(
                    api_url, headers={"X-API-TOKEN": token, 
                                      "accept": "application/json",
                                      "User-Agent": usera})

            # Check for successful response
            if response.status_code == 200:

                if 'x-ratelimit-limit' in response.headers:
                    # Retry get request if rate limit is reached
                    limit_remain = response.headers.get(
                        'x-ratelimit-remaining')
                    #print(f"x-ratelimit-remaining: {limit_remain}")
                    # this is printing the rate limit every time the function is used
                    if int(limit_remain) < 1:
                        # Wait for the reset time
                        time_reset = response.headers.get('x-ratelimit-reset')
                        print(
                            f"Rate limit reached. Pausing for {time_reset} seconds to reset.\n")
                        time.sleep(int(time_reset))
                        # Increment loop to retry request attempt
                        j += 1

                    else:
                        # If rate limit is not reached, exit out of loop
                        j += 5

                else:
                    # If x-ratelimit-limit not found in headers, exit out of
                    # loop (don't need to retry because of rate-limit)
                    j += 5

            else:
                # Return nothing if request failed (status code is not 200)
                # Print the status code and it's meaning
                status_code_meaning = get_status_code_meaning(
                    response.status_code)
                print(
                    f"Request failed with status code {response.status_code}, indicating '{status_code_meaning}'\n")
                return None

            return response

        except:
            print(
                "No response. NEON API may be unavailable, check NEON data portal for outage alerts. If the problem persists and can't be traced to an outage alert, check your computer for firewall or other security settings preventing Python from accessing the internet.")
            return None


def get_zip_urls(url_set, 
                 package,
                 release,
                 include_provisional,
                 token=None,
                 progress=True):
    """

    Given a set of urls to the data endpoint of the NEON API, returns the set of zip file urls for each site-month package. Internal function, called by zips_by_product().

    Parameters
    --------
    url_set: A list of urls pointing to the data endpoint of the NEON API
    package: Data download package, basic or expanded.
    release: Data release to download.
    include_provisional: Should Provisional data be returned in the download?
    token: User specific API token (generated within neon.datascience user accounts). Optional.
    progress: Should the progress bar be displayed?

    Return
    --------
    List of urls pointing to zip files for each product-site-month.

    Created on Feb 23 2024

    @author: Claire Lunch
    """
    
    flnm=[]
    z=[]
    sz=[]
    rel=[]
    provflag=False
    if progress:
        print("Finding available files")
        
    for i in tqdm(range(0,len(url_set)), disable=not progress):
        
        # get list of files from data endpoint
        m_res=get_api(api_url=url_set[i], token=token)
        m_di=m_res.json()
        
        # only keep queried release
        if release!="current":
            if release!=m_di["data"]["release"]:
                continue
            
        # if include_provisional=F, exclude provisional
        if not include_provisional:
            if m_di["data"]["release"]=="PROVISIONAL":
                provflag=True
                continue
            
        # check for no files
        if not "packages" in list(m_di["data"]):
            print(f"No files found for site {m_di['data']['siteCode']} and month {m_di['data']['month']}")
            continue
            
        if len(m_di["data"]["packages"])==0:
            print(f"No files found for site {m_di['data']['siteCode']} and month {m_di['data']['month']}")
            continue
        
        # if package=expanded, check for expanded. reassign to basic if not found.
        if package=="expanded":
            if not package in [p["type"] for p in m_di["data"]["packages"]]:
                print(f"No expanded package found for site {m_di['data']['siteCode']} and month {m_di['data']['month']}. Basic package downloaded instead.")
                package="basic"
                
        # get zip file url and file name
        zi=[u["url"] for u in m_di["data"]["packages"] if u["type"]==package]
        h=get_api_headers(api_url=zi[0], token=token)
        fltp=re.sub(pattern='"', repl="", 
                    string=h.headers["content-disposition"])
        flnmi=re.sub(pattern="inline; filename=", repl="", string=fltp)
        
        # get file sizes
        szr=re.compile(package)
        flszs=[siz["size"] for siz in m_di["data"]["files"] if szr.search(siz["url"])]
        flszi=sum(flszs)
        
        # return url, file name, file size, and release
        flnm.append(flnmi)
        z.append(zi)
        sz.append(flszi)
        rel.append(m_di["data"]["release"])
    
    z=sum(z, [])
    zpfiles=dict(flnm=flnm, z=z, sz=sz, rel=rel)
        
    # provisional message
    if(provflag):
        print("Provisional data were excluded from available files list. To download provisional data, use input parameter include_provisional=True.")
        
    return(zpfiles)
      

def get_tab_urls(url_set, 
                 package,
                 release,
                 include_provisional,
                 timeindex,
                 tabl,
                 token=None,
                 progress=True):
    """

    Given a set of urls to the data endpoint of the NEON API, and averaging interval or table name criteria, returns the set of urls to individual files for each site-month package. Internal function, called by zips_by_product().

    Parameters
    --------
    url_set: A list of urls pointing to the data endpoint of the NEON API
    package: Data download package, basic or expanded.
    release: Data release to download.
    include_provisional: Should Provisional data be returned in the download?
    timeindex: Averaging interval of data to download.
    tabl: Table name of data to download.
    token: User specific API token (generated within neon.datascience user accounts). Optional.
    progress: Should the progress bar be displayed?

    Return
    --------
    List of urls pointing to files for each product-site-month and subset.

    Created on Mar 23 2024

    @author: Claire Lunch
    """
    
    # initiate file lists
    flnm=[]
    z=[]
    sz=[]
    rel=[]
    varf=[]
    rdme=[]
    sp=[]
    
    # create regular expressions for file finding
    vr=re.compile("variables")
    rdr=re.compile("readme")
    spr=re.compile("sensor_positions")
    
    if timeindex!="all":
        tt=re.compile(str(timeindex)+"min|"+str(timeindex)+"_min|science_review_flags")
        
    if tabl!="all":
        tb=re.compile("[.]"+tabl+"[.]")
    
    provflag=False
    if progress:
        print("Finding available files")
                
    for i in tqdm(range(0,len(url_set)), disable=not progress):
        
        # get list of files from data endpoint
        m_res=get_api(api_url=url_set[i], token=token)
        m_di=m_res.json()
        
        # only keep queried release
        if release!="current":
            if release!=m_di["data"]["release"]:
                continue
            
        # if include_provisional=F, exclude provisional
        if not include_provisional:
            if m_di["data"]["release"]=="PROVISIONAL":
                provflag=True
                continue
        
        # subset to package. switch to basic if expanded not available
        # package name isn't always in file name (lab files, SRFs) but is always in url
        pr=re.compile(package)
        flsp=[f for f in m_di["data"]["files"] if pr.search(f["url"])]
        if package=="expanded" and len(flsp)==0:
            pr=re.compile("basic")
            flsp=[f for f in m_di["data"]["files"] if pr.search(f["url"])]
            
        # check for no files
        if len(flsp)==0:
            print(f"No files found for site {m_di['data']['siteCode']} and month {m_di['data']['month']}")
            continue
        
        # make separate lists of variables, readme and sensor positions
        varfi=[f for f in m_di["data"]["files"] if vr.search(f["name"])]
        rdmei=[f for f in m_di["data"]["files"] if rdr.search(f["name"])]
        spi=[f for f in m_di["data"]["files"] if spr.search(f["name"])]
        
        varf.append(varfi)
        rdme.append(rdmei)
        if len(spi)>0:
            sp.append(spi)
            
        # subset by averaging interval, and include SRF files
        if timeindex!="all":
            flnmi=[fl["name"] for fl in flsp if tt.search(fl["name"])]
            flszi=[fl["size"] for fl in flsp if tt.search(fl["name"])]
            zi=[fl["url"] for fl in flsp if tt.search(fl["name"])]
            
            # check for no files
            if len(flnmi)==0:
                print(f"No files found for site {m_di['data']['siteCode']}, month {m_di['data']['month']}, and averaging interval (time index) {timeindex}")
                continue
        
        # subset by table
        if tabl!="all":
            flnmi=[fl["name"] for fl in flsp if tb.search(fl["name"])]
            flszi=[fl["size"] for fl in flsp if tb.search(fl["name"])]
            zi=[fl["url"] for fl in flsp if tb.search(fl["name"])]
            
            # check for no files
            if len(flnmi)==0:
                print(f"No files found for site {m_di['data']['siteCode']}, month {m_di['data']['month']}, and table {tabl}")
                continue
                            
        # return url, file name, file size, and release
        flnm.append(flnmi)
        z.append(zi)
        sz.append(flszi)
        rel.append(m_di["data"]["release"])
    
    # get most recent metadata files from lists
    try:
        varf=sum(varf, [])
        varfl=get_recent(varf, "variables")
        flnm.append([fl["name"] for fl in varfl])
        z.append([fl["url"] for fl in varfl])
        sz.append([fl["size"]for fl in varfl])
        #rel.append() # do we need a value here?
    except:
        pass
    
    try:
        rdme=sum(rdme, [])
        rdfl=get_recent(rdme, "readme")
        flnm.append([fl["name"] for fl in rdfl])
        z.append([fl["url"] for fl in rdfl])
        sz.append([fl["size"] for fl in rdfl])
        #rel.append()
    except:
        pass
    
    # get most recent sensor positions file for each site
    if len(sp)>0:
        sp=sum(sp, [])
        sr=re.compile("\/[A-Z]{4}\/")
        sites=[sr.search(f["url"]).group(0) for f in sp]
        sites=list(set(sites))
        sites=[re.sub(pattern="\/", repl="", string=s) for s in sites]
        try:
            for s in sites:
                spfl=get_recent(sp, s)
                flnm.append([fl["name"] for fl in spfl])
                z.append([fl["url"] for fl in spfl])
                sz.append([fl["size"] for fl in spfl])
                #rel.append()
        except:
            pass

    
    z=sum(z, [])
    flnm=sum(flnm, [])
    sz=sum(sz, [])
    tbfiles=dict(flnm=flnm, z=z, sz=sz, rel=rel)
        
    # provisional message
    if(provflag):
        print("Provisional data were excluded from available files list. To download provisional data, use input parameter include_provisional=True.")
        
    return(tbfiles)


def download_urls(url_set, 
                  outpath,
                  token=None,
                  progress=True):
    """

    Given a set of urls to NEON data packages or files, downloads the contents of each. Internal function, called by zips_by_product().

    Parameters
    --------
    url_set: A list of urls pointing to zipped data packages
    outpath: Filepath of the folder to download to
    token: User specific API token (generated within neon.datascience user accounts). Optional.
    progress: Should the progress bar be displayed?

    Return
    --------
    Files in the designated folder

    Created on Feb 28 2024

    @author: Claire Lunch
    """
    
    if progress:
        print("Downloading files")
        
    for i in tqdm(range(0,len(url_set["z"])), disable=not progress):

        try:
            if token is None:
                with open(outpath+url_set["flnm"][i], "wb") as out_file:
                    content = requests.get(url_set["z"][i], stream=True, 
                                           headers={"accept": "application/json",
                                           "User-Agent": usera}).content
                    out_file.write(content)
            else:
                with open(outpath+url_set["flnm"][i], "wb") as out_file:
                    content = requests.get(url_set["z"][i], stream=True, 
                                           headers={"X-API-TOKEN": token, 
                                                    "accept": "application/json",
                                                    "User-Agent": usera}).content
                    out_file.write(content)

        except:
            print(f"File {url_set['flnm'][i]} could not be downloaded. Try increasing the timeout limit.")
            return None
        
    return None