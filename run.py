"""Entry point for Red Hat Ceph QE CI."""
import logging
import sys
import yaml
from docopt import docopt
from pathlib import Path
from typing import Dict

from ceph.utils import cleanup_ceph_nodes
from utility.utils import generate_unique_id, add_log_file_handler, merge_dicts

usage = """
An orchestrator that calls the relevant methods based on the provided workflow.

Usage:
  run.py -h | --help
  run.py --cleanup <instance-prefix> (--conf <conf-file)... [--verbose]
  run.py (--conf <conf-file>)...
    [--rhcs <rhcs-version>]
    [--build <build-type>]
    [--clusters-spec <cluster-spec>]
    [--test-suite <test-suite>]...
    [--verbose]

Options:
  -h --help                         Displays the usage and supported options.
  --cleanup <instance-prefix>       Runs the VM environment cleanup.
  --conf <rhcs-version>             Configuration files in YAML format containing
                                    details for execution.
  --rhcs <rhcs-version>             Red Hat Ceph Storage version
  --build <build-type>              Type of build to be used for deployment. Default the
                                    latest CDN bits
  --clusters-spec <cluster-spec>    System Under Test layout file
  --test-suite <test-suite>         Absolute test suite file. Supports multiple values
  --verbose                         Increases the log level. Default, log level is info
"""

# Configuring the logging options
LOG = logging.getLogger(__name__)
logging.basicConfig(
    handlers=[logging.StreamHandler(sys.stdout)],
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)


def run(cli_args: Dict) -> None:
    """
    Wrapper method that triggers the workflows based on the provided arguments.

    Args:
        cli_args (Dict)     CLI arguments passed to run.py. Refer cepchi.yaml.template
                            for supported key-value pairs
    Returns:
        None
    Raises:
        Exception
    """
    # run_id is a unique identifier for the execution run
    run_id = generate_unique_id(length=6)

    log_level = logging.INFO
    if cli_args.get("--verbose"):
        LOG.setLevel(logging.DEBUG)
        log_level = logging.DEBUG
        LOG.debug("Log level now is at DEBUG.")

    add_log_file_handler(run_id, "startup.log", log_level)

    # Read test configuration and CLI arguments
    configs = dict()

    for file_ in cli_args["--conf"]:
        file_ = Path(file_).absolute()
        with file_.open('r') as fh:
            config = yaml.safe_load(fh)
            merge_dicts(config, configs)

    # Always check if the operation is cleanup first before proceeding with workflow
    if cli_args.get("--cleanup"):
        cleanup_ceph_nodes(configs["compute"]["credential"], cli_args["--cleanup"])
        return

    # CLI args must have the highest precedence
    if cli_args["--rhcs"]:
        configs["rhcs"] = cli_args["--rhcs"]

    if cli_args["--build"]:
        configs["build"] = cli_args["--build"]

    if cli_args["--clusters-spec"]:
        configs["compute"]["spec"] = cli_args["--clusters-spec"]

    if cli_args["--test-suite"]:
        configs["test_suites"] = cli_args["--test-suite"]


if __name__ == "__main__":
    args = docopt(usage)
    try:
        LOG.debug(args)
        run(args)
    except BaseException as be:  # no-qa
        LOG.error(be)
        sys.exit(1)
