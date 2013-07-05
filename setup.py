#!/usr/bin/env python

from setuptools import setup

setup(
    name = "freeradius_samlldap",
    version = "0.0.1",
    description = "Testing rlm_python / rlm_exec Freeradius modules",
    author = "Vincent Giersch",
    author_email = "vg66@kent.ac.uk",
    py_modules = [
        'freeradius_samlldap',
        'radiusd'
    ],
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        ],
    data_files=[('attributemaps',
                            ['attributemaps/basic.py',
                             'attributemaps/saml_uri.py',
                             'attributemaps/shibboleth_uri.py'])]
)
