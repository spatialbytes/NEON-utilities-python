#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def get_recent(fl_set, fltype):
    """

    Given a set of file names and urls for NEON data files, returns the url for the most recently published item of type=fltype, based on publication datetime stamp in the file name.

    Parameters
    --------
    fl_set: A set of file names and urls for NEON data files, in the format returned via the data endpoint of the NEON API.
    fltype: The type of file to be returned (e.g. variables, sensor positions).

    Return
    --------
    The most recently published object (contains file name, url, size).

    Created on Apr 18 2024

    @author: Claire Lunch
    """

    # subset to files of specified type
    ty=re.compile(fltype)
    flt=[f for f in fl_set if ty.search(f["name"])]
    
    if len(flt)==0:
        return None
    
    # get max date stamp in subset
    pdater=re.compile("[0-9]{8}T[0-9]{6}Z")
    flvar=[pdater.search(f["name"]).group(0) for f in flt]
    
    if len(flvar)==0:
        return None
    
    recdate=max(flvar)
    
    # get url matching max date stamp
    maxr=re.compile(recdate)
    flmax=[f for f in flt if maxr.search(f["name"])]
    
    return [flmax[0]]