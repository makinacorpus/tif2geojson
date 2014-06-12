#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='tif2geojson',
    version='0.1.2',
    description='Converts TourInFrance XML format to GeoJSON',
    long_description=readme + '\n\n' + history,
    author='Makina Corpus',
    author_email='mathieu.leplatre@makina-corpus.com',
    url='https://github.com/makinacorpus/tif2geojson',
    scripts=[
        'tif2geojson.py'
    ],
    py_modules=['tif2geojson'],
    include_package_data=True,
    install_requires=[
        'geojson',
        'xmltodict',
    ],
    license="BSD",
    zip_safe=False,
    keywords='tif2geojson',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',
)
