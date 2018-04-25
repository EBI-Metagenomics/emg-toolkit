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
    usage: mg-toolkit [-h] [-V] [-d] -a ACCESSION [ACCESSION ...]
                      {original_metadata}

Example::

    $ mg-toolkit original_metadata -a ERP001736
