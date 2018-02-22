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

setup(
    name="emg_toolkit",
    packages=find_packages(exclude=['ez_setup']),
    version="0.1.0",
    install_requires=install_requirements,
    setup_requires=['pytest-runner'],
    tests_require=test_requirements,
    include_package_data=True,
    zip_safe=False,
    license='Apache Software License',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    test_suite="tests",
    entry_points={
        'console_scripts': [
            'emg-toolkit=emg_toolkit.__main__:main',
        ],
    },
)
