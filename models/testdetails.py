# -*- coding: utf-8 -*-
"""Provides a structure containing information about the test case."""
TEST_MGR_ENDPOINT = "https://polarion.engineering.redhat.com/polarion"
TESTCASE_BASE_URI = f"{TEST_MGR_ENDPOINT}/#/project/CEPH/workitem?id="


class TestCaseMeta:
    """Structure that holds the metadata information of a CephCI test case."""

    def __init__(self, testcase: dict) -> None:
        """
        Initialize the structure.

        Args:
            testcase (dict):    Test case details and configuration as provided in the
                                suite file. The following keys are processed
                                - name
                                - desc
                                - module
                                - polarion-id
                                - comments
        Returns:
            None
        """
        self.name = testcase["name"]
        self.description = testcase["desc"]
        self.module = testcase["module"]

        if testcase.get("polarion-id"):
            self.polarion_id = f"{TESTCASE_BASE_URI}{testcase['polarion-id']}"
        else:
            self.polarion_id = None

        self.comments = testcase.get("comments")

        # Runtime assignments
        self.status = None
        self.start_time = None
        self.end_time = None
        self.extra = {}  # Data to be pushed to Report Portal

    @property
    def duration(self) -> int:
        """Return the time taken to execute the test."""
        return (self.end_time - self.start_time).total_seconds()
