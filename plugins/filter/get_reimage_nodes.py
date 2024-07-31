# -*- code: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
    name: get_reimage_nodes
    short_description: Return a list of nodes that should be reimaged.
    description:
      - Return a list of nodes that should be reimaged with teuthology.
      - This filter functions as extracter of the node names from the input.
    positional: _input
    options:
      _input:
        description:
          - list of physical systems that can be reimage using teuthology.
        type: list
        elements: str
        required: true
"""

EXAMPLES = """
    # This example uses the 'get_reimage_nodes' filter in conjunction
    _list: "{{ neerali_systems_layout.baremetal | get_reimage_nodes }}"
"""


RETURN = """
    _value:
      description: The list of strings that can be passed to 
                   teuthology-reimage command.
      type: list
      elements: str
"""


from ansible.errors import AnsibleFilterTypeError


class FilterModule:
    """Filter module class"""

    @classmethod
    def _get_cmd_options(cls, data):
        """Returns a list of strings to be passed to teuthology-reimage."""
        if not isinstance(data, list):
            raise AnsibleFilterTypeError(
                f"get_reimage_nodes requires list, got {type(data)}"
            )

        _node_map = dict()
        for _node in data:
            _os_family = _node["os"]["type"]
            _os_version = _node["os"]["version"]

            if _os_family not in _node_map:
                _node_map[_os_family] = dict()

            if _os_version not in _node_map[_os_family]:
                _node_map[_os_family][_os_version] = list()

            _node_map[_os_family][_os_version].append(_node["name"])

        _results = list()
        for _os in _node_map:
            for _ver in _node_map[_os]:
                _nodes = " ".join(_node_map[_os][_ver])
                _results.append(f"--os-type {_os} --os-version {_ver} {_nodes}")

        return _results

    def filters(self):
        return {"get_reimage_nodes": self._get_cmd_options}
