#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 2023
@author: Bridget Hass (bhass@battelleecology.org)

Functions to download AOP data either for an entire site (by_file_aop), or 
for a portion of a site (by_tile_aop), specified by the UTM coordinates 
(easting and northing) of the AOP data tiles that you want to download.

Adapted from R neonUtilities byFileAOP.R and byTileAOP.R, along with other helper functions.
https://github.com/NEONScience/NEON-utilities/blob/main/neonUtilities/R/byFileAOP.R
https://github.com/NEONScience/NEON-utilities/blob/main/neonUtilities/R/byTileAOP.R
written by:
@author: Claire Lunch (clunch@battelleecology.org)
@author: Christine Laney (claney@battelleecology.org)

"""
# TODO: Add provisional/release handling in by_file_aop and by_tile_aop
# TODO: Set user agent
# TODO: Add functionality to get new list of URLs if the old ones expire during the download stream
# TODO: Get DOIs and generate citations (using get_citation function)

import importlib
import importlib_resources
from . import __resources__
from pathlib import Path
# from aop_helpers import get_api
from neonutilities import get_api
import numpy as np
import pandas as pd
import re
# from tdqm import tdqm
from progress.bar import Bar
from time import sleep


# check that token was used
def check_token(response):
    """
    This function checks the API response headers for a rate limit. If the rate limit is found to be '200',
    it prints a warning message indicating that the API token was not recognized and the public rate limit was applied.

    Parameters
    --------
    response: API get response object containing status code and json data. Return of get_api function.

    Returns
    --------
    None

    Raises
    --------
    None

    """

    if 'x-ratelimit-limit' in response.headers and response.headers['x-ratelimit-limit'] == '200':
        print('API token was not recognized. Public rate limit applied.\n')


def convert_byte_size(size_bytes):
    """
    This function converts the file size in bytes to a more readable format.
    It converts bytes to Kilobytes (KB), Megabytes (MB), Gigabytes (GB), or Terabytes (TB)
    depending on the size of the input.

    Parameters
    --------
    size_bytes: int or float
        The file size in bytes. It should be a non-negative number.

    Returns
    --------
    str
        A string that represents the file size in a more readable format.
        The format includes the size number followed by the size unit (KB, MB, GB, or TB).

    Raises
    --------
    None

    Examples
    --------
    >>> convert_byte_size(5000)
    '5.0 KB'

    >>> convert_byte_size(2000000)
    '2.0 MB'

    >>> convert_byte_size(3000000000)
    '3.0 GB'

    >>> convert_byte_size(4000000000000)
    '4.0 TB'
