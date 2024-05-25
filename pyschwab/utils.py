import json
import os
import re
from datetime import datetime, date, timedelta, UTC
from enum import Enum
from typing import Any, Dict, List

import holidays
import requests

from .exceptions import BadRequestException, BrokerAPIException, HTTPErrorException, InternetConnectionException, ServerErrorException

def camel_to_snake(name):
    """
    Convert camelCase string to snake_case string.
    """
    if not name:
        return name

    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    return "_" + s2 if s2[0].isdigit() else s2


def snake_to_camel(name):
    """
    Convert snake_case string to camelCase string.
    """
    components = name.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def dataclass_to_dict(instance):
    """
    Convert a dataclass instance to a dictionary with camelCase keys.
    Handles nested dataclass instances as well.
    """
    if instance is None:
        return instance
    if isinstance(instance, Enum):
        return instance.value
    if isinstance(instance, list):
        return [dataclass_to_dict(item) for item in instance]
    if not hasattr(instance, '__dataclass_fields__'):
        return instance

    result = {}
    for field_name in instance.__dataclass_fields__.keys():
        value = getattr(instance, field_name)
        key = snake_to_camel(field_name)
        result[key] = dataclass_to_dict(value)
    return result


def is_subset_object(base_obj: Any, full_obj: Any) -> bool:
    """
    Recursively check if the object base_obj is a subset of full_obj, respecting the order for lists.
    This function handles dictionaries, lists, and other comparable data types recursively.

    Args:
        base_obj (any): The base object to verify, can be a dict, list, or other types.
        full_obj (any): The object that contains additional elements or key/value pairs.

    Returns:
        bool: True if base_obj is a subset of full_obj with order respected for lists, False otherwise.
    """
    if type(base_obj) != type(full_obj):
        return False

    if isinstance(base_obj, dict):
        for key, value in base_obj.items():
            if key not in full_obj:
                return False
            if not is_subset_object(value, full_obj[key]):
                return False
        return True

    if isinstance(base_obj, list):
        if len(base_obj) != len(full_obj):
            return False
        return all(is_subset_object(base_item, full_item) for base_item, full_item in zip(base_obj, full_obj))
        
    return base_obj == full_obj


def get_value(config: Dict[str, Any], key: str, default_value: Any = None) -> str:
    val = config.get(key, default_value)
    if type(val) is str and val.startswith('$'):
        return os.getenv(val[1:])
    return val


def time_to_str(dt: datetime | str, format: str=None) -> str:
    if dt is None or isinstance(dt, str):
        return dt

    if format is not None:
        return dt.strftime(format)

    return f'{dt.isoformat()[:-3]}Z'


def time_to_int(dt: datetime) -> int:
    if dt is None or isinstance(dt, str):
        return dt

    return int(dt.timestamp() * 1000)


def to_time(dt: datetime | str | int) -> datetime:
    if dt is None or isinstance(dt, datetime):
        return dt

    if isinstance(dt, int):
        return datetime.fromtimestamp(dt / 1000, UTC)

    if isinstance(dt, str):
        return datetime.fromisoformat(dt)
 
    raise ValueError("Invalid datetime format.")


def next_sunday():
    today = datetime.now()
    days_until_sunday = (6 - today.weekday()) % 7
    days_until_sunday = 7 if days_until_sunday == 0 else days_until_sunday
    return today + timedelta(days=days_until_sunday)


def next_market_open_day():
    today = datetime.now()
    us_holidays = holidays.US(years=[today.year, today.year + 1])
    next_day = today + timedelta(days=1)
    while True:
        if next_day.weekday() not in [5, 6] and next_day not in us_holidays:
            return next_day

        next_day += timedelta(days=1)


def is_market_closed(dt: datetime=None) -> bool:
    dt = dt if dt else datetime.now()
    if dt.weekday() in [5, 6]:
        return True

    return dt in holidays.US(years=[dt.year, dt.year + 1])


def format_param(param: Any) -> str | List[str]:
    if param is None:
        return ""

    if isinstance(param, Enum):
        return param.value

    if isinstance(param, list):
        return [format_param(p) for p in param]

    return str(param)


def format_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Removes all key-value pairs from a dictionary where the value is None.

    Args:
    params (Dict[str, Any]): A dictionary whose keys are strings and values can be any type.

    Returns:
    Dict[str, Any]: The dictionary with None values removed.
    """
    return {key: format_param(value) for key, value in params.items() if value is not None}


def format_list(lst: str | List) -> str:
    if lst is None or isinstance(lst, str):
        return lst

    return ",".join(lst)

def remove_none_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively remove all keys with None values from the dictionary.

    Args:
    data (dict): The dictionary to clean.

    Returns:
    dict: The cleaned dictionary with no None values.
    """
    if not isinstance(data, dict):
        return data

    clean_dict = {}
    for key, value in data.items():
        if isinstance(value, dict):
            nested_clean_dict = remove_none_values(value)
            if nested_clean_dict:  # only add non-empty nested dictionaries
                clean_dict[key] = nested_clean_dict
        elif isinstance(value, list):
            clean_list = [remove_none_values(item) for item in value]
            if clean_list:  # only add non-empty lists
                clean_dict[key] = clean_list
        elif value is not None:
            clean_dict[key] = value

    return clean_dict


def to_json_str(obj):
    def json_encode(obj):
        """Custom JSON serializer for objects not serializable by default json code."""
        if isinstance(obj, datetime) or isinstance(obj, date):
            return obj.isoformat()

        return obj 

    return json.dumps(obj, default=json_encode)

def request(url, method='GET', headers=None, params=None, data=None, json=None) -> requests.Response:
    try:
        response = requests.request(method=method, url=url, headers=headers, params=params, data=data, json=json)
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
