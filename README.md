[![Build Status](https://travis-ci.org/EBI-Metagenomics/emg-toolkit.svg?branch=master)](https://travis-ci.org/EBI-Metagenomics/emg-toolkit) [![PyPi package](https://badge.fury.io/py/mg-toolkit.svg)](https://badge.fury.io/py/mg-toolkit) [![Downloads](http://pepy.tech/badge/mg-toolkit)](http://pepy.tech/project/mg-toolkit)


Metagenomics toolkit enables scientists to download all of the sample
metadata for a given study or sequence to a single csv file.


Install metagenomics toolkit
============================

    pip install -U mg-toolkit


Usage
=====

    $ mg-toolkit -h
    usage: mg-toolkit [-h] [-V] [-d] {original_metadata,sequence_search} ...

    Metagenomics toolkit
    --------------------

    positional arguments:
      {original_metadata,sequence_search}
        original_metadata   Download original metadata
        sequence_search     Search non-redundant protein database using HMMER

    optional arguments:
      -h, --help            show this help message and exit
      -V, --version         print version information
      -d, --debug           print debugging information


Examples
========

Download metadata::

    $ mg-toolkit original_metadata -a ERP001736


Search non-redundant protein database using HMMER and fetch metadata

    $ mg-toolkit sequence_search -seq test.fasta -db full

    Databases:
    - full - Full length sequences (default)
    - all - All sequences
    - partial - Partial sequences
