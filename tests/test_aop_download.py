# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 17:00:19 2024

@author: bhass

Installation dependencies:
    conda install pytest
    conda install parameterized

Unit tests for by_file_aop and by_tile_aop.

These mainly test the function's output messages for invalid inputs, 
collocated sites, data not found, and provisional scenarios so far.

More complete functional testing is included in the nu_python_testing repository.
https://github.com/NEONScience/nu-python-testing

Notes:
- These tests require an internet connection to run, as they are actually making API calls
- Paramaterization with the @parameterized.expand decorator allows for testing different sets of inputs with the same test
    This requires the parameterized package (pip install parameterized)
- The @patch('builtins.input', return_value='n') decorator mocks the user input to say "n" (no) to avoid downloading data


"""

# import required packages

import os
from src.neonutilities.aop_download import by_file_aop, by_tile_aop

import pytest
import unittest
from unittest.mock import patch
from parameterized import parameterized

# read in token from os.environ
token = os.environ.get("NEON_TOKEN")

# Test invalid inputs and make sure informational messages display correctly ###

# similar tests for by_file_aop and by_tile_aop, with some additional tests for by_tile_aop

# TestByFileAOP
# TestByTileAOP


class TestByFileAOP(unittest.TestCase):
    def setUp(self):
        """Set up before each test"""
        # these are valid inputs, invalid inputs for testing logs / messages are supplied within each test
        self.dpid = "DP3.30015.001"
        self.site = "MCRA"
        self.year = 2021

    def test_invalid_dpid_format(self):
        """
        Test that invalid dpid format raises ValueError and message displays correctly.
        """
        invalid_dpid = "DP1.30001"
        with self.assertRaises(ValueError, msg=f'{invalid_dpid} is not a properly formatted data product ID. The correct format is DP#.#####.00#'):
            by_file_aop(dpid=invalid_dpid, site=self.site, year=self.year)

    def test_check_field_spectra_dpid(self):
        """
        Test that providing field spectra dpid raises ValueError and message displays correctly.
        """
        field_spectra_dpid = 'DP1.30012.001'
        with self.assertRaises(ValueError, msg=f'{field_spectra_dpid} is the Field spectral data product, which is published as tabular data. Use zipsByProduct() or loadByProduct() to download these data.'):
            by_file_aop(dpid=field_spectra_dpid,
                        site=self.site, year=self.year)

    def test_invalid_site_format(self):
        """
        Test that invalid site format raises ValueError and message displays correctly.
        """
        invalid_site = 'McRae'
        with self.assertRaises(ValueError, msg=f'{invalid_site} is an invalid site. A four-letter NEON site code is required. NEON sites codes can be found here: https://www.neonscience.org/field-sites/field-sites-map/list.'):
            by_file_aop(dpid=self.dpid, site=invalid_site, year=self.year)

    @parameterized.expand([("21",), ("2021-05",), ])
    def test_invalid_year_format(self, year):
        """
        Test that invalid year format raises ValueError and message displays correctly.
        """
        with pytest.raises(ValueError, match=f'{year} is an invalid year. Year is required in the format "2017" or 2017, eg. AOP data are available from 2013 to present.'):
            by_file_aop(dpid=self.dpid, site=self.site, year=year)

    @parameterized.expand([
        ("2022", "CHEQ", "STEI"),
        ("2022", "TREE", "STEI"),
        ("2021", "DCFS", "WOOD"),
        ("2020", "KONA", "KONZ"),
    ], name_func=lambda f, n, p: f'{f.__name__}_{p.args[1]}_{p.args[0]}')
    # the name_func displays a more descriptive test name when running the tests
    @patch('builtins.input', return_value='n')
    def test_collocated_terrestrial_site_message(self, year, site, flightSite, input_mock):
        """
        Test application of the terrestrial collocated site lookup, and expected message display.
        """
        with self.assertLogs(level='INFO') as cm:
            by_file_aop(dpid="DP3.30015.001", site=site,
                        year=year, token=token)
            self.assertIn(
                f'INFO:root:{site} is part of the flight box for {flightSite}. Downloading data from {flightSite}.', cm.output)

    @parameterized.expand([
        ("2018", "BARC", "OSBS"),
        ("2020", "COMO", "NIWO"),
        # ("2021", "BLDE", "YELL"),
        # ("2020", "KING", "KONZ"),
    ], name_func=lambda f, n, p: f'{f.__name__}_{p.args[1]}_{p.args[0]}')
    @patch('builtins.input', return_value='n')
    def test_collocated_aquatic_site_message(self, year, site, flightSite, input_mock):
        """
        Test application of the aquatic collocated site lookup, and expected message display.
        """
        with self.assertLogs(level='INFO') as cm:
            by_file_aop(dpid=self.dpid, site=site,
                        year=year, token=token)
            self.assertIn(
                f'INFO:root:{site} is an aquatic site and is sometimes included in the flight box for {flightSite}. Aquatic sites are not always included in the flight coverage every year.\nDownloading data from {flightSite}. Check data to confirm coverage of {site}.', cm.output)

    # @patch('builtins.input', return_value='n')
    def test_no_data_available_message(self):
        """
        Test that the by_file_aop() function returns the expected error log when no data is available for a selected site and year.
        """
        with self.assertLogs(level='INFO') as cm:
            by_file_aop(dpid="DP3.30015.001", site=self.site, year=2020)
            self.assertIn(
                'INFO:root:There are no data available at the selected site and year.', cm.output)

    @patch('builtins.input', return_value='n')
    def test_check_download_size_message(self, input_mock):
        """
        Test that download check_size message displays correctly.
        """
        result = by_file_aop(dpid=self.dpid, site=self.site, year=self.year)
        # Check that the function asked for confirmation to download and prints expected message.
        input_mock.assert_called_once_with(
            'Continuing will download 128 files totaling approximately 97.7 MB. Do you want to proceed? (y/n) ')
        # Check that the function halted the download
        self.assertEqual(result, None)

    # Provisional scenarios

    # provisional not included, and no data available
    def test_all_provisional_no_data_available_message(self):
        """
        Test that the by_file_aop() function returns the expected message when include_provisional is set to False (default) but no data are available.
        This has already run through the check that any data is available (eg. there is data at that site for the year provided)
        """
        with self.assertLogs(level='INFO') as cm:
            by_file_aop(dpid="DP3.30015.001", site="SCBI", year=2023)
            self.assertIn(
                'INFO:root:No data files found. Available data may all be provisional. To download provisional data, use input parameter include_provisional=True.', cm.output)

    # provisional included, and no data available
    @patch('builtins.input', return_value='n')
    def test_provisional_included_and_data_available_message(self, input_mock):
        """
        Test that the by_file_aop() function returns the expected message when include_provisional is set to False (default) but no data are available.
        This has already run through the check that any data is available (eg. there is data at that site for the year provided)
        """
        with self.assertLogs(level='INFO') as cm:
            by_file_aop(dpid="DP3.30015.001", site="SCBI",
                        year=2023, include_provisional=True)
            self.assertIn(
                'INFO:root:Provisional data are included. To exclude provisional data, use input parameter include_provisional=False.', cm.output)

    # other scenarios- check messages but don't donwload the data ?
    # provisional not included, and data available
    # provisional included, and data available


class TestByTileAop(unittest.TestCase):
    def setUp(self):
        """Set up before each test"""
        # these are valid inputs, invalid inputs for each tests are supplied within each test
        self.dpid = "DP3.30015.001"
        self.easting = 566000
        self.northing = 4900000
        self.site = "MCRA"
        self.year = 2021

    def test_invalid_dpid_format(self):
        invalid_dpid = "DP1.30001"
        with self.assertRaises(ValueError, msg=f'{invalid_dpid} is not a properly formatted data product ID. The correct format is DP#.#####.00#'):
            by_tile_aop(dpid=invalid_dpid, site=self.site, year=self.year,
                        easting=self.easting, northing=self.northing)

    def test_check_field_spectra_dpid(self):
        field_spectra_dpid = 'DP1.30012.001'
        with self.assertRaises(ValueError, msg=f'{field_spectra_dpid} is the Field spectral data product, which is published as tabular data. Use zipsByProduct() or loadByProduct() to download these data.'):
            by_tile_aop(dpid=field_spectra_dpid, site=self.site, year=self.year,
                        easting=self.easting, northing=self.northing)

    def test_invalid_site_format(self):
        invalid_site = 'McRae'
        with self.assertRaises(ValueError, msg=f'{invalid_site} is an invalid site. A four-letter NEON site code is required. NEON sites codes can be found here: https://www.neonscience.org/field-sites/field-sites-map/list.'):
            by_tile_aop(dpid=self.dpid, site=invalid_site, year=self.year,
                        easting=self.easting, northing=self.northing)

    @parameterized.expand([("21",), ("2021-05",), ])
    def test_invalid_year_format(self, year):
        """
        Test that invalid year format raises ValueError and message displays correctly.
        """
        with pytest.raises(ValueError, match=f'{year} is an invalid year. Year is required in the format "2017" or 2017, eg. AOP data are available from 2013 to present.'):
            by_tile_aop(dpid=self.dpid, site=self.site, year=year,
                        easting=self.easting, northing=self.northing)

    @parameterized.expand([
        ("2022", "CHEQ", "STEI"),
        ("2022", "TREE", "STEI"),
        ("2021", "DCFS", "WOOD"),
        ("2020", "KONA", "KONZ"),
    ], name_func=lambda f, n, p: f'{f.__name__}_{p.args[1]}_{p.args[0]}')
    # the name_func displays a more descriptive test name when running the tests
    @patch('builtins.input', return_value='n')
    def test_collocated_terrestrial_site_message(self, year, site, flightSite, input_mock):
        """
        Test application of the terrestrial collocated site lookup, and expected message display.
        """
        with self.assertLogs(level='INFO') as cm:
            by_tile_aop(dpid=self.dpid, site=site,
                        year=year, easting=[], northing=[])
            self.assertIn(
                f'INFO:root:{site} is part of the flight box for {flightSite}. Downloading data from {flightSite}.', cm.output)

    @parameterized.expand([
        ("2018", "BARC", "OSBS"),
        ("2020", "COMO", "NIWO"),
        # ("2021", "BLDE", "YELL"),
        # ("2020", "KING", "KONZ"),
    ], name_func=lambda f, n, p: f'{f.__name__}_{p.args[1]}_{p.args[0]}')
    @patch('builtins.input', return_value='n')
    def test_collocated_aquatic_site_message(self, year, site, flightSite, input_mock):
        """
        Test application of the aquatic collocated site lookup, and expected message display.
        """
        with self.assertLogs(level='INFO') as cm:
            by_tile_aop(dpid=self.dpid, site=site,
                        year=year, easting=[], northing=[])
            self.assertIn(
                f'INFO:root:{site} is an aquatic site and is sometimes included in the flight box for {flightSite}. Aquatic sites are not always included in the flight coverage every year.\nDownloading data from {flightSite}. Check data to confirm coverage of {site}.', cm.output)

    def test_no_data_available_message(self):
        """
        Test that the by_tile_aop() function returns the expected error log when no data is available for a selected site and year.
        """
        with self.assertLogs(level='INFO') as cm:
            by_tile_aop(dpid="DP3.30015.001", site=self.site,
                        year=2020, easting=self.easting, northing=self.northing)
            self.assertIn(
                'INFO:root:There are no data available at the selected site and year.', cm.output)

    def test_no_data_files_found_message(self):
        """
        Test that the by_tile_aop() function returns the expected error log when no data files are found.
        """
        with self.assertLogs(level='INFO') as cm:
            by_tile_aop(dpid="DP3.30015.001", site=self.site,
                        year=2020, easting=564000, northing=4900000)
            self.assertIn(
                'INFO:root:There are no data available at the selected site and year.', cm.output)

    @patch('builtins.input', return_value='n')
    def test_check_download_size_message(self, input_mock):
        """
        Test that download check_size message displays correctly.
        """
        result = by_tile_aop(dpid=self.dpid, site=self.site,
                             year=self.year, easting=self.easting, northing=self.northing)
        # Check that the function asked for confirmation to download and prints expected message.
        input_mock.assert_called_once_with(
            'Continuing will download 7 files totaling approximately 4.0 MB. Do you want to proceed? (y/n) ')
        # Check that the function halted the download
        self.assertEqual(result, None)

    # Provisional scenarios

    # provisional not included, and no data available
    # these tests should be mocked, as provisional data changes with each NEON Data Release
    def test_all_provisional_no_data_available_message(self):
        """
        Test that the by_tile_aop() function returns the expected message when include_provisional is set to False (default) but no data are available.
        This has already run through the check that any data is available (eg. there is data at that site for the year provided)
        """
        with self.assertLogs(level='INFO') as cm:
            by_tile_aop(dpid=self.dpid, site=self.site, year=2023,
                        easting=self.easting, northing=self.northing)
            self.assertIn(
                'INFO:root:No data files found. Available data may all be provisional. To download provisional data, use input parameter include_provisional=True.', cm.output)

    # provisional included, and no data available
    @patch('builtins.input', return_value='n')
    def test_provisional_included_and_data_available_message(self, input_mock):
        """
        Test that the by_file_aop() function returns the expected message when include_provisional is set to False (default) but no data are available.
        This has already run through the check that any data is available (eg. there is data at that site for the year provided)
        """
        with self.assertLogs(level='INFO') as cm:
            by_tile_aop(dpid=self.dpid, site=self.site, year=2023,
                        include_provisional=True, easting=self.easting, northing=self.northing)
            self.assertIn(
                'INFO:root:Provisional data are included. To exclude provisional data, use input parameter include_provisional=False.', cm.output)

    @patch('builtins.input', return_value='n')
    @patch('importlib.import_module')
    @patch('logging.info')
    def test_pyproj_not_installed(self, logging_mock, import_module_mock, input_mock):
        # Setup the mock to raise ImportError when pyproj is attempted to be imported
        import_module_mock.side_effect = ImportError(
            "No module named 'pyproj'")

        by_tile_aop(dpid="DP3.30015.001", site='BLAN', year=2022,
                    easting=243758.81, northing=4330667.37,
                    include_provisional=False, verbose=True)

        # Check if logging.info was called with the correct message
        # There will also be a message about the include_provisional, so can't use assert_called_once_with
        logging_mock.assert_any_call(
            "Package pyproj is required for this function to work at the BLAN site. Install and re-try"
        )

    @patch('builtins.input', return_value='n')
    def test_blan_utm_info_message(self, input_mock):
        """
        Test that the by_tile_aop() function returns the expected message about UTM zone conversion when BLAN is the site.
        """
        with self.assertLogs(level='INFO') as cm:
            by_tile_aop(dpid="DP3.30015.001", site='BLAN', year=2022,
                        easting=243758.81, northing=4330667.37, verbose=True)
            self.assertIn('INFO:root:Blandy (BLAN) plots include two UTM zones, flight data are all in 17N. '
                          'Coordinates in UTM zone 18N have been converted to 17N to download the correct tiles. '
                          'You will need to make the same conversion to connect airborne to ground data.', cm.output)

    # this should work with parameterized package (!pip install parameterized, from parameterized import parameterized)
    # @parameterized.expand([
    #     ("McRae",),
    #     ("mcra,abby",),
    # ])
    # def test_invalid_site_format(self, site):
    #     with self.assertRaises(ValueError, msg=f'{site} is an invalid site. A four-letter NEON site code is required. NEON sites codes can be found here: https://www.neonscience.org/field-sites/field-sites-map/list.'):
    #         my_module.by_tile_aop(dpid=self.dpid, site=site, year=self.year, easting=self.easting, northing=self.northing)

    # @pytest.mark.parametrize("site", [("McRae"), ("mcra,abby"), ],)
    # def test_invalid_site_format(self, site):
    #     """
    #     Test that the by_file_aop() function returns the expected error message when an invalid site format is provided
    #     """
    #     with self.assertRaises(ValueError, msg=f'{site} is an invalid site. A four-letter NEON site code is required. NEON sites codes can be found here: https://www.neonscience.org/field-sites/field-sites-map/list.'):
    #         by_tile_aop(dpid=self.dpid, site=site, year=self.year,
    #                     easting=self.easting, northing=self.northing)
        # by_tile_aop(dpid=self.dpid, site=site, year=self.year,easting=self.easting, northing=self.northing)
        # # out, err = capsys.readouterr()
        # assert out == f'{site.upper()} is an invalid site. A four-letter NEON site code is required. NEON sites codes can be found here: https://www.neonscience.org/field-sites/field-sites-map/list.\n'


