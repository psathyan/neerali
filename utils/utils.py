# -*- coding: utf-8 -*-
"""Module contains use workflows for the core package."""
import random
from pathlib import Path
from string import ascii_lowercase, digits
from typing import Dict
from yaml import safe_load


class Singleton(type):
    """Ensures a single instance."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances.keys():
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)

        return cls._instances[cls]


def merge_dicts(source: Dict, target: Dict) -> None:
    """
    Return a merged dictionary.

    This method allows us to consider nested dictionaries so that all values are
    considered instead of second one alone

    Args:
        source (dict)    Dictionary that needs to be merged
        target (dict)    Dictionary that needs to contain the source

    Returns:
        None
    """
    for key, value in source.items():
        if key in target.keys():
            target[key].update(value)
            continue

        target.update({key: value})


def generate_unique_id(length: int = 1) -> str:
    """
    Returns a unique string of length requested in arguments.

    Args:
        length (int): Length of the string

    Returns:
        (str) a unique string
    """
    return "".join(random.choices(ascii_lowercase + digits, k=length))


def yaml_to_dict(filename: str) -> Dict:
    """Convert the contents of YAML to a dict."""
    file_name = Path(filename).absolute()

    with file_name.open('r') as fh:
        content = safe_load(fh)
        return content
