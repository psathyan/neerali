# -*- coding: utf-8 -*-
"""Entry point for Red Hat Ceph QE CI."""
import logging
import sys

from docopt import docopt

from utils.compute import delete_vms, delete_volumes
from utils.config import CephCIConfig
from utils.log import LOG_FORMAT, Log
from utils.utils import generate_unique_id, merge_dicts, yaml_to_dict

usage = """
An orchestrator that calls the relevant methods based on the provided workflow.

Usage:
  run.py -h | --help 
  run.py (--conf <conf-file>)...
    [--rhcs <rhcs-version>]
    [--build <build-type>]
    [--vm-spec <vm-spec>]
    [--test-suite <test-suite>]...
    [--verbose]
    [--cleanup <instances-prefix>]

Options:
  -h --help                         Displays the usage and supported options.
  --cleanup <instances-prefix>      Runs the VM environment cleanup.
  --conf <rhcs-version>             Configuration files in YAML format containing
                                    details for execution.
  --rhcs <rhcs-version>             Red Hat Ceph Storage version
  --build <build-type>              Type of build to be used for deployment. Default the
                                    latest CDN bits
  --vm-spec <vm-spec>               System Under Test layout file
  --test-suite <test-suite>         Absolute test suite file. Supports multiple values
  --verbose                         Increases the log level. Default, log level is info
"""
LOG = logging.getLogger(__name__)
logging.basicConfig(
    handlers=[logging.StreamHandler(sys.stdout)], level=logging.INFO, format=LOG_FORMAT
)


def run(conf: CephCIConfig) -> None:
    """
    Wrapper method that triggers the workflows based on the provided arguments.

    This method uses the CephCIConf variable to read the configuration passed to the
    scripts by the user. Refer the cephci.yaml.template for supported keys and sections.

    Args:
        conf (CephCIConfig):    test configurations passed by the user

    Returns:
        None

    Raises:
        Exception
    """
    # Always check if the operation is cleanup first before proceeding with workflow
    if conf.get("cleanup"):
        delete_vms(conf["cleanup"])
        delete_volumes(conf["cleanup"])
        return

    delete_vms()

    LOG.info("Successfully completed the execution")


if __name__ == "__main__":
    args = docopt(usage)
    try:
        # run_id is a unique identifier for the execution run
        run_id = generate_unique_id(length=6)

        # Read test configuration and CLI arguments
        configs = dict({"run_id": run_id})

        for file_ in args["--conf"]:
            config = yaml_to_dict(file_)
            merge_dicts(config, configs)

        # CLI args must have the highest precedence
        if args["--rhcs"]:
            configs["rhcs"] = args["--rhcs"]

        if args["--build"]:
            configs["build"] = args["--build"]

        if args["--vm-spec"]:
            configs["compute"]["spec"] = args["--vm-spec"]

        if args["--test-suite"]:
            configs["test_suites"] = args["--test-suite"]

        if args["--cleanup"]:
            configs["cleanup"] = args["--cleanup"]

        if args["--verbose"]:
            if "log" in configs.keys():
                configs["log"]["verbose"] = True
            else:
                configs["log"] = dict({"verbose": True})

        cephci_conf = CephCIConfig(configs)

        # Initiate the loggers
        msg = """
        Note :
            By default, the logging directory is '/ceph/cephci-jenkins' if it exists.
            Otherwise, it is '/tmp' on the local system.
        """
        print(msg)

        # Perform the log initializers
        LOG = Log()
        LOG.create_root_folder()
        LOG.add_file_handler("startup.log")

        run(cephci_conf)

    except BaseException as be:  # no-qa
        LOG.exception(be)
        sys.exit(1)
    finally:
        LOG.close()