# OLD CODE, using pytest, outside of testing classes

# Notes:
# - The capsys fixture captures the output of the function to enable checking the output messages
# - @pytest.mark.parametrize allows for testing different sets of inputs with the same test
# - The unittest "monkeypatch" mocks the user input to say "n" (no) to avoid downloading data

    # @pytest.mark.parametrize("year",
    #                          [("19"), ("2018-05"), ],)
    # def test_by_file_aop_invalid_year_format(year):
    #     """
    #     Test that the by_file_aop() function returns the expected error message when an invalid site format is provided
    #     """
    #     with pytest.raises(ValueError, match=f'{year} is an invalid year. Year is required in the format "2017" or 2017, eg. AOP data are available from 2013 to present.'):
    #         by_file_aop(dpid="DP3.30015.001", site="MCRA", year=year)

    # @pytest.mark.parametrize("year",
    #                          [("19"), ("2018-05"), ],)
    # def test_by_file_aop_invalid_year_format(year):
    #     """
    #     Test that the by_file_aop() function returns the expected error message when an invalid site format is provided
    #     """
    #     with pytest.raises(ValueError, match=f'{year} is an invalid year. Year is required in the format "2017" or 2017, eg. AOP data are available from 2013 to present.'):
    #         by_file_aop(dpid="DP3.30015.001", site="MCRA", year=year)

