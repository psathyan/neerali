"""Module contains use workflows for the core package."""
import logging
import random
from string import ascii_lowercase, digits
from typing import Dict

LOG = logging.getLogger(__name__)


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
