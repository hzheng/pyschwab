import os
import re
from datetime import datetime
from typing import Any, Dict


import requests

from .exceptions import BadRequestException, BrokerAPIException, HTTPErrorException, InternetConnectionException, ServerErrorException

def camel_to_snake(name):
    """
    Convert camelCase string to snake_case string.
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def get_value(config: Dict[str, Any], key: str, default_value: Any = None):
    val = config.get(key, default_value)
    if type(val) is str and val.startswith('$'):
        return os.getenv(val[1:])
    return val


def time_to_str(dt: datetime | str) -> str:
    if dt is None or isinstance(dt, str):
        return dt

    return f'{dt.isoformat()[:-3]}Z'


def str_to_time(dt: datetime | str) -> datetime:
    if dt is None or isinstance(dt, datetime):
        return dt

    return datetime.fromisoformat(dt)


def format_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Removes all key-value pairs from a dictionary where the value is None.

    Args:
    params (Dict[str, Any]): A dictionary whose keys are strings and values can be any type.

    Returns:
    Dict[str, Any]: The dictionary with None values removed.
    """
    return {key: value for key, value in params.items() if value is not None}


def request(url, method='GET', headers=None, params=None, data=None) -> requests.Response:
    try:
        response = requests.request(method=method, url=url, headers=headers, data=data, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response
    except requests.exceptions.HTTPError as e:
        if 400 <= response.status_code < 500:
            raise BadRequestException(f"Client error: {response.status_code} {response.reason}")
        if 500 <= response.status_code < 600:
            raise ServerErrorException(f"Server error: {response.status_code} {response.reason}")
        raise HTTPErrorException(f"HTTP error {response.status_code}: {response.reason}")
    except requests.exceptions.ConnectionError:
        raise InternetConnectionException("Check your internet connection.")
    except requests.exceptions.RequestException as e:
        raise BrokerAPIException(f"An error occurred while making a request: {str(e)}")