# def test_by_file_aop_invalid_dpid_format():
#     dpid = "DP1.0010"
#     with pytest.raises(ValueError, match=f'{dpid} is not a properly formatted data product ID. The correct format is DP#.#####.00#'):
#         by_file_aop(dpid=dpid, site="MCRA", year=2021)
#         # validate_dpid(dpid)


# def test_by_file_aop_check_field_spectra_dpid():
#     dpid = 'DP1.30012.001'
#     with pytest.raises(ValueError, match=f'{dpid} is the Field spectral data product, which is published as tabular data. Use zipsByProduct() or loadByProduct() to download these data.'):
#         by_file_aop(dpid=dpid, site="MCRA", year=2021)

# def test_by_file_aop_invalid_dpid_format(capsys):
#     """
#     Test that the by_file_aop() function returns the expected error message when an invalid dpid format is provided
#     """
#     dpid = "DP1.0010"
#     by_file_aop(dpid=dpid, site="MCRA", year=2021)
#     out, err = capsys.readouterr()
#     assert out == f'{dpid} is not a properly formatted data product ID. The correct format is DP#.#####.00#\n'


# @pytest.mark.parametrize("year, site, dpid",
#                          [
#                              ("2019", "McRae", "DP3.30015.001"),
#                              (2020, "mcra,abby", "DP3.30015.001"),
#                          ],)
# def test_by_file_aop_invalid_site_format(capsys, year, site, dpid):
#     """
#     Test that the by_file_aop() function returns the expected error message when an invalid site format is provided
#     """
#     by_file_aop(dpid=dpid, site=site, year=year)
#     out, err = capsys.readouterr()
#     assert out == f'{site.upper()} is an invalid site. A four-letter NEON site code is required. NEON sites codes can be found here: https://www.neonscience.org/field-sites/field-sites-map/list.\n'

