# -*- coding: utf-8 -*-
"""Provides methods for logging to a given report portal instance."""
import traceback
from pathlib import Path
from time import time

from reportportal_client import ReportPortalServiceAsync

from .config import CephCIConfig
from .log import Log

from models.testdetails import TestCaseMeta

log = Log()


def timestamp() -> str:
    """Serialize the time."""
    return str(int(time() * 1000))


def error_handler(exc_info) -> None:
    """Error handler for Report Portal."""
    print(f"ERROR: {exc_info[1]}")
    traceback.print_exception(*exc_info)


class RPLogger:
    """Report Portal logger object."""

    def __init__(self) -> None:
        """Initializes the object using CephCI global conf file."""
        self.conf = CephCIConfig()

        if not self.conf.get("report-portal"):
            self.client = None
            return

        self.client = ReportPortalServiceAsync(
            endpoint=self.conf["report-portal"]["endpoint"],
            project=self.conf["report-portal"]["project"],
            token=self.conf["report-portal"]["token"],
            error_handler=error_handler,
        )

    def start_launch(self, suite_name: str) -> None:
        """
        Creates a test suite entry in the report portal.

        Args:
            suite_name (str):   Test suite that is executed.
        Returns:
            None
        """
        launch_name = Path(suite_name).name
        ceph_version = self.conf["versions"].get("ceph-version")

        if not ceph_version:
            # Only development builds would have ceph-version populated via recipe file.
            ceph_version = f"{self.conf['rhcs']} released"

        tags = ["cephci", self.conf["rhcs"]]

        if launch_name.startswith("tier"):
            # Launch name could be tier_0_rgw
            content = launch_name.split("_")
            tier_level = "-".join(content[:2])
            component = content[2]

            tags += [content, tier_level, component]

        description = f"{launch_name}_{ceph_version}"
        self.client.start_launch(
            name=launch_name,
            start_time=timestamp(),
            description=description,
            tags=["cephci"],
        )

    def finish_launch(self, status="PASSED") -> None:
        """Closes the launch session."""
        self.client.finish_launch(end_time=timestamp(), status=status)

    def start_test_step(self, name, testcase: TestCaseMeta) -> None:
        """
        Logs a test setup with the metadata information.

        Args:
            name (str):                 Unique name of the test step.
            testcase (TestCaseMeta):    Test case metadata information

        Returns:
            None
        """
        params = testcase.extra
        self.client.start_test_item(
            name=name,
            description=testcase.description,
            start_time=timestamp(),
            item_type="STEP",
            parameters=params,
        )

    def finish_test_step(self, testcase: TestCaseMeta) -> None:
        """Stop the test step logging with the provided status."""
        status = testcase.status
        issues = testcase.extra.get("issues")
        self.client.finish_test_item(end_time=timestamp(), status=status, issue=issues)
