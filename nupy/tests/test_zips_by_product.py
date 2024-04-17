# -*- coding: utf-8 -*-
"""
Created on 14 Mar 2024

@author: Claire Lunch

Unit tests for zips_by_product()

Mocking is not used here, tests access API resources. Tests here primarily test for error handling.

"""

# import required packages
import os
from neonutilities import zips_by_product

import pytest

# read in token from os.environ
token = os.environ.get("NEON_TOKEN")

### Test a provisional and a release citation ###

def test_zips_by_product_dpid(capsys):
    """
    Test that the zips_by_product() function errors correctly for an invalid DPID
    """
    murls = zips_by_product(dpID='DP1.444.001', site='NIWO',
                           startdate='2012-01', enddate='2022-12')
    captured = capsys.readouterr()
    assert captured.out == "DP1.444.001 is not a properly formatted data product ID. The correct format is DP#.#####.00#\n"

