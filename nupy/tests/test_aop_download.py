# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 17:00:19 2024

@author: bhass

Unit tests for by_file_aop and by_tile_aop.

These mainly test messages for invalid inputs, collocated sites, and provisional scenarios so far.

More complete functional testing is included in the nu_python_testing repository.
https://github.com/NEONScience/nu-python-testing

Notes:
- The capsys fixture captures the output of the function to enable checking the output messages
- Paramaterization allows for testing different sets of inputs with the same test
- The unittest "monkeypatch" mocks the user input to say "n" (no) to avoid downloading data

"""

# import required packages
import os
import shutil
from pathlib import Path
import glob
import pandas as pd
from shapely.geometry import Point
import geopandas as gpd
from neonutilities import by_file_aop, by_tile_aop

import pytest
from unittest import mock

# read in token from os.environ
token = os.environ.get("AOP_TOKEN")

### Test invalid inputs and make sure informational messages display correctly ###


def test_by_file_aop_invalid_dpid_format(capsys):
    """
    Test that the by_file_aop() function returns the expected error message when an invalid dpid format is provided
    """
    dpid = "DP1.0010"
    by_file_aop(dpid=dpid, site="MCRA", year=2021)
    out, err = capsys.readouterr()
    assert out == f'{dpid} is not a properly formatted data product ID. The correct format is DP#.#####.00#\n'


@pytest.mark.parametrize("year, site, dpid",
                         [
                             ("2019", "McRae", "DP3.30015.001"),
                             (2020, "mcra,abby", "DP3.30015.001"),
                         ],)
def test_by_file_aop_invalid_site_format(capsys, year, site, dpid):
    """
    Test that the by_file_aop() function returns the expected error message when an invalid site format is provided
    """
    by_file_aop(dpid=dpid, site=site, year=year)
    out, err = capsys.readouterr()
    assert out == f'{site.upper()} is an invalid site. A four-letter NEON site code is required. NEON sites codes can be found here: https://www.neonscience.org/field-sites/field-sites-map/list.\n'


@pytest.mark.parametrize("year", [("19"), (18), ],)
def test_by_file_aop_invalid_year_format(capsys, year):
    """
    Test that the by_file_aop() function returns the expected error message when an invalid year format is provided
    """
    by_file_aop(dpid="DP3.30015.001", site="MCRA", year=year)
    out, err = capsys.readouterr()
    assert out == f'{year} is an invalid year. Year is required in the format "2017", eg. Data are available from 2013 to present.\n'

# Test message if no data is available (eg. wrong site/year combination)


def test_by_file_aop_no_data_available_message(capsys, monkeypatch):
    """
    Test that the by_file_aop() function returns the expected error message when no data is available
    """
    monkeypatch.setattr('builtins.input', lambda _: "n")
    by_file_aop(dpid="DP3.30024.001", site="MCRA", year='2020')
    out, err = capsys.readouterr()
    assert out == 'There are no data available at the selected site and year.\n'

### Test collocated and regular sites ###
# The monkey patch mocks the user input to say "n" (no) to avoid downloading data

# These next two tests make an API request, so if there is a print statement in get_api for x-ratelimit-remaining,
# it will FAIL without a token. Should mock that part. And/or just test the get_shared_flights function?


@pytest.mark.parametrize("year, site, flightSite",
                         [
                             ("2022", "CHEQ", "STEI"),
                             ("2022", "TREE", "STEI"),
                             ("2021", "DCFS", "WOOD"),
                             ("2020", "KONA", "KONZ"),
                         ],)
def test_by_file_aop_collocated_site_message(capsys, monkeypatch, year, site, flightSite):
    """
    Test that the by_file_aop() function returns the expected message when a collocated terrestrial site is provided
    """
    monkeypatch.setattr('builtins.input', lambda _: "n")
    by_file_aop(dpid="DP3.30015.001", site=site, year=year, token=token)
    out, err = capsys.readouterr()
    assert out == f'{site} is part of the flight box for {flightSite}. Downloading data from {flightSite}.\nDownload halted.\n'


def test_by_file_aop_noncollocated_site_message(capsys, monkeypatch):
    """
    Test that the by_file_aop() function returns the expected message when a non-collocated terrestrial site is provided
    """
    site = "MCRA"
    monkeypatch.setattr('builtins.input', lambda _: "n")
    by_file_aop(dpid="DP3.30015.001", site=site, year="2021", token=token)
    out, err = capsys.readouterr()
    assert out == f'Download halted.\n'


### Test messages for varying scenarios of include_provisional with data unavailable / available for the provided inputs ###
# Note that these tests would need to change for a given year/data release, as provisional data is subject to change.
# These tests were written in Mar 2024 so work for the 2024 Release

def test_by_file_aop_all_provisional_no_data_available_message(capsys, monkeypatch):
    """
    Test that the by_file_aop() function returns the expected message when include_provisional is set to false (default) but no data are available.
    This has already run through the check that any data is available (eg. there is data at that site for the year provided)
    """
    site = "SCBI"
    monkeypatch.setattr('builtins.input', lambda _: "n")
    by_file_aop(dpid="DP3.30015.001", site=site, year="2023", token=token)
    out, err = capsys.readouterr()
    assert out == f'No data files found. Available data may all be provisional. To download provisional data, use input parameter include_provisional=True.\n'


def test_by_file_aop_provisional_included_and_data_available_message(capsys, monkeypatch):
    """
    Test that the by_file_aop() function returns the expected message when include_provisional is set to false (default) and data are available.
    """
    site = "STEI"
    monkeypatch.setattr('builtins.input', lambda _: "n")
    by_file_aop(dpid="DP3.30015.001", site=site, year="2022",
                include_provisional=True, token=token)
    out, err = capsys.readouterr()
    assert out == f'Provisional data are included. To exclude provisional data, use input parameter include_provisional=False.\nDownload halted.\n'