"""


def download_file(url, save_path, token=None):
    """
    This function downloads a single file from a Google Cloud Storage URL to a user-specified directory.

    Parameters
    --------
    url: str
        The Google Cloud Storage URL where the file is stored.

    save_path: str or pathlib.Path
        The file location (path) where the file will be downloaded. It can be a string or a pathlib.Path object.

    token: str, optional
        User-specific API token generated within neon.datascience user accounts. If provided, it will be used for authentication.

    Returns
    --------
    None

    Raises
    --------
    None

    Examples
    --------
    >>> download_file('https://storage.googleapis.com/neon-aop-products/2023/FullSite/D02/2023_SCBI_6/L3/DiscreteLidar/CanopyHeightModelGtif/NEON_D02_SCBI_DP3_741000_4301000_CHM.tif', '/path/to/save', 'my-api-token')
    # This will download 'NEON_D02_SCBI_DP3_741000_4301000_CHM.tif' from the specified URL to '/path/to/save' directory using 'my-api-token' for authentication.

    Notes
    --------
    The function creates the directory specified by 'save_path' if it does not exist. 
    It also handles 'neon-publication' and 'neon-aop-products' in the URL differently to determine the file path. 
    This is for downloading the readme.txt file which contains detailed information about the data package, issue logs, etc.
    https://storage.googleapis.com/neon-publication/NEON.DOM.SITE.DP3.30015.001/SCBI/20230601T000000--20230701T000000/basic/NEON.D02.SCBI.DP3.30015.001.readme.20240206T001418Z.txt
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
    This function retrieves all the files from a list of NEON data URLs.

    Parameters
    --------
    urls: list of str
        A list of URLs from which the files will be retrieved.

    token: str, optional
        User-specific API token generated within neon.datascience user accounts. If provided, it will be used for authentication.

    Returns
    --------
    all_file_url_df: pandas.DataFrame
        A DataFrame containing information about all the files retrieved from the URLs. 
        The DataFrame includes columns for 'name', 'size', 'crc32c', and 'url' and 'release' of the files.

    release: str
        The release information retrieved from the response JSON.

    Raises
    --------
    None

    Examples
    --------
    >>> urls = [ 'https://data.neonscience.org/api/v0/data/DP3.30015.001/SCBI/2022-05',
                'https://data.neonscience.org/api/v0/data/DP3.30015.001/SCBI/2023-06']
    >>> get_file_urls(urls, 'my-api-token')
    # This will return a DataFrame with all the data files contained in SCBI 2022-05 and 2023-06 and the release information.

    Notes
    --------
    The function makes API calls to each URL in the 'urls' list and retrieves the file information. 
    It also retrieves the release information from the response JSON. 
    If the API call fails, it prints a warning message and continues with the next URL.
    """

    all_file_url_df = pd.DataFrame()
    releases = []
    for url in urls:
        response = get_api(api_url=url, token=token)
        if not response:
            print(
                f"Data file retrieval failed. Check NEON data portal for outage alerts.")

        # get release info
        release = response.json()['data']['release']
        releases.append(release)
        #print(url, ':', release)

        file_url_dict = response.json()['data']['files']
        file_url_df = pd.DataFrame(data=file_url_dict)
        file_url_df['release'] = release

        # drop md5 and crc32 columns, which are all NaNs
        file_url_df.drop(columns=['md5', 'crc32'], inplace=True)

        # append the new dataframe to the existing one
        all_file_url_df = pd.concat(
            [all_file_url_df, file_url_df], ignore_index=True)

    return all_file_url_df, list(set(releases))

# %%


def get_shared_flights(site):
    """
    This function retrieves shared flights information for a NEON site from 
    the shared_flights.csv lookup file, which contains the mapping between 
    collocated AOP sites (terrestrial:terrestrial and aquatic:terrestrial). 
    If the site is found in the shared flights data, it prints a message and 
    updates the site to the corresponding "flightSite".

    Parameters
    --------
    site: str
        The 4-letter NEON site code for which the collocated site information is to be retrieved.

    Returns
    --------
    site: str
        The collocated site that AOP data is published uner. If the original 
        site is found in the shared flights lookup, it is updated to the 
        corresponding flight site. Otherwise, it remains the same.

    Raises
    --------
    None

    Examples
    --------
    >>> get_shared_flights('TREE')
    'TREE is part of the flight box for STEI. Downloading data from STEI.'

    Notes
    --------
    The function reads the shared flights data from a CSV file named 
    'shared_flights.csv' located in the '__resources__' directory. 

    """
    shared_flights_file = (importlib_resources.files(
        __resources__) / 'shared_flights.csv')

    shared_flights_df = pd.read_csv(shared_flights_file)

    shared_flights_dict = shared_flights_df.set_index(
        ['site'])['flightSite'].to_dict()
    if site in shared_flights_dict:
        flightSite = shared_flights_dict[site]
        if site in ['TREE', 'CHEQ', 'KONA', 'DCFS']:
            print(
                f'{site} is part of the flight box for {flightSite}. Downloading data from {flightSite}.')
        else:
            print(f'{site} is an aquatic site and is sometimes included in the flight box for {flightSite}. Aquatic sites are not always included in the flight coverage every year.\nDownloading data from {flightSite}. Check data to confirm coverage of {site}.')
        site = flightSite
    return site

# %%


def by_file_aop(dpid,
                site,
                year,
                include_provisional=False,
                check_size=True,
                save_path=None,
                token=None):
    """
    This function queries the API for AOP data by site, year, and product, and downloads all
    files found, preserving the original folder structure. It downloads files serially to
    avoid API rate-limit overload, which may take a long time.

    Parameters
    --------
    dpid: str
        The identifier of the NEON data product to pull, in the form DPL.PRNUM.REV, e.g. DP3.30001.001.

    site: str
        The four-letter code of a single NEON site, e.g. 'CLBJ'.

    year: str or int
        The four-digit year to search for data.

    include_provisional: bool, optional
        Should provisional data be downloaded? Defaults to False. See
        https://www.neonscience.org/data-samples/data-management/data-revisions-releases 
        for details on the difference between provisional and released data.

    check_size: bool, optional
        Should the user approve the total file size before downloading? Defaults to True. 
        If you have sufficient storage space on your local drive, when working 
        in batch mode, or other non-interactive workflow, use check_size=False.

    save_path: str or pathlib.Path, optional
        The file path to download to. Defaults to None, in which case the working directory is used. 
        It can be a string or a pathlib.Path object.

    token: str, optional
        User-specific API token generated within neon.datascience user accounts.

    Returns
    --------
    None

    Raises
    --------
    None

    Examples
    --------
    >>> by_file_aop(dpid="DP3.30015.001", site="MCRA", year="2021", save_path="./test_download")
    # This will download 2021 CHM data from MCRA to the './test_download' directory.

    Notes
    --------
    The function creates a folder in the 'save_path' directory, containing all AOP files meeting the query criteria. 
    If 'save_path' is not provided, it uses the working directory.
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
            f'{site} is an invalid site. A four-letter NEON site code is required. NEON sites codes can be found here: https://www.neonscience.org/field-sites/field-sites-map/list.')
        return

    # error message if year input is not valid
    year = str(year)  # cast year to string (if it's not already)
    year_pattern = "20[1-9][0-9]"
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

    # replace collocated site with the site name it's published under
    site = get_shared_flights(site)

    # get the urls for months with data available, and subset to site
    site_info = next(
        item for item in response_dict['data']['siteCodes'] if item["siteCode"] == site)
    site_urls = site_info['availableDataUrls']

    site_year_urls = [url for url in site_urls if str(year) in url]

    # error message if nothing is available
    if len(site_year_urls) == 0:
        print("There are no data available at the selected site and year.")
        return

    # get file url dataframe for the available month urls
    file_url_df, release = get_file_urls(site_year_urls, token=token)

    # get the number of files in the dataframe, if there are no files to download, return
    if len(file_url_df) == 0:
        print("No data files found.")
        return

    # if 'PROVISIONAL' in releases and not include_provisional:
    if include_provisional:
        # print provisional message
        print("Provisional data are included. To exclude provisional data, use input parameter include_provisional=False.")
    else:
        file_url_df = file_url_df[file_url_df['release'] != 'PROVISIONAL']
        # print("Provisional data are not included. To download provisional data, use input parameter include_provisional=True.")

    num_files = len(file_url_df)
    if num_files == 0:
        print("No data files found. Available data may all be provisional. To download provisional data, use input parameter include_provisional=True.")
        return

    # get the total size of all the files found
    download_size_bytes = file_url_df['size'].sum()
    download_size = convert_byte_size(download_size_bytes)

    # report data download size and ask user if they want to proceed
    if check_size:
        if input(f"Continuing will download {num_files} totaling approximately {download_size}. Do you want to proceed? (y/n) ") != "y":
            print("Download halted.")
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

