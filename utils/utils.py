"""Module contains use workflows for the core package."""
from pathlib import Path
from typing import Dict, Optional


def create_run_dir(run_id: str, log_dir="/tmp") -> str:
    """
    Create the root logging folder for the run.

    Args:
        run_id: id of the test run. used to name the directory
        log_dir: log directory. default: "/tmp"

    Returns:
        Full path of the created directory
    """
    msg = """\nNote :
    1. Custom log directory will be disabled if '/ceph/cephci-jenkins' exists.
    2. If custom log directory not specified, then '/tmp' directory is considered .
    """
    print(msg)

    root_log_dir = Path("/ceph/cephci-jenkins")

    if not root_log_dir.exists():
        root_log_dir = Path("/tmp")

    dir_name = f"cephci-run-{run_id}"
    base_dir = "/ceph/cephci-jenkins"

    if

    if not os.path.isdir(base_dir):
        if not os.path.isabs(log_dir):
            log_dir = os.path.join(os.getcwd(), log_dir)
        base_dir = log_dir
    run_dir = os.path.join(base_dir, dir_name)
    try:
        os.makedirs(run_dir)
    except OSError:
        if "jenkins" in getpass.getuser():
            raise

    return run_dir


def merge_dicts(source: Dict, target: Dict) -> None:
    """
    Return a merged dictionary.

    This method allows us to consider nested dictionaries so that all values are
    considered instead of second one alone

    Args:
        source (dict)    Dictionary that needs to be merged
        target (dict)    Dictionary that needs to contain the source

    Returns:
        None
    """
    for key, value in source.items():
        if key in target.keys():
            target[key].update(value)
            continue

        target.update({key: value})
