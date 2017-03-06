#!/usr/bin/env python

import unittest

from setuptools import setup

def suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='*_test.py')
    return test_suite

setup(
    pbr=True,
    test_suite='setup.suite',
    tests_require=['mock'],
    setup_requires=['pbr>=1.9', 'setuptools>=17.1']
)
