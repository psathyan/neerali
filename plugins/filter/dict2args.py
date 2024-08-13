# -*- code: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
    name: dict2args
    short_description: Convert a dictionary into cli arguments.
    positional: _input
    options:
      _input:
        description: Dictionary to be converted to CLI arguments
        type: dictionary
        required: true
"""


EXAMPLES = """
    # This example uses dict2args
    _args: "{{ argumets | neerali.general.dict2args }}"

    # Returns a string that can be passed to the command line
"""


RETURN = """
    _value:
      description: The CLI arguments as a string.
      type: str
"""


from ansible.errors import AnsibleFilterError


class FilterModule:
    """Filter module class."""

    @classmethod
    def _dict_to_string(cls, data):
        """Return a string containing CLI arguments."""
        if not isinstance(data, dict):
            raise AnsibleFilterError(f"dict2args requires a dict, got {type(data)}")

        _result = ""
        for _key, _value in data.items():
            if (isinstance(_value, bool) and not _value) or (
                isinstance(_value, str) and _value.lower in ["false", "no"]
            ):
                continue

            # Currently, we are ignoring key having None value.
            if _value is None:
                continue

            _result += f" -{_key}" if len(_key) == 1 else f" --{_key}"

            if (
                isinstance(_value, str) and _value.lower in ["true", "yes"]
            ) or isinstance(_value, bool):
                continue

            if isinstance(_value, list):
                # A space to separate option and value
                _result += " "
                _result += ",".join([f" {_item}" for _item in _value])

            if isinstance(_value, dict):
                raise AnsibleFilterError("Unexpected dict as value.")

            _result += f" {_value}"

        return _result

    def filters(self):
        return {"dict2args": self._dict_to_string}
