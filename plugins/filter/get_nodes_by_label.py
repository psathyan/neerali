# -*- code: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
    name: get_nodes_by_label
    short_description: Get nodes by label.
    description:
      - Returns a list of nodes having the specified label.
    positional: _input
    options:
      _input:
        description:
          - list of systems under test
        type: list
        elements: dict
        required: true
      label:
        description:
          - The label to be used for filtering the nodes
        type: str
        required: true
      cluster:
        description:
          - The Ceph cluster name to refer
        type: str
        required: true
"""


EXAMPLES = """
    # This is an example of using get_nodes_by_label filter plugin.
    _osd_nodes: >-
      {{
        neerali_systems_provisioned |
        get_nodes_by_label(label='osd', cluster=neerali_cluster_name)
      }}
"""


RETURN = """
    _value:
      description: The list of nodes having the specified label.
      type: list
      elements: str
"""


from ansible.errors import AnsibleFilterTypeError


class FilterModule:
    """Custom filter module class."""

    @classmethod
    def _get_nodes(cls, nodes, label, cluster):
        """Returns a list of nodes filtered by cluster and label."""
        if not isinstance(nodes, list):
            raise AnsibleFilterTypeError(
                f"get_nodes_by_labe requires a list, got {type(nodes)}"
            )

        _results = []
        for _node in nodes:
            if label in _node["roles"] and _node.get("cluster", "ceph") == cluster:
                _results.append(_node["name"])

        return _results

    def filters(self):
        return {"get_nodes_by_label": self._get_nodes}
