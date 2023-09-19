#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 13:10:18 2023

@author: bhass
"""

from pathlib import Path, PurePath
import re
from get_api import get_api
import pandas as pd

##############################################################################################
# ' @title Get and store the file names, S3 URLs, file size, and download status (default = 0) in a data frame

# ' @author
# ' Claire Lunch \email{clunch@battelleecology.org}
# ' Christine Laney \email{claney@battelleecology.org}

# ' @description Used to generate a data frame of available AOP files.
# '
# ' @param m.urls The monthly API URL for the AOP files
# ' @param token User specific API token (generated within neon.datascience user accounts)

# ' @return A dataframe comprised of file names, S3 URLs, file size, and download status (default = 0)

# ' @references
# ' License: GNU AFFERO GENERAL PUBLIC LICENSE Version 3, 19 November 2007

# Changelog and author contributions / copyrights
#   Claire Lunch (2018-02-19): original creation
#   Christine Laney (2018-03-05): Added functionality to get new list of URLs if the old ones expire, during the download stream.

##############################################################################################

# get and stash the file names, google cloud storage URLs, file size, and download status (default = 0) in a data frame

# def list_urls_by_product(self, dpid):
#     """
#     list_urls_by_product lists all the available api url for a given data product id (dpid)
#     """
#     product_url = self.construct_product_url(dpid)
#     # print(product_url)
#     r = self.make_request(product_url)
#     data_urls = []
#     for i in range(len(r['data']['siteCodes'])):
#         data_urls_temp = r['data']['siteCodes'][i]['availableDataUrls']
#         data_urls.extend(data_urls_temp)

#     return data_urls

# def make_new_dir(folder):
#     if not os.path.exists(folder):
#         os.makedirs(folder)

# %%


def check_token(request):
    #   # check that token was used
    if 'x-ratelimit-limit' in request.headers and request.headers['x-ratelimit-limit'] == '200':
        print('API token was not recognized. Public rate limit applied.\n')


def convert_byte_size(size_bytes):

    # if size_bytes < 10**3:
    #     size_printout = ('Download size:', round(size_bytes, 1), 'bytes')
    if 10**3 < size_bytes < 10**6:
        size_kb = round(size_bytes/(10**3), 2)
        size_read = f'{size_kb} KB'
    elif 10**6 < size_bytes < 10**9:
        size_mb = round(size_bytes/(10**6), 1)
        size_read = f'{size_mb} MB'
        # print('Download size:', round(size/(10**6), 2), 'MB')
    elif 10**9 < size_bytes < 10**12:
        size_gb = round(size_bytes/(10**9), 1)
        size_read = f'{size_gb} GB'
        # print('Download size:', round(size/(10**9), 2), 'GB')
    else:
        size_tb = round(size_bytes/(10**12), 1)
        size_read = f'{size_tb} TB'
        # print('Download size:', round(size/(10**12), 2), 'TB')
    return size_read

# %%


def download_file(url, token=None, save_path=None):
    # print('url:', url)
    file_name = url.split('/')[-1]
    # print('filename:', file_name)
    file_path = url.split('neon-aop-products/')[1]
    # print('filepath:', file_path)
    if save_path:
        print('save_path found')
        file_fullpath = save_path / file_path
    else:
        file_fullpath = Path.cwd() / file_path

    file_fullpath.parent.mkdir(parents=True, exist_ok=True)
    print(f'downloading file to {file_fullpath}')
    req = get_api(url, token)
    with open(file_fullpath, 'wb') as f:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    return

# %%


def get_file_urls(urls, token=None):
    # url_messages = []
    # releases = []

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
# getFileUrls < - function(m.urls, token=NA){
#     url.messages < - character()
#     file.urls < - c(NA, NA, NA)
#     releases < - character()
#     for(i in 1: length(m.urls)) {

#         tmp < - getAPI(apiURL=m.urls[i], token=token)

#         if(tmp$status_code != 200) {
#             message(paste("Data file retrieval failed with code ", tmp$status_code,
#                           ". Check NEON data portal for outage alerts.", sep=""))
#             return(invisible())
#         }

#         tmp.files < - jsonlite: : fromJSON(httr: : content(tmp, as='text', encoding='UTF-8'),
#                                           simplifyDataFrame=TRUE, flatten=TRUE)

#         # check for no files
#         if(length(tmp.files$data$files) == 0) {
#             url.messages < - c(url.messages, paste("No files found for site", tmp.files$data$siteCode,
#                                                    "and year", tmp.files$data$month, sep=" "))
#             next
#         }

