"""Entry point for Red Hat Ceph QE CI."""
import logging
import sys
from pathlib import Path
from typing import Dict

import yaml
from docopt import docopt

from utils.log import (
    LOG_FORMAT,
    add_log_file_handler,
    close_log_handlers,
    create_or_get_root_log_dir,
)
from utils.utils import generate_unique_id, merge_dicts

usage = """
An orchestrator that calls the relevant methods based on the provided workflow.

Usage:
  run.py -h | --help 
  run.py (--conf <conf-file>)...
    [--rhcs <rhcs-version>]
    [--build <build-type>]
    [--clusters-spec <cluster-spec>]
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
  --clusters-spec <cluster-spec>    System Under Test layout file
  --test-suite <test-suite>         Absolute test suite file. Supports multiple values
  --verbose                         Increases the log level. Default, log level is info
"""
LOG = logging.getLogger(__name__)
logging.basicConfig(
    handlers=[logging.StreamHandler(sys.stdout)], level=logging.DEBUG, format=LOG_FORMAT
)


def run(conf: Dict, cli_args: Dict) -> None:
    """
    Wrapper method that triggers the workflows based on the provided arguments.

    Args:
        conf (dict):        Single configuration dictionary passed to the module.
        cli_args (dict)     CLI arguments passed to run.py. Refer cepchi.yaml.template
                            for supported key-value pairs
    Returns:
        None
    Raises:
        Exception
    """
    # Always check if the operation is cleanup first before proceeding with workflow
    if cli_args.get("--cleanup"):
        # cleanup_ceph_nodes(configs["compute"]["credential"], cli_args["--cleanup"])
        print("Nothing to do")
        return

    # CLI args must have the highest precedence
    if cli_args["--rhcs"]:
        conf["rhcs"] = cli_args["--rhcs"]

    if cli_args["--build"]:
        conf["build"] = cli_args["--build"]

    if cli_args["--clusters-spec"]:
        conf["compute"]["spec"] = cli_args["--clusters-spec"]

    if cli_args["--test-suite"]:
        conf["test_suites"] = cli_args["--test-suite"]


if __name__ == "__main__":
    args = docopt(usage)
    try:
        # run_id is a unique identifier for the execution run
        run_id = generate_unique_id(length=6)

        # Read test configuration and CLI arguments
        configs = dict()

        for file_ in args["--conf"]:
            file_ = Path(file_).absolute()
            with file_.open("r") as fh:
                config = yaml.safe_load(fh)
                merge_dicts(config, configs)

        # Initiate the loggers
        msg = """
        Note :
            By default, the logging directory is '/ceph/cephci-jenkins' if it exists.
            Otherwise, it is '/tmp' on the local system.
        """
        print(msg)

        log_level = logging.DEBUG if args.get("--verbose") else logging.INFO
        create_or_get_root_log_dir(run_id, config.get("log", {}).get("path"))
        add_log_file_handler(run_id, "startup.log", log_level)

        LOG.info("Testing from info level")
        LOG.debug("Testing from debug level")

        LOG.debug(args)
        run(configs, args)
    except BaseException as be:  # no-qa
        LOG.error(be)
        sys.exit(1)
    finally:
        close_log_handlers()
