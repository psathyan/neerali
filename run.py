"""Entry point for Red Hat Ceph QE CI."""
import logging
import sys
from pathlib import Path
from typing import Dict, Optional

import yaml
from docopt import docopt

from utils.log import LOG_FORMAT, Log
from utils.utils import generate_unique_id, merge_dicts

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
    handlers=[logging.StreamHandler(sys.stdout)], level=logging.DEBUG, format=LOG_FORMAT
)


def run(conf: Dict, cleanup: Optional[bool] = None) -> None:
    """
    Wrapper method that triggers the workflows based on the provided arguments.

    Args:
        conf (dict):        Single configuration dictionary passed to the module.
        cleanup (bool):     Is enabled only if instances is to be cleaned up.
    Returns:
        None
    Raises:
        Exception
    """
    # Always check if the operation is cleanup first before proceeding with workflow
    # cleanup_nodes(conf)
    if cleanup:
        return

    LOG.info("Successfully completed the execution")


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

        # CLI args must have the highest precedence
        if args["--rhcs"]:
            configs["rhcs"] = args["--rhcs"]

        if args["--build"]:
            configs["build"] = args["--build"]

        if args["--vm-spec"]:
            configs["compute"]["spec"] = args["--vm-spec"]

        if args["--test-suite"]:
            configs["test_suites"] = args["--test-suite"]

        # Initiate the loggers
        msg = """
        Note :
            By default, the logging directory is '/ceph/cephci-jenkins' if it exists.
            Otherwise, it is '/tmp' on the local system.
        """
        print(msg)

        LOG = Log(run_id=run_id, config=configs, verbose=args.get("--verbose"))
        LOG.add_file_handler("startup.log")

        run(configs, args.get("--cleanup"))
        LOG.debug(args)
    except BaseException as be:  # no-qa
        LOG.error(be)
        sys.exit(1)
    finally:
        LOG.close()