# %%


def by_tile_aop(dpid,
                site,
                year,
                easting,
                northing,
                buffer=0,
                include_provisional=False,
                check_size=True,
                save_path=None,
                token=None,
                verbose=False):
    """
    This function queries the API for AOP data by site, year, product, and 
    UTM coordinates, and downloads all files found, preserving the original 
    folder structure. It downloads files serially to avoid API rate-limit 
    overload, which may take a long time.

    Parameters
    --------
    dpid: str
        The identifier of the NEON data product to pull, in the form DPL.PRNUM.REV, e.g. DP3.30001.001.

    site: str
        The four-letter code of a single NEON site, e.g. 'CLBJ'.

    year: str or int
        The four-digit year to search for data.

    easting: int or list of int
        A number or list containing the easting UTM coordinate(s) of the locations to download.

    northing: int or list of int
        A number or list containing the northing UTM coordinate(s) of the locations to download.

    buffer: int, optional
        Size, in meters, of the buffer to be included around the coordinates when determining which tiles to download. Defaults to 0. 
        If easting and northing coordinates are the centroids of NEON TOS plots, use buffer = 20.

    include_provisional: bool, optional
        Should provisional data be downloaded? Defaults to False. See 
        https://www.neonscience.org/data-samples/data-management/data-revisions-releases 
        for details on the difference between provisional and released data.

    check_size: bool, optional
        Should the user approve the total file size before downloading? Defaults to True. 
        If you have sufficient storage space on your local drive, when working 
        in batch mode, or other non-interactive workflow, use check_size=False.

    save_path: str or pathlib.Path, optional
        The file path to download to. Defaults to None, in which case the working directory is used. 
        It can be a string or a pathlib.Path object.

    token: str, optional
        User-specific API token generated within neon.datascience user accounts.

    verbose: bool, optional
        If set to True, the function will print

    Return
    --------
    A folder in the working directory, containing all AOP files meeting query criteria.

    Example
    --------
    Download 2021 CHM data from MCRA at a single point:
    by_tile_aop(dpid="DP3.30015.001", site="MCRA",easting = , northing = ,
                year="2021", save_path="../../test_download")


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
            f'{site} is an invalid site. A four-letter NEON site code is required. NEON sites codes can be found here: https://www.neonscience.org/field-sites/field-sites-map/list.')
        return

    # error message if year input is not valid
    year = str(year)  # cast year to string (if it's not already)
    year_pattern = "20[1-9][0-9]"
    if not re.fullmatch(year_pattern, year):
        print(
            f'{year} is an invalid year. Year is required in the format "2017", eg. Data are available from 2013 to present.')
        return

    # convert easting and northing to lists, if they are not already
    if type(easting) is not list:
        easting = [easting]
    if type(northing) is not list:
        northing = [northing]

    # convert to floats, and display error message if easting and northing lists are not numeric
    try:
        easting = [float(e) for e in easting]
    except ValueError as e:
        print(
            f'The easting is invalid, this is required as a number or numeric list format, eg. 732000 or [732000, 733000]')
        print(e)

    try:
        northing = [float(e) for e in northing]
    except ValueError as e:
        print(
            f'The northing is invalid, this is required as a number or numeric list format, eg. 4713000 or [4713000, 4714000]')
        print(e)

    # link easting and northing coordinates - as a list of tuples ?
    # coord_tuples = [(easting[i], northing[i]) for i in range(0, len(easting))]

    # error message if easting and northing vector lengths don't match (also handles empty/NA cases)
    # note there should not be any strings now that we've converted everything to float
    easting = [e for e in easting if not np.isnan(e)]
    northing = [n for n in northing if not np.isnan(n)]

    if len(easting) != len(northing):
        print(
            f'Easting and northing list lengths do not match, and/or contain null values. Cannot identify paired coordinates.')
        return

    # if token is an empty string, set to None
    if token == '':
        token = None

    # query the products endpoint for the product requested
    response = get_api(
        "http://data.neonscience.org/api/v0/products/" + dpid, token)

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

    # replace collocated site with the site name it's published under
    site = get_shared_flights(site)

    # get the urls for months with data available, and subset to site
    site_info = next(
        item for item in response_dict['data']['siteCodes'] if item["siteCode"] == site)
    site_urls = site_info['availableDataUrls']

    # error message if nothing is available
    if len(site_urls) == 0:
        print("There are no data available at the selected site and year.")

    site_year_urls = [url for url in site_urls if str(year) in url]

    # get file url dataframe for the available month url(s)
    file_url_df, releases = get_file_urls(site_year_urls, token=token)

    # get the number of files in the dataframe, if there are no files to download, return
    if len(file_url_df) == 0:
        print("No data files found.")
        return

    # if 'PROVISIONAL' in releases and not include_provisional:
    if include_provisional:
        # print provisional message
        print("Provisional data are included. To exclude provisional data, use input parameter include_provisional=False.")
    else:
        file_url_df = file_url_df[file_url_df['release'] != 'PROVISIONAL']
        # print("Provisional data are not included. To download provisional data, use input parameter include_provisional=True.")

    num_files = len(file_url_df)
    if num_files == 0:
        print("No data files found. Available data may all be provisional. To download provisional data, use input parameter include_provisional=True.")
        return

    # BLAN edge-case - contains plots in 18N and plots in 17N; flight data are all in 17N
    # convert easting & northing coordinates for Blandy (BLAN) to 17N
    if site == 'BLAN' and any([e > 725000.0 for e in easting]):
        # check that pyproj is installed
        try:
            importlib.import_module('pyproj')
            print("pyproj is installed.")
        except ImportError:
            print(
                "Package pyproj is required for this function to work at the BLAN site. Install and re-try")
            return

        from pyproj import Proj, CRS

        crs17 = CRS.from_epsg(32617)  # utm zone 17N
        crs18 = CRS.from_epsg(32618)  # utm zone 18N

        proj18to17 = Proj.from_crs(crs_from=crs18, crs_to=crs17)

        # add warning if provided an easting > 250000 ?

        # link easting and northing coordinates so it's easier to parse the zone for each
        coord_tuples = [(easting[i], northing[i])
                        for i in range(0, len(easting))]

        coords17 = [(e, n) for (e, n) in coord_tuples if e > 250000.0]
        coords18 = [(e, n) for (e, n) in coord_tuples if e <= 250000.0]

        # apply the projection transformation from 18N to 17N for each coordinate tuple

        coords18_reprojected = [proj18to17.transform(
            coords18[i][0], coords18[i][1]) for i in range(len(coords18))]

        coords17.extend(coords18_reprojected)

        easting = [c[0] for c in coords17]
        northing = [c[1] for c in coords17]

        print('Blandy (BLAN) plots include two UTM zones, flight data are '
              'all in 17N. Coordinates in UTM zone 18N have been converted '
              'to 17N to download the correct tiles. You will need to make '
              'the same conversion to connect airborne to ground data.')

    # function to round down to the nearest 1000, in order to determine lower left coordinate of AOP tile to be downloaded
    def round_down1000(val):
        return int(np.floor(val/1000)*1000)

    # function to get the coordinates of the tiles including the buffer
    def get_buffer_coords(easting, northing, buffer):
        # apply the buffer to the easting and northings
        buffer_min_e = easting - buffer
        buffer_min_n = northing - buffer
        buffer_max_e = easting + buffer
        buffer_max_n = northing + buffer

        new_coords = [(buffer_min_e, buffer_min_n), (buffer_min_e, buffer_max_n),
                      (buffer_max_e, buffer_min_n), (buffer_max_e, buffer_max_n)]

        return new_coords

    # get the tiles corresponding to the new coordinates (mins and maxes)
    # if verbose:
    #     print('getting coordinates of tiles, including the buffer')
    buffer_coords = []
    for e, n in zip(easting, northing):
        buffer_coords.extend(get_buffer_coords(e, n, buffer))

    buffer_coords_rounded = [
        (round_down1000(c[0]), round_down1000(c[1])) for c in buffer_coords]
    # remove duplicate coordinates
    buffer_coords_set = list(set(buffer_coords_rounded))
    buffer_coords_set.sort()

    if verbose:
        print('Easting:', easting)
        print('Northing:', northing)
        print('Buffer:', buffer)
        print('UTM (x, y) lower-left coordinates of tiles to be downloaded:')
        for coord in buffer_coords_set:
            print(coord)

    # create the list of utm "easting_northing" strings that will be used to match to the tile names
    coord_strs = ['_'.join([str(c[0]), str(c[1])])
                  for c in buffer_coords_set]
    # print(coord_strs)

    # round down to get the lower left coordinate of the tile corresponding to the point
    # coord_tuples = [(easting[i], northing[i]) for i in range(0, len(easting))]
    # coord_tuples_floor = [(round_down1000(c[0]),round_down1000(c[1])) for c in coord_tuples]
    # easting_floor = [int(np.floor(e/1000)*1000) for e in easting]
    # northing_floor = [int(np.floor(n/1000)*1000) for n in northing]

    # subset by the tiles in the easting, northing lists
    # first get a list of the coordinate strings (easting_northing) to match
    # coord_strs = ['_'.join([str(e), str(n)])
    #               for e, n in zip(easting_floor, northing_floor)]

    # append the .txt file to include the README
    # coord_strs.append('.txt')
    coord_strs.append('.txt')

    # subset the dataframe to include only the coordinate strings matching coord_strs
    # if verbose:
    #     print('finding the tiles')
    file_url_df_subset = file_url_df[file_url_df['name'].str.contains(
        '|'.join(coord_strs))]

    file_url_df_subset2 = file_url_df_subset[~file_url_df_subset['name'].str.endswith(
        '.txt')]

    # if any coordinates were not included in the data, print a warning message
    # Warning: the following coordinates are outside the bounds of site-year:
    unique_coords_to_download = set(
        file_url_df_subset2['name'].str.extract(r'_(\d+_\d+)_')[0])

    coord_strs.remove('.txt')
    # compare two lists:
    coords_not_found = list(
        set(coord_strs).difference(list(unique_coords_to_download)))
    if len(coords_not_found) > 0:
        print('Warning, the following coordinates fall outside the bounds of the site, so will not be downloaded:')
        for coord in coords_not_found:
            print(','.join(coord.split('_')))

    # get the number of files in the dataframe, if there are no files to download, return
    num_files = len(file_url_df_subset)
    if num_files == 0:
        print("No data files found.")
        return

    # get the total size of all the files found
    download_size_bytes = file_url_df_subset['size'].sum()
    download_size = convert_byte_size(download_size_bytes)

    # ask whether to continue download, depending on size
    if check_size:
        if input(f"Continuing will download {num_files} files totaling approximately {download_size}. Do you want to proceed? (y/n) ") != "y":
            print("Download halted")
            return

    # create folder in working directory to put files in
    if save_path:
        download_path = Path(save_path) / dpid
    else:
        download_path = Path.cwd() / dpid
    # print('download path', download_path)
    download_path.mkdir(parents=True, exist_ok=True)

    # serially download all files, with progress bar
    files = list(file_url_df_subset['url'])
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
