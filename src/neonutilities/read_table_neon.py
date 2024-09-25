#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from pyarrow import dataset
import logging
from .unzip_and_stack import get_variables
logging.basicConfig(level=logging.INFO, format='%(message)s')


def read_table_neon(data_file,
                    var_file
                    ):
    """

    Read a NEON data table with correct data types for each variable.

    Parameters
    --------
    data_file: Filepath to a data table to load.
    var_file: Filepath to the variables file.

    Return
    --------
    A data frame of a NEON data table, with column classes assigned by data type.

    Example
    --------
    >>> dattab = read_table_neon(data_file="path to data table file",
                                 var_file="path to variables file matching data table")

    Created on Thu Feb 1 2024

    @author: Zachary Nickerson
    """
    
    # Read in variables file and check type
    if isinstance(var_file, str):
        try:
            v = pd.read_csv(var_file)
        except Exception:
            logging.info("Table read failed because var_file must be either a NEON variables table or a file path to a NEON variables table.")
            return

    # Check this is a valid variables file
    if any(x in ['category', 'system', 'stat'] for x in list(v.columns)):
        print('var_file appears to match DP4.00200.001. Data wrangling for surface-atmosphere exchange data is currently only available in the R package version of neonUtilities.')
        return
    else:
        if not any(x in ['table', 'fieldName', 'dataType'] for x in list(v.columns)):
            logging.info('var_file is not a variables file, or is missing critical values.')
            return

    # get field names from the data table without loading table
    tabcols = pd.read_csv(data_file, index_col=0, nrows=0).columns.tolist()

    # subset variables file to the relevant fields
    vtab = v[v["fieldName"].isin(tabcols)]
    vtabu = vtab.drop_duplicates(subset="fieldName", ignore_index=True)

    # generate schema
    tableschema = get_variables(vtabu)

    # Check that most fields have a corrsponding value in variables
    m = len(tabcols) - len(tableschema)
    if m == len(tabcols):
        logging.info("Cannot correct data types because the variables file does not match the data file.")
        return
    if m > 4:
        logging.info(f"{m} fieldNames are present in data file but not in variables file. Data load may be affected; if possible, unknown fields are read as character strings.")

    # read data and append file names
    dat = dataset.dataset(source=data_file, format="csv", schema=tableschema)
    dattab = dat.to_table()
    pdat = dattab.to_pandas()    

    return pdat


def date_convert(dates):
    """

    Convert a string to a date type, or, if possible date formats fail, keep as a string.

    Parameters
    --------
    dates: A date or datetime in string format

    Return
    --------
    The date in date format, or, if conversion fails, the original string.

    Example
    --------
    >>> d = date_convert("2023-08-01")

    Created on 2 May 2024

    @author: Claire Lunch
    """    

    try:
        dout = pd.to_datetime(dates, format="%Y-%m-%dT%H:%M:%S", utc=True)
    except Exception:
        try:
            dout = pd.to_datetime(dates, format="%Y-%m-%dT%H:%M", utc=True)
        except Exception:
            try:
                dout = pd.to_datetime(dates, format="%Y-%m-%dT%H", utc=True)
            except Exception:
                try:
                    dout = pd.to_datetime(dates, format="%Y-%m-%d", utc=True)
                except Exception:
                    dout = dates
    return dout
