#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 13:10:18 2023

@author: bhass
"""

import re
from get_api import get_api


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
    request = get_api(
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
    if token and 'x-ratelimit-limit' in request.headers:
        if request.headers['x-ratelimit-limit'] == '200':
            print('API token was not recognized. Public rate limit applied.\n')

#   if(!is.na(token) & !is.null(req$headers$`x-ratelimit-limit`)) {
#     if(req$headers$`x-ratelimit-limit`==200) {
#       cat('API token was not recognized. Public rate limit applied.\n')
#     }
#   }

    request_dict = request.json()
    # error message if data are not from AOP
    if request_dict['data']['productScienceTeamAbbr'] != 'AOP':
        print(
            f'{dpid} is not a remote sensing product. Use zipsByProduct()')
        return
#   if(avail$data$productScienceTeamAbbr!="AOP") {
#     stop(paste(dpID, "is not a remote sensing product. Use zipsByProduct()"))
#   }

#   # check for sites that are flown under the flight box of a different site
#   if(site %in% shared_flights$site) {
#     flightSite <- shared_flights$flightSite[which(shared_flights$site==site)]
#     if(site %in% c('TREE','CHEQ','KONA','DCFS')) {
#       cat(paste(site, ' is part of the flight box for ', flightSite,
#                 '. Downloading data from ', flightSite, '.\n', sep=''))
#     } else {
#       cat(paste(site, ' is an aquatic site and is sometimes included in the flight box for ', flightSite,
#                 '. Aquatic sites are not always included in flight coverage every year.\nDownloading data from ',
#                 flightSite, '. Check data to confirm coverage of ', site, '.\n', sep=''))
#     }
#     site <- flightSite
#   }

#   # get the urls for months with data available, and subset to site
#   month.urls <- unlist(avail$data$siteCodes$availableDataUrls)
#   month.urls <- month.urls[grep(paste(site, year, sep="/"), month.urls)]

#   # error message if nothing is available
#   if(length(month.urls)==0) {
#     stop("There are no data at the selected site and year.")
#   }

#   file.urls.current <- getFileUrls(month.urls, token = token)
#   if(is.null(file.urls.current)) {
#     message("No data files found.")
#     return(invisible())
#   }
#   downld.size <- sum(as.numeric(as.character(file.urls.current[[1]]$size)), na.rm=T)
#   downld.size.read <- convByteSize(downld.size)

#   # ask user if they want to proceed
#   # can disable this with check.size=F
#   if(check.size==TRUE) {
#     resp <- readline(paste("Continuing will download ", nrow(file.urls.current[[1]]), " files totaling approximately ",
#                            downld.size.read, ". Do you want to proceed y/n: ", sep=""))
#     if(!(resp %in% c("y","Y"))) {
#       stop("Download halted.")
#     }
#   } else {
#     cat(paste("Downloading files totaling approximately", downld.size.read, "\n", sep=" "))
#     }


# request with suspended data (no data available)
# eg. https://data.neonscience.org/api/v0/products/DP3.30016.001
# suspended biomass data product
# productStatus: FUTURE
# releases: []
# siteCodes: NoneType object

    return request