# @pytest.mark.parametrize("site",
#                          [
#                              ("McRae"),
#                              ("mcra,abby"),
#                          ],)
# def test_by_file_aop_invalid_site_format(site):
#     """
#     Test that the by_file_aop() function returns the expected error message when an invalid site format is provided
#     """
#     dpid = "DP3.30015.001"
#     with pytest.raises(ValueError, match=f'{site.upper()} is an invalid site. A four-letter NEON site code is required. NEON sites codes can be found here: https://www.neonscience.org/field-sites/field-sites-map/list'):
#         by_file_aop(dpid=dpid, site=site, year=2021)


# @pytest.mark.parametrize("year", [("19"), (18), ],)
# def test_by_file_aop_invalid_year_format(capsys, year):
#     """
#     Test that the by_file_aop() function returns the expected error message when an invalid year format is provided
#     """
#     by_file_aop(dpid="DP3.30015.001", site="MCRA", year=year)
#     out, err = capsys.readouterr()
#     assert out == f'{year} is an invalid year. Year is required in the format "2017", eg. Data are available from 2013 to present.\n'


### Test collocated and regular sites ###
# The monkey patch mocks the user input to say "n" (no) to avoid downloading data

# These next two tests make an API request, so if there is a print statement in get_api for x-ratelimit-remaining,
# it will FAIL without a token. Should mock that part. And/or just test the get_shared_flights function?


