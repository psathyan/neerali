# -*- code: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
    name: conf2cmds
    short_description: Convert a dictionary into a list of commands.
    positional: _input
    options:
      _input:
        description: Dictionary to be converted to commands
        type: dictionary
        required: true
"""


EXAMPLES = """
    # This example uses dict2args
    _args: "{{ argumets | neerali.general.conf2cmds }}"

    # Returns a list of strings that can be passed to the command line.
"""


RETURN = """
    _value:
      description: The CLI arguments as a string.
      type: list
      elements: str
"""

from ansible.errors import AnsibleFilterTypeError


def data_parser(payload, prefix=[]):
    """Parse the given payload.

    The parser traverses the items in the dictionary and on encountering a dict
    it calls itself recursively. The prefix holds the path it has traversed so
    it can be used to create the final argument.

    Args:
      payload (dict)   The dictionary that needs to be processed
      prefix (list)    This should not be set by the user. It is used to hold
                       the path traversed so far.

    Returns:
      A comma seperate string.
    """
    _result = ""
    for k, v in payload.items():
        if isinstance(v, dict):
            prefix.append(k)
            _result += data_parser(v, prefix)
            continue

        prefix_str = " ".join(prefix)

        if isinstance(v, list):
            for i in v:
                _result += f"{prefix_str} {k} {i}," if prefix else f"{k} {i},"
            continue

        _result += f"{prefix_str} {k} {v}," if prefix else f"{k} {v},"

    if prefix:
        prefix.pop()

    return _result


class FilterModule:
    """Filter module class."""

    @classmethod
    def _conf2cmds(cls, data):
        """Returns a list of commands for ceph cluster tuning."""
        if not isinstance(data, dict):
            raise AnsibleFilterTypeError(
                f"get_reimage_nodes requires dict, got {type(data)}"
            )

        result = data_parser(data)
        return result.strip(",").split(",")

    def filters(self):
        return {"conf2cmds": self._conf2cmds}
