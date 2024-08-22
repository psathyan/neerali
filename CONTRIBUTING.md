# Contribute to neerali

Thank you for your interest in the project and for taking the time to support.

## Create a new role

Run the following command to get a new role

```Bash
[dev]$ make create-update-role ROLE_NAME=an_example
```

### Documentation

Proper documentation of the new role is required. This can be done by modifying
the README.md located in the role directory. Ensure the following

- Overview
- Parameters
- Usage with examples

### Testing

A new role must have unit tests. Primarily, molecule is used for unit testing
of the roles in the framework. Unit testing is initiated by executing

```Bash
[dev]$ make unit-test TEST_EXEC=molecule TEST_SUITE=an_example
```

Testing is done using an image built from centos:stream-9 container. Hence, we
require podman to be installed on the development system.

### Exceptions

We understand some roles cannot be unit tested due to dependency issues. It is
acceptable for those roles not have unit test scenarios.

## Adding new plugins

`neerali` is a collection hence support exists for adding custom plugins if
required. New modules must be added under `plugins/` directory.

### Plugin documentation

Unlike roles, custom plugin documentation exists in `plugins/README.md`. Ensure
proper documentation is added for the custom plugin with examples.

### Testing

Tests for the custom plugin must be added under the `tests/` directory. It is
highly recommended to cover both negative and postive use cases. The tests can
be run using the below command

```Bash
[dev]$ make unit-test TEST_EXEC=ansible-test TEST_SUITE=integration
```
