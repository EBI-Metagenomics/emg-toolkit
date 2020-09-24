[![Build Status](https://travis-ci.com/EBI-Metagenomics/emg-toolkit.svg?branch=master)](https://travis-ci.com/EBI-Metagenomics/emg-toolkit) [![PyPi package](https://badge.fury.io/py/mg-toolkit.svg)](https://badge.fury.io/py/mg-toolkit) [![Downloads](http://pepy.tech/badge/mg-toolkit)](http://pepy.tech/project/mg-toolkit)


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

    $ mg-toolkit sequence_search -seq test.fasta -db full evalue -incE 0.02

    Databases:
    - full - Full length sequences (default)
    - all - All sequences
    - partial - Partial sequences


How to bulk download result files for an entire study?

    usage: mg-toolkit bulk_download [-h] -a ACCESSION [-o OUTPUT_PATH]
                                    [-p {1.0,2.0,3.0,4.0,4.1,5.0}]
                                    [-g {statistics,sequence_data,functional_analysis,taxonomic_analysis,taxonomic_analysis_ssu_rrna,taxonomic_analysis_lsu_rrna,non-coding_rnas,taxonomic_analysis_itsonedb,taxonomic_analysis_unite,taxonomic_analysis_motupathways_and_systems}]

    optional arguments:
    -h, --help            show this help message and exit
    -a ACCESSION, --accession ACCESSION
                            Provide the study/project accession of your interest, e.g. ERP001736, SRP000319. The study must be publicly available in MGnify.
    -o OUTPUT_PATH, --output_path OUTPUT_PATH
                            Location of the output directory, where the downloadable files are written to.
                            DEFAULT: CWD
    -p {1.0,2.0,3.0,4.0,4.1,5.0}, --pipeline {1.0,2.0,3.0,4.0,4.1,5.0}
                            Specify the version of the pipeline you are interested in.
                            Lets say your study of interest has been analysed with
                            multiple version, but you are only interested in a particular
                            version then used this option to filter down the results by
                            the version you interested in.
                            DEFAULT: Downloads all versions
    -g {statistics,sequence_data,functional_analysis,taxonomic_analysis,taxonomic_analysis_ssu_rrna,taxonomic_analysis_lsu_rrna,non-coding_rnas,taxonomic_analysis_itsonedb,taxonomic_analysis_unite,taxonomic_analysis_motupathways_and_systems}, --result_group {statistics,sequence_data,functional_analysis,taxonomic_analysis,taxonomic_analysis_ssu_rrna,taxonomic_analysis_lsu_rrna,non-coding_rnas,taxonomic_analysis_itsonedb,taxonomic_analysis_unite,taxonomic_analysis_motupathways_and_systems}
                            Provide a single result group if needed.
                            Supported result groups are:
                            - statistics
                            - sequence_data (all versions)
                            - functional_analysis (all versions)
                            - taxonomic_analysis (1.0-3.0)
                            - taxonomic_analysis_ssu_rrna (>=4.0)
                            - taxonomic_analysis_lsu_rrna (>=4.0)
                            - non-coding_rnas (>=4.0)
                            - taxonomic_analysis_itsonedb (>= 5.0)
                            - taxonomic_analysis_unite (>= 5.0)
                            - taxonomic_analysis_motu  (>= 5.0)
                            - pathways_and_systems (>= 5.0)
                            DEFAULT: Downloads all result groups if not provided.
                            (default: None).


How to download all files for a given study accession?

    $ mg-toolkit -d bulk_download -a ERP009703

How to download results of a specific version for given study accession?

    $ mg-toolkit -d bulk_download -a ERP009703 -v 4.0

How to download specific result file groups (e.g. functional analysis only) for given study accession?

    $ mg-toolkit -d bulk_download -a ERP009703 -g functional_analysis


Contributors
============

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://github.com/olatarkowska"><img src="https://avatars3.githubusercontent.com/u/1065155?v=4" width="100px;" alt=""/><br /><sub><b>Ola Tarkowska</b></sub></a><br /><a href="https://github.com/EBI-Metagenomics/emg-toolkit/commits?author=olatarkowska" title="Code">💻</a><a href="https://github.com/EBI-Metagenomics/EMG-docs/commits/master?author=olatarkowska">📖</a></td>
    <td align="center"><a href="https://github.com/mscheremetjew"><img src="https://avatars3.githubusercontent.com/u/1681284?v=4" width="100px;" alt=""/><br /><sub><b>Maxim Scheremetjew</b></sub></a><br /><a href="https://github.com/EBI-Metagenomics/emg-toolkit/commits?author=mscheremetjew" title="Code">💻</a><a href="https://github.com/EBI-Metagenomics/EMG-docs/commits/master?author=mscheremetjew">📖</a></td>
    <td align="center"><a href="https://github.com/mberacochea"><img src="https://avatars3.githubusercontent.com/u/1123897?v=4" width="100px;" alt=""/><br /><sub><b>Martin Beracochea</b></sub></a><br /><a href="https://github.com/EBI-Metagenomics/emg-toolkit/commits?author=mberacochea" title="Code">💻</a></td>
  </tr>
</table>

<!-- markdownlint-enable -->
<!-- prettier-ignore-end -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

Contact
=======

If the documentation do not answer your questions, please [contact us](https://www.ebi.ac.uk/support/metagenomics).
