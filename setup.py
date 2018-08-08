#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2018 EMBL - European Bioinformatics Institute
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import os

from setuptools import setup, find_packages

_base = os.path.dirname(os.path.abspath(__file__))
_requirements = os.path.join(_base, 'requirements.txt')
_requirements_test = os.path.join(_base, 'requirements-test.txt')

install_requirements = []
with open(_requirements) as f:
    install_requirements = f.read().splitlines()

test_requirements = []
if "test" in sys.argv:
    with open(_requirements_test) as f:
        test_requirements = f.read().splitlines()

long_description = ""
with open(os.path.join(_base, 'README.md'), 'rb') as f:
    long_description = f.read().decode('utf-8')

setup(
    name="mg-toolkit",
    url='https://github.com/EBI-metagenomics/emg-toolkit',
    author='Ola Tarkowska',
    author_email='olat@ebi.ac.uk',
    description='Metagenomics toolkit',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=['ez_setup']),
    version="0.6.1",
    python_requires=">=3.4",
    install_requires=install_requirements,
    setup_requires=['pytest-runner'],
    tests_require=test_requirements,
    include_package_data=True,
    zip_safe=False,
    license='Apache Software License',
    classifiers=[
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    test_suite="tests",
    entry_points={
        'console_scripts': [
            'mg-toolkit=mg_toolkit:main',
        ],
    },
)
