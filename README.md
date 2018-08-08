[![Build Status](https://travis-ci.org/EBI-Metagenomics/emg-toolkit.svg?branch=master)](https://travis-ci.org/EBI-Metagenomics/emg-toolkit) [![PyPi package](https://badge.fury.io/py/mg-toolkit.svg)](https://badge.fury.io/py/mg-toolkit) [![Downloads](http://pepy.tech/badge/mg-toolkit)](http://pepy.tech/project/mg-toolkit)


Metagenomics toolkit enables scientists to download all of the sample
metadata for a given study or sequence to a single csv file.


Install metagenomics toolkit
============================

    pip install -U mg-toolkit


Usage
=====

    $ mg-toolkit -h
    usage: mg-toolkit [-h] [-V] [-d]
                      {original_metadata,sequence_search,bulk_download} ...

    Metagenomics toolkit
    --------------------

    positional arguments:
      {original_metadata,sequence_search,bulk_download}
        original_metadata   Download original metadata.
        sequence_search     Search non-redundant protein database using HMMER
        bulk_download       Download result files in bulks for an entire study.

    optional arguments:
      -h, --help            show this help message and exit
      -V, --version         print version information
      -d, --debug           print debugging information


Examples
========

Download metadata:

    $ mg-toolkit original_metadata -a ERP001736


Search non-redundant protein database using HMMER and fetch metadata:

    $ mg-toolkit sequence_search -seq test.fasta -db full evalue --incE 0.02

    Databases:
    - full - Full length sequences (default)
    - all - All sequences
    - partial - Partial sequences


How to bulk download result files for an entire study?

    $ mg-toolkit bulk_download -h
    usage: mg-toolkit bulk_download [-h] -a ACCESSION [-o OUTPUT_PATH]
                                      [-v {1.0,2.0,3.0,4.0,4.1}]
                                      [-g {sequence_data,functional_analysis,taxonomic_analysis,taxonomic_analysis_ssu,taxonomic_analysis_lsu,stats,non_coding_rna}]
      
    optional arguments:
      -h, --help            show this help message and exit
      -a ACCESSION, --accession ACCESSION
                            Provide the study/project accession of your interest,
                            e.g. ERP001736, SRP000319. The study must be publicly
                            available in MGnify.
      -o OUTPUT_PATH, --output_path OUTPUT_PATH
                            Location of the output directory, where the
                            downloadable files are written to. DEFAULT: CWD
      -v {1.0,2.0,3.0,4.0,4.1}, --version {1.0,2.0,3.0,4.0,4.1}
                            Specify the version of the pipeline you are interested
                            in. Lets say your study of interest has been analysed
                            with multiple version, but you are only interested in
                            a particular version then used this option to filter
                            down the results by the version you interested in.
                            DEFAULT: Downloads all versions
      -g {sequence_data,functional_annotations,taxonomic_annotations,taxonomic_annot_ssu,taxonomic_annot_lsu,stats,non_coding_rna}, --result_group {sequence_data,functional_annotations,taxonomic_annotations,taxonomic_annot_ssu,taxonomic_annot_lsu,stats,non_coding_rna}
                            Provide a single result group if needed. Supported
                            result groups are: [sequence_data (all version),
                            functional_annotations (all version),
                            taxonomic_annotations (1.0-3.0), taxonomic_annot_ssu
                            (>=4.0), taxonomic_annot_lsu (>=4.0), stats,
                            non_coding_rna (>=4.0) DEFAULT: Downloads all result
                            groups if not provided. (default: None).
    
How to download all files for a given study accession?
    
    $ mg-toolkit -d bulk_download -a ERP009703
    
How to download results of a specific version for given study accession?
    
    $ mg-toolkit -d bulk_download -a ERP009703 -v 4.0
    
How to download specific result file groups (e.g. functional annotations only) for given study accession?
    
    $ mg-toolkit -d bulk_download -a ERP009703 -g functional_annotations