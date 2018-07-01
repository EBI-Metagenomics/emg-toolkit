.. image:: https://travis-ci.org/EBI-Metagenomics/emg-toolkit.svg?branch=master
    :target: https://travis-ci.org/EBI-Metagenomics/emg-toolkit

.. image:: https://badge.fury.io/py/mg-toolkit.svg
    :target: https://badge.fury.io/py/mg-toolkit



Metagenomics toolkit enables scientists to download all of the sample metadata for a given study to a single csv file.


Install metagenomics toolkit
============================

::

    pip install mg-toolkit


Usage
=====

::

    $ mg-toolkit -h
    usage: mg-toolkit [-h] [-V] [-d] {original_metadata,sequence_search} ...

    Metagenomics toolkit
    --------------------

    positional arguments:
      {original_metadata,sequence_search}
        original_metadata   Download original metadata
        sequence_search     Search sequence

    optional arguments:
      -h, --help            show this help message and exit
      -V, --version         print version information
      -d, --debug           print debugging information

Example::

    $ mg-toolkit original_metadata -a ERP001736

or::

    $ mg-toolkit sequence_search -s test.fasta
