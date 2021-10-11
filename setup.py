# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

setup(
    name="cephci",
    version="0.2",
    description="Red Hat Ceph Storage QE CI utility.",
    author="Ceph-QE",
    author_email="cephci@redhat.com",
    install_requires=[
        "apache-libcloud",
        "docopt",
        "gevent",
        "greenlet",
        "htmllistparse",
        "ibm-cloud-networking-services",
        "ibm-cos-sdk",
        "ibm-cos-sdk-core",
        "ibm-cos-sdk-s3transfer",
        "ibm-vpc",
        "jinja2",
        "jinja_markdown",
        "junitparser",
        "paramiko",
        "pyOpenSSL",
        "pyyaml",
        "python-logstash",
        "reportportal-client",
        "requests",
    ],
    zip_safe=True,
    include_package_data=True,
    packages=find_packages(exclude=["ez_setup"]),
)
