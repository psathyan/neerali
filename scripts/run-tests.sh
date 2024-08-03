#!/bin/bash
set -euxo pipefail

project_dir="$(dirname $(readlink -f ${BASH_SOURCE[0]}))/../"
_test_exe=${TEST_EXEC:-'ansible-test'}
_suite=${TEST_SUITE:-'integration'}

# linters
ansible-lint -s
black --check --diff .

# Check and create molecule image
_image_c=$(podman image ls --format {{.Names}} | grep -c neerali-molecule) || true
if [ ${_image_c} -eq 0 ]; then
    pushd ${project_dir}/ci/molecule
    podman image build \
        --tag neerali-molecule \
        --force-rm \
        --squash \
        --no-cache \
        .
    popd
fi

echo "Begin test execution"
podman run --name unit-test --rm \
    --volume ${project_dir}:/home/ciuser/neerali:ro \
    localhost/neerali-molecule  ${_test_exe} ${_suite}
