#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time


def get_api(api_url,
            token=None):
    """

    Accesses the API with options to use the user-specific API token generated within neon.datascience user accounts.

    Parameters
    --------
    api_url: The API endpoint URL.
    token: User specific API token (generated within neon.datascience user accounts). Optional.

    Return
    --------
    API GET response containing status code and data that can be parsed into a json file

    Example
    --------
    Get the sample class for a surface water particulate stable isotope sample

    >>> sample_get = get_api(api_url='https://data.neonscience.org/api/v0/samples/classes?sampleTag=MCRA.SS.20230425.POM.1',token=None)

    Created on Fri Aug 30 2023

    @author: Zachary Nickerson
    """

    # Check internet connection
    check_connection = requests.get("https://data.neonscience.org/")
    if check_connection.status_code != 200:
        print("No internet connection detected. Cannot access NEON API.\n")
        return None

    # Make 5 request attempts. If the rate limit is reached, pause for the
    # burst reset time to try again.
    j = 1

    while (j <= 5):

        # Try making the request
        try:
            # Construct URL either with or without token
            if token is None:
                response = requests.get(api_url)
            else:
                response = requests.get(
                    api_url, headers={"X-API-TOKEN": token, "accept": "application/json"})

            # Check for successful response
            if response.status_code == 200:

                if 'x-ratelimit-limit' in dict(response.headers).keys():
                    # Retry get request if rate limit exceeded
                    limit_remain = dict(response.headers)[
                        'x-ratelimit-remaining']
                    # print(f"x-ratelimit-remaining: {limit_remain}")
                    if int(limit_remain) < 1:
                        # Wait for the reset time
                        time_reset = dict(response.headers)[
                            'x-ratelimit-reset']
                        print(
                            f"Rate limit reached. Pausing for {time_reset} seconds to reset.\n")
                        time.sleep(int(time_reset))
                        # Increment loop to retry request attempt
                        j += 1

                    else:
                        # If rate limit is not reached, exit out of loop
                        j += 5

                else:
                    # If x-ratelimit-limit not found in headers, exit out of
                    # loop (don't need to retry because of rate-limit)
                    j += 5
            else:
                # Return nothing if request failed (status code is not 200)
                print(
                    f"Request failed with status code {response.status_code}\n")
                return None

            return response

        except Exception as e:
            print(e)
            print("No response. NEON API may be unavailable, check NEON data portal for outage alerts. If the problem persists and can't be traced to an outage alert, check your computer for firewall or other security settings preventing Python from accessing the internet.")
            return None

# api_url = 'https://data.neonscience.org/api/v0/samples/classes?sampleTag=MCRA.SS.20230425.POM.1'
# token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJhdWQiOiJodHRwczovL2RhdGEubmVvbnNjaWVuY2Uub3JnL2FwaS92MC8iLCJzdWIiOiJuaWNrZXJzb25AYmF0dGVsbGVlY29sb2d5Lm9yZyIsInNjb3BlIjoicmF0ZTp1bmxpbWl0ZWQgcmVhZDpyZWxlYXNlcyByZWFkOnJlbGVhc2VzLWxhdGVzdCIsImlzcyI6Imh0dHBzOi8vZGF0YS5uZW9uc2NpZW5jZS5vcmcvIiwiZXhwIjoxNzkzNjQ2MTUyLCJpYXQiOjE2MzU5NjYxNTIsImVtYWlsIjoibmlja2Vyc29uQGJhdHRlbGxlZWNvbG9neS5vcmcifQ.dUyan8p2z42DWimkrRcxBUOBrbwL5dqPpF_55GqKbLnqZAFwcg6pjPu-ByugkaixeQqL7LL_BCny-GNjh7vlWw'
# get_api(api_url,token=None)
# response.json()
