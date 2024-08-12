# -*- code: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
    name: get_admin_nodes
    short_description: A comma seperated list of hosts with _admin label.
    description:
      - A string of comma seperated hosts with '_admin' label.
      - Unique to a given cluster.
    positional: _input
    options:
      _input:
        description:
          - list of systems under test
        type: list
        elements: dict
        required: true
"""


EXAMPLES = """
    # This example uses get_admin_nodes
    _targets: "{{ neerali_systems_layout.baremetal | get_admin_nodes }}"
"""


RETURN = """
    _value:
      description: The list of strings that can be passed to ceph role.
      type: str
"""


from ansible.errors import AnsibleFilterTypeError


class FilterModule:
    """Filter module class."""

    @classmethod
    def _get_admin_labelled_nodes(cls, data):
        """Returns a string having comma seperate hosts."""
        if not isinstance(data, list):
            raise AnsibleFilterTypeError(
                f"get_admin_nodes requires a list, got {type(data)}"
            )

        _results = []
        _clusters = []
        for _node in data:
            if "_admin" not in _node["roles"]:
                continue

            if _node.get("cluster", "ceph") in _clusters:
                continue

            _results.append(_node["name"])
            _clusters.append(_node.get("cluster", "ceph"))

        return ",".join(_results)

    def filters(self):
        return {"get_admin_nodes": self._get_admin_labelled_nodes}
