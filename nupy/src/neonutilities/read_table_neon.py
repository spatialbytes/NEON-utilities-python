#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

def read_table_neon(data_file,
                    var_file#,
                    #use_fast_time # Equivalent in Python?
                    ):
    """

    Read a NEON data table with correct data types for each variable.
    
    Parameters
    --------
    data_file: A data frame containing a NEON data table, or the filepath to a data table to load.
    var_file: A data frame containing the corresponding NEON variables file, or the filepath to the variables file.
    
    Return
    --------
    A data frame of a NEON data table, with column classes assigned by data type.
    
    Example
    --------
    ZN NOTE: Insert example when function is coded
    
    >>> example
    
    Created on Thu Feb 1 2024
    
    @author: Zachary Nickerson
    """    
    # Read in variables file and check type
    if isinstance(var_file,str):
        try:
            v = pd.read_csv(var_file)
        except:
            logging.info("Table read failed because var_file must be either a NEON variables table or a file path to a NEON variables table.")
            return
    # else:
    #     try:
    #         v = pd.DataFrame(var_file)
    #     except:
    #         logging.info("Table read failed because var_file must be either a NEON variables table or a file path to a NEON variables table.")
    #         return
        
    # Check this is a valid variables file
    if any(x in ['category','system','stat'] for x in list(v.columns)):
        print('var_file appears to match DP4.00200.001. Data wrangling for surface-atmosphere exchange data is currently only available in the R package version of neonUtilities.')
        return
    else:
        if not any(x in ['table','fieldName','dataType'] for x in list(v.columns)):
            logging.info('var_file is not a variables file, or is missing critical values.')
            return
    
    tableschema = get_variables(v)
    
    # # Make a new colClass column
    # # Use to specify data types
    # v['colClass'] = None
    # v['colClass'][v.dataType == "real"] = "float"
    # v['colClass'][v.dataType == "integer"] = "int"
    # v['colClass'][v.dataType == "unsigned integer"] = "int"
    # v['colClass'][v.dataType == "signed integer"] = "int"
    # v['colClass'][v.dataType == "string"] = "str"
    # v['colClass'][v.dataType == "uri"] = "str"
    # v['colClass'][v.dataType == "dateTime"] = "datetime"
    # v = v[['table','fieldName','colClass']]
    
    # Read in data file and check type
    if isinstance(data_file,str):
        try:
            d = pd.read_csv(data_file)
        except:
            logging.info("Table read failed because data_file must be either a NEON variables table or a file path to a NEON variables table.")
            return
    else:
        try:
            d = pd.DataFrame(data_file)
        except:
            logging.info("Table read failed because data_file must be either a NEON variables table or a file path to a NEON variables table.")
            return    
    
    # Check that most fields have a corrsponding value in variables
    m = len(set(list(d.columns)) - set(list(v.fieldName)))
    if m == len(d.columns):
        logging.info("Cannot correct data types because the variables file does not match the data file.")
        return
    if m > 4:
        logging.info(f"{m} fieldNames are present in data files but not in variables file. Unknown fields are read as character strings.")
    
    # IN PROGRESS - LEFT OFF HERE #
    
    # read data and append file names
    dat = dataset.dataset(source=tablepaths,format="csv",schema=tableschema)
    cols = tableschema.names
    cols.append("__filename")
    dattab = dat.to_table(columns=cols)
    pdat = dattab.to_pandas()    

    
    # # fieldNames each have a unique dataType - don't need to match table    
    # for i in list(d.columns):
    #     if i not in list(v.fieldName):
    #         d[i] = d[i].astype("string")
    #     else:
    #         type = v.colClass[v.fieldName == i]
    #         type=type[type.index[0]]
    #         if type == 'str':
    #             d[i] = d[i].astype("string")
    #         if type == 'datetime':
    #             d[i] = date_convert(d[i])
    #         if type in ['int','float']:
    #             d[i] = pd.to_numeric(d[i])
                
    return d

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
    d = date_convert("2023-08-01")
        
    Created on 2 May 2024
    
    @author: Claire Lunch
    """    
    
    try:
        dout=pd.to_datetime(dates, format = "%Y-%m-%dT%H:%M:%S", utc=True)
    except:
        try:
            dout=pd.to_datetime(dates, format = "%Y-%m-%dT%H:%M", utc=True)
        except:
            try:
                dout=pd.to_datetime(dates, format = "%Y-%m-%dT%H", utc=True)
            except:
                try:
                    dout=pd.to_datetime(dates, format = "%Y-%m-%d", utc=True)
                except:
                    dout=dates
    return dout

