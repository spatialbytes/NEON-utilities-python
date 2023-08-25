#!/usr/bin/env python3
# -*- coding: utf-8 -*-
def get_citation(dpID, release):
    """
    Use the DOI Foundation API to get BibTex-formatted citations for NEON data, 
    or use a template to generate a BibTex citation for provisional data. 
    Helper function to download and stacking functions.

    Parameters
    ----------
    dpID : The data product ID of the data to be cited
    release : The data release to be cited. Can be provisional.

    Return
    ------
    A character string containing the citation in BibTex format.

    Example
    -------
    Get the citation for Breeding landbird point counts (DP1.10003.001), 
    RELEASE-2023

    >>> cit = get_citation(dpID="DP1.10003.001", release="RELEASE-2023")

    Created on Fri Aug 25 10:26:23 2023

    @author: Claire Lunch
    """
    
    if release == "PROVISIONAL"
        citI = "@misc{DPID/provisional,\n  doi = {},\n  url = {https://data.neonscience.org/data-products/DPID},\n  author = {{National Ecological Observatory Network (NEON)}},\n  language = {en},\n  title = {NAME (DPID)},\n  publisher = {National Ecological Observatory Network (NEON)},\n  year = {YEAR}\n}"
        citDP = citI.replace("DPID", dpID)
        citY = citDP.replace("YEAR", str(datetime.now().year))
        
        nm_req = requests.get("https://data.neonscience.org/api/v0/products/"+
                              dpID)
        nm_str = nm_req.json()
        nm = nm_str["data"]["productName"]
        
        cit = citY.replace("NAME", nm)
        
    else:
        
        print("DOI retrieval code coming soon")