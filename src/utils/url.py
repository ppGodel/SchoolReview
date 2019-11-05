import re
import urllib.parse
from functools import lru_cache
from typing import Optional, Union, Dict, List

import requests


def _remove_protocol_from_url(url: str):
    return_url = url
    is_match = re.match('https?://', url)
    if is_match:
        return_url = url.replace(is_match.group(0), '')
    return return_url


@lru_cache(maxsize=None)
def get_response_content(download_url) -> bytes:
    content = None
    response = requests.get(download_url)
    if response.status_code >= 200 <= 250:
        content = response.content
    return content


@lru_cache(maxsize=None)
def get_response_json(url) -> Optional[Union[Dict, List[Dict]]]:
    response = requests.get(url)
    json = None
    if response.status_code >= 200 <= 250:
        json = response.json()
    return json


def get_url(base_url: str, params: str):
    return "{base}?{parameters}".format(base=base_url, parameters=params)


def map_parameters(**params):
    parameters = None
    if params:
        parameters = "&".join([f"{urllib.parse.quote(k)}={urllib.parse.quote(v)}" for (k, v) in params.items()])
    return parameters


def get_base_url(url_template: str, **kwargs):
    return url_template.format(**kwargs)