# @pytest.mark.parametrize("year, site, flightSite",
#                          [
#                              ("2022", "CHEQ", "STEI"),
#                              ("2022", "TREE", "STEI"),
#                              ("2021", "DCFS", "WOOD"),
#                              ("2020", "KONA", "KONZ"),
#                          ],)
# def test_by_file_aop_collocated_site_message(capsys, monkeypatch, year, site, flightSite):
#     """
#     Test that the by_file_aop() function returns the expected message when a collocated terrestrial site is provided
#     """
#     monkeypatch.setattr('builtins.input', lambda _: "n")
#     by_file_aop(dpid="DP3.30015.001", site=site, year=year, token=token)
#     out, err = capsys.readouterr()
#     assert out == f'{site} is part of the flight box for {flightSite}. Downloading data from {flightSite}.\nDownload halted.\n'


# def test_by_file_aop_noncollocated_site_message(capsys, monkeypatch):
#     """
#     Test that the by_file_aop() function returns the expected message when a non-collocated terrestrial site is provided
#     """
#     site = "MCRA"
#     monkeypatch.setattr('builtins.input', lambda _: "n")
#     by_file_aop(dpid="DP3.30015.001", site=site, year="2021", token=token)
#     out, err = capsys.readouterr()
#     assert out == f'Download halted.\n'


