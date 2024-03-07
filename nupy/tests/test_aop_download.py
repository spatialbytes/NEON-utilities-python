# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 17:00:19 2024

@author: bhass

Unit tests for by_file_aop and by_tile_aop.

These mainly test invalid inputs so far.

More complete functional testing is included in the nu_python_testing repository.
https://github.com/NEONScience/nu-python-testing
"""
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

# probably shouldn't have token hard-coded like this, but it works for now
token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJhdWQiOiJodHRwczovL2RhdGEubmVvbnNjaWVuY2Uub3JnL2FwaS92MC8iLCJzdWIiOiJuaWNrZXJzb25AYmF0dGVsbGVlY29sb2d5Lm9yZyIsInNjb3BlIjoicmF0ZTp1bmxpbWl0ZWQgcmVhZDpyZWxlYXNlcyByZWFkOnJlbGVhc2VzLWxhdGVzdCIsImlzcyI6Imh0dHBzOi8vZGF0YS5uZW9uc2NpZW5jZS5vcmcvIiwiZXhwIjoxNzkzNjQ2MTUyLCJpYXQiOjE2MzU5NjYxNTIsImVtYWlsIjoibmlja2Vyc29uQGJhdHRlbGxlZWNvbG9neS5vcmcifQ.dUyan8p2z42DWimkrRcxBUOBrbwL5dqPpF_55GqKbLnqZAFwcg6pjPu-ByugkaixeQqL7LL_BCny-GNjh7vlWw'


# test print-out messages for incorrect inputs using capsys fixture
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

# These next two tests are making API request, so if there is a print statement in get_api for x-ratelimit-remaining,
# it will FAIL without a token. Should mock that part. And/or just test the get_shared_flights function?


@pytest.mark.parametrize("year, site, flightSite",
                         [
                             ("2022", "CHEQ", "STEI"),
                             ("2022", "TREE", "STEI"),
                             ("2021", "DCFS", "WOOD"),
                             ("2020", "KONA", "KONZ"),
                         ],)
def test_by_file_aop_collocated_site_message(capsys, monkeypatch, year, site, flightSite):
    monkeypatch.setattr('builtins.input', lambda _: "n")
    by_file_aop(dpid="DP3.30015.001", site=site, year=year, token=token)
    out, err = capsys.readouterr()
    assert out == f'{site} is part of the flight box for {flightSite}. Downloading data from {flightSite}.\nDownload halted.\n'


def test_by_file_aop_noncollocated_site_message(capsys, monkeypatch):
    site = "STEI"
    monkeypatch.setattr('builtins.input', lambda _: "n")
    by_file_aop(dpid="DP3.30015.001", site=site, year="2022", token=token)
    out, err = capsys.readouterr()
    assert out == f'Download halted.\n'
