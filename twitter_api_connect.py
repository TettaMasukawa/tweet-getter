import sys
import time
from datetime import datetime

import requests


def waitUntilReset(reset):
    """
    reset 時刻まで sleep
    """
    seconds = reset - time.mktime(datetime.now().timetuple())
    seconds = max(seconds, 0)
    print("\n     =====================")
    print("     == waiting %d sec ==" % seconds)
    print("     =====================")
    sys.stdout.flush()
    time.sleep(seconds + 30)


def connect_to_endpoint(url, params, headers):

    response = requests.request("GET", url, params=params, headers=headers)

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)

    return response, response.json()

def connect_to_endpoint_next_token(url, params1, params2, headers, next_token=None):
    
    if next_token is not None:
        params = params1
    else:
        params = params2
    
    response = requests.request("GET", url, params=params, headers=headers)

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)

    return response, response.json()