### Test messages for varying scenarios of include_provisional with data unavailable / available for the provided inputs ###
# Note that these tests would need to change for a given year/data release, as provisional data is subject to change.
# These tests were written in Mar 2024 so work for the 2024 Release

# def test_by_file_aop_all_provisional_no_data_available_message(capsys, monkeypatch):
#     """
#     Test that the by_file_aop() function returns the expected message when include_provisional is set to false (default) but no data are available.
#     This has already run through the check that any data is available (eg. there is data at that site for the year provided)
#     """
#     site = "SCBI"
#     monkeypatch.setattr('builtins.input', lambda _: "n")
#     by_file_aop(dpid="DP3.30015.001", site=site, year="2023", token=token)
#     out, err = capsys.readouterr()
#     assert out == f'No data files found. Available data may all be provisional. To download provisional data, use input parameter include_provisional=True.\n'


# def test_by_file_aop_provisional_included_and_data_available_message(capsys, monkeypatch):
#     """
#     Test that the by_file_aop() function returns the expected message when include_provisional is set to false (default) and data are available.
#     """
#     site = "STEI"
#     monkeypatch.setattr('builtins.input', lambda _: "n")
#     by_file_aop(dpid="DP3.30015.001", site=site, year="2022",
#                 include_provisional=True, token=token)
#     out, err = capsys.readouterr()
#     assert out == f'Provisional data are included. To exclude provisional data, use input parameter include_provisional=False.\nDownload halted.\n'