#         # get release info
#         releases < - c(releases, tmp.files$data$release)

#         file.urls < - rbind(file.urls, cbind(tmp.files$data$files$name,
#                                              tmp.files$data$files$url,
#                                              tmp.files$data$files$size))

#     }

#     # get size info
#     file.urls < - data.frame(file.urls, row.names=NULL)
#     colnames(file.urls) < - c("name", "URL", "size")
#     file.urls$URL < - as.character(file.urls$URL)
#     file.urls$name < - as.character(file.urls$name)

#     if(length(url.messages) > 0){writeLines(url.messages)}
#     file.urls < - file.urls[-1, ]
#     release < - unique(releases)
#     return(list(file.urls, release))

# }


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
    Download 2017 vegetation index data from San Joaquin Experimental Range:

    >>> by_file_aop(dpID="DP3.30026.001", site="SJER", year="2017")

    Created on Wed Sep 13 2023
    @author: Bridget Hass (bhass@battelleecology.org)

    Adapted from R neonUtilities byFileAOP written by
    @author: Claire Lunch (clunch@battelleecology.org)
    @author: Christine Laney (claney@battelleecology.org)
    # https://github.com/NEONScience/NEON-utilities/blob/main/neonUtilities/R/byFileAOP.R

    """

    # error message if dpid isn't formatted as expected
    dpid_pattern = "DP[1-4]{1}.[0-9]{5}.00[1-2]{1}"
    if not re.fullmatch(dpid_pattern, dpid):
        print(
            f'{dpid} is not a properly formatted data product ID. The correct format is DP#.#####.00#')
        return
#     if(regexpr("DP[1-4]{1}.[0-9]{5}.00[1-2]{1}",dpID)!=1) {
#             stop(paste(dpID, "is not a properly formatted data product ID. The correct format is DP#.#####.00#", sep=" "))

# }
    # error message if field spectra data are attempted
    if dpid == 'DP1.30012.001':
        print(
            'DP1.30012.001 is the Field spectral data product, which is published as tabular data. Use zipsByProduct() or loadByProduct() to download these data.')
        return
#   if(dpID=='DP1.30012.001') {
#     stop('DP1.30012.001 is the Field spectral data product, which is published as tabular data. Use zipsByProduct() or loadByProduct() to download these data.')
#   }

    # error message if site is not a 4-letter character
    site = site.upper()  # make site upper case (if it's not already)
    site_pattern = "[A-Z]{4}"
    if not re.fullmatch(site_pattern, site):
        print(
            'A four-letter NEON site code is required. NEON sites codes can be found here: https://www.neonscience.org/field-sites/field-sites-map/list')
        return

  # if(regexpr('[[:alpha:]]{4}', site)!=1) {
  #   stop("A four-letter site code is required. NEON sites codes can be found here: https://www.neonscience.org/field-sites/field-sites-map/list")
  # }

    # error message if year input is not valid
    year = str(year)  # cast year to string (if it's not already)
    year_pattern = "20[1-9][1-9]"
    if not re.fullmatch(year_pattern, year):
        print(
            f'{year} is an invalid year. Year is required in the format "2017", eg. Data are available from 2013 to present.')
        return

    # if(regexpr('[[:digit:]]{4}', year)!=1) {
  #   stop("Year is required (e.g. '2017').")
  # }

    # if token is an empty string, set to None
    if token == '':
        token = None

  # if(identical(token, "")) {
  #   token <- NA_character_
  # }

  # releases <- character()

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
        if response.headers['x-ratelimit-limit'] == '200':
            print('API token was not recognized. Public rate limit applied.\n')

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

    shared_flights_df = pd.read_csv('./shared_flights.csv')
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
        print('Download size:', download_size)
        if input(f"Continuing will download {num_files} totaling approximately {download_size}. Do you want to proceed? (y/n)") != "y":
            print("Download halted")
            return
        else:
            print(f"Downloading files totaling approximately {download_size}")

    # create folder in working directory to put files in
    if save_path:
        download_path = Path(save_path)
    else:
        download_path = Path.cwd()
    download_path.mkdir(parents=True, exist_ok=True)

    # serially download all files
    files = list(file_url_df['url'])
    for file in files:
        try:
            download_file(file, download_path)
        except Exception as e:
            print(e)

    return

# request with suspended data (no data available)
# eg. https://data.neonscience.org/api/v0/products/DP3.30016.001
# suspended biomass data product
# productStatus: FUTURE
# releases: []
# siteCodes: NoneType object
