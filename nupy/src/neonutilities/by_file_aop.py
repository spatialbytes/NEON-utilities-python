#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 13:10:18 2023

@author: bhass

Created on Wed Sep 13 2023
@author: Bridget Hass (bhass@battelleecology.org)

Adapted from R neonUtilities byFileAOP 
https://github.com/NEONScience/NEON-utilities/blob/main/neonUtilities/R/byFileAOP.R
written by:
@author: Claire Lunch (clunch@battelleecology.org)
@author: Christine Laney (claney@battelleecology.org)

"""

from importlib_resources import files
from pathlib import Path
#from get_api import get_api
from neonutilities import get_api
import pandas as pd
import re
# from tdqm import tdqm
from progress.bar import Bar
from time import sleep


# check that token was used
def check_token(response):
    """
    Query the API for AOP data by site, year, and product, and download all 
    files found, preserving original folder structure. Downloads serially to 
    avoid API rate-limit overload; may take a long time.

    Parameters
    --------
    response: 

    Return
    --------
    Warning statement explaining that the API token was not recognized.

    """

    if 'x-ratelimit-limit' in response.headers and response.headers['x-ratelimit-limit'] == '200':
        print('API token was not recognized. Public rate limit applied.\n')


def convert_byte_size(size_bytes):
    """
    Convert the file size in bytes to a more readable format for display. 

    Parameters
    --------
    size_bytes: the full file size in bytes

    Return
    --------
    String of converted file size in KB, MB, GB, or TB.
    """

    if 10**3 < size_bytes < 10**6:
        size_kb = round(size_bytes/(10**3), 2)
        size_read = f'{size_kb} KB'
    elif 10**6 < size_bytes < 10**9:
        size_mb = round(size_bytes/(10**6), 1)
        size_read = f'{size_mb} MB'
        # print('Download size:', size_read)
    elif 10**9 < size_bytes < 10**12:
        size_gb = round(size_bytes/(10**9), 1)
        size_read = f'{size_gb} GB'
        # print('Download size:', size_read)
    else:
        size_tb = round(size_bytes/(10**12), 1)
        size_read = f'{size_tb} TB'
        # print('Download size:', size_read)
    return size_read

# %%


def download_file(url, save_path, token=None):
    """
    Function to download a single file from a file's google cloud storage url.

    Parameters
    --------
    url: google cloud storage url where the file is stored
    save_path: the file location (path) where a file will be downloaded
    token: User specific API token (generated within neon.datascience user accounts). Optional.

    Return
    --------
    Downloads the file to the user-specified directory "save_path".

    """
    # print('url:', url)
    file_name = url.split('/')[-1]
    # print(f'downloading {file_name}')
    if 'neon-publication' in url:
        file_path = url.split('/')[-1]
        # print(url)
        # print(file_path)
    else:  # elif 'neon-aop-products' in url:
        file_path = url.split('neon-aop-products/')[1]
    file_fullpath = save_path / file_path
    file_fullpath.parent.mkdir(parents=True, exist_ok=True)
    # print(f'downloading file to {file_fullpath}')
    req = get_api(url, token)
    with open(file_fullpath, 'wb') as f:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    return

# %%


def get_file_urls(urls, token=None):
    """
    Get all the files from a list of urls

    Parameters
    --------
    urls: 
    token: User specific API token (generated within neon.datascience user accounts). Optional.

    Return
    --------
    file_url_df:
    release:

    """

    for url in urls:
        req = get_api(api_url=url, token=token)
        if not req:
            print(
                f"Data file retrieval failed. Check NEON data portal for outage alerts.")

        # get release info
        release = req.json()['data']['release']

        file_url_dict = req.json()['data']['files']
        file_url_df = pd.DataFrame(data=file_url_dict)
        # drop md5 and crc32 columns, which are all NaNs
        file_url_df.drop(columns=['md5', 'crc32'], inplace=True)

    return file_url_df, release

# %%


def by_file_aop(dpid,
                site,
                year,
                check_size=True,
                save_path=None,
                token=None):
    """
    Query the API for AOP data by site, year, and product, and download all 
    files found, preserving original folder structure. Downloads serially to 
    avoid API rate-limit overload; may take a long time.

    Parameters
    --------
    dpid: The identifier of the NEON data product to pull, in the form DPL.PRNUM.REV, e.g. DP3.30001.001
    site: The four-letter code of a single NEON site, e.g. 'CLBJ'.
    year: The four-digit year to search for data.
    check_size: True or False, should the user approve the total file size before downloading? Defaults to True. When working in batch mode, or other non-interactive workflow, use check.size=False.
    save_path: The file path to download to. Defaults to None, in which case the working directory is used.
    token: User specific API token (generated within neon.datascience user accounts). Optional.

    Return
    --------
    A folder in the working directory, containing all AOP files meeting query criteria.

    Example
    --------
    Download 2021 CHM data from MCRA:
    by_file_aop(dpid="DP3.30015.001", site="MCRA", year="2021",save_path="../../test_download")
    """

    # error message if dpid isn't formatted as expected
    dpid_pattern = "DP[1-4]{1}.[0-9]{5}.00[1-2]{1}"
    if not re.fullmatch(dpid_pattern, dpid):
        print(
            f'{dpid} is not a properly formatted data product ID. The correct format is DP#.#####.00#')
        return

    # error message if field spectra data are attempted
    if dpid == 'DP1.30012.001':
        print(
            'DP1.30012.001 is the Field spectral data product, which is published as tabular data. Use zipsByProduct() or loadByProduct() to download these data.')
        return

    # error message if site is not a 4-letter character
    site = site.upper()  # make site upper case (if it's not already)
    site_pattern = "[A-Z]{4}"
    if not re.fullmatch(site_pattern, site):
        print(
            'A four-letter NEON site code is required. NEON sites codes can be found here: https://www.neonscience.org/field-sites/field-sites-map/list')
        return

    # error message if year input is not valid
    year = str(year)  # cast year to string (if it's not already)
    year_pattern = "20[1-9][1-9]"
    if not re.fullmatch(year_pattern, year):
        print(
            f'{year} is an invalid year. Year is required in the format "2017", eg. Data are available from 2013 to present.')
        return

    # if token is an empty string, set to None
    if token == '':
        token = None

    # query the products endpoint for the product requested
    response = get_api(
        "http://data.neonscience.org/api/v0/products/" + dpid, token)

  # # query the products endpoint for the product requested
  # req <- getAPI(paste("http://data.neonscience.org/api/v0/products/", dpID, sep=""), token)
  # avail <- jsonlite::fromJSON(httr::content(req, as="text", encoding="UTF-8"),
  #                             simplifyDataFrame=TRUE, flatten=TRUE)

# with the way get_api is currently written it returns None for a bad request
# eg. https://data.neonscience.org/api/v0/products/DP3.30050.001
# doesn't seem like this part below is actually doing anything in the R script either?
# not sure what edge case it is handling
# # error message if product not found
#   if(!is.null(avail$error$status)) {
#     stop(paste("No data found for product", dpID, sep=" "))
#   }

#   # check that token was used
    if token and 'x-ratelimit-limit' in response.headers:
        check_token(response)
        # if response.headers['x-ratelimit-limit'] == '200':
        #     print('API token was not recognized. Public rate limit applied.\n')

    # get the request respose dictionary
    response_dict = response.json()
    # error message if dpid is not an AOP data product
    if response_dict['data']['productScienceTeamAbbr'] != 'AOP':
        print(
            f'{dpid} is not a remote sensing product. Use zipsByProduct()')
        return

    # check for sites that are flown under the flight box of a different site
    # this next section pulls from the shared_flights.csv file (could also use
    # a Python pickle, but csv is more transparent on Git)
    # still need to determine the best place to put it, link below recommends
    # "Files which are to be used by your installed library should usually be
    # placed inside of the Python module directory itself"
    # https://python-packaging.readthedocs.io/en/latest/non-code-files.html
    
    shared_flights_df = pd.read_csv(files('neonutilities').joinpath('shared_flights.csv'))
    # shared_flights_df = pd.read_csv('shared_flights.csv')
    # .to_dict(orient='tight',index=False)

    shared_flights_dict = shared_flights_df.set_index(
        ['site'])['flightSite'].to_dict()
    if site in shared_flights_dict:
        flightSite = shared_flights_dict[site]
        if site in ['TREE', 'CHEQ', 'KONA', 'DCFS']:
            print(
                f'{site} is part of the flight box for {flightSite}. Downloading data from {flightSite}.')
        else:
            print(f'{site} is an aquatic site and is sometimes included in the flight box for {flightSite}. Aquatic sites are not always included in the flight coverage every year. \nDownloading data from {flightSite}. Check data to confirm coverage of {site}.')
        site = flightSite

    # get the urls for months with data available, and subset to site
    site_info = next(
        item for item in response_dict['data']['siteCodes'] if item["siteCode"] == site)
    site_urls = site_info['availableDataUrls']

    # error message if nothing is available
    if len(site_urls) == 0:
        print("There are no data available at the selected site and year.")

    # get file url dataframe for the available month urls
    file_url_df, release = get_file_urls(site_urls, token=token)

    # get the number of files in the dataframe, if there are no files to download, return
    num_files = len(file_url_df)
    if num_files == 0:
        print("No data files found.")
        return

    # get the total size of all the files found
    download_size_bytes = file_url_df['size'].sum()
    download_size = convert_byte_size(download_size_bytes)

    # ask user if they want to proceed
    if check_size:
        if input(f"Continuing will download {num_files} totaling approximately {download_size}. Do you want to proceed? (y/n) ") != "y":
            print("Download halted")
            return

    # create folder in working directory to put files in
    if save_path:
        download_path = Path.cwd() / Path(save_path)
    else:
        download_path = Path.cwd()
    # print('download path', download_path)
    download_path.mkdir(parents=True, exist_ok=True)

    # serially download all files, with tdqm progress bar
    files = list(file_url_df['url'])
    print(
        f"Downloading {num_files} files totaling approximately {download_size}\n")
    sleep(1)
    # for file in tdqm(files): # if tdqm imports properly, this should work
    with Bar('Download Progress...', max=len(files)) as bar:
        for file in files:
            # try:
            download_file(file, download_path)
            bar.next()
        # except Exception as e:
        #     print(e)
        bar.finish()

    return

# request with suspended data (no data available)
# eg. https://data.neonscience.org/api/v0/products/DP3.30016.001
# suspended biomass data product
# productStatus: FUTURE
# releases: []
# siteCodes: NoneType object
