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

import os
import logging
import argparse
import textwrap
import mg_toolkit

from .metadata import original_metadata  # noqa
from .search import sequence_search  # noqa
from .bulk_download import bulk_download  # noqa

__version__ = '0.6.5'
__all__ = [
    'original_metadata',
    'sequence_search',
    'bulk_download'
]


def is_file(filename):
    if not os.path.isfile(filename):
        msg = "{0} is not a directory".format(filename)
        raise argparse.ArgumentTypeError(msg)
    else:
        return filename


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
        Metagenomics toolkit
        --------------------''')
    )
    parser.add_argument(
        '-V', '--version', action='version', version=__version__,
        help='print version information'
    )
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='print debugging information'
    )

    subparsers = parser.add_subparsers(dest='tool')

    original_metadata_parser = subparsers.add_parser(
        'original_metadata', help='Download original metadata.'
    )
    original_metadata_parser.add_argument(
        '-a', '--accession', required=True, nargs='+',
        help='Provide study accession, e.g. PRJEB1787 or ERP001736.'
    )

    sequence_search_parser = subparsers.add_parser(
        'sequence_search',
        help='Search non-redundant protein database using HMMER'
    )

    sequence_search_parser.add_argument(
        '-seq', '--sequence', required=True, type=is_file, nargs='+',
        help='Provide path to fasta file.'
    )
    sequence_search_parser.add_argument(
        '-db', '--database', type=str, choices=['full', 'all', 'partial', ],
        default='full',
        help='Choose peptide database (default: %(default)s).'
    )

    sequence_search_subparser = \
        sequence_search_parser.add_subparsers(dest='threshold')

    # e-value
    evalue_parser = sequence_search_subparser.add_parser(
        'evalue',
        help='Search non-redundant protein database using HMMER.'
    )
    evalue_parser.add_argument(
        '-incE', '--seq-evalue-threshold', type=float, default=0.01,
        help=('Sequence E-value threshold. Accepted value 0 < x ≤ 10 '
              '(default: %(default)s).')
    )
    evalue_parser.add_argument(
        '-incdomE', '--hit-evalue-threshold', type=float, default=0.03,
        help=('Hit E-value threshold. Accepted value 0 < x ≤ 10 '
              '(default: %(default)s).')
    )
    evalue_parser.add_argument(
        '-E', '--report-seq-evalue-threshold', type=float, default=1,
        help=('Sequence E-value threshold (reporting).'
              'Accepted value 0 < x ≤ 10 (default: %(default)s).')
    )
    evalue_parser.add_argument(
        '-domE', '--report-hit-evalue-threshold', type=float, default=1,
        help=('Hit E-value threshold (reporting). Accepted value 0 < x ≤ 10 '
              '(default: %(default)s).')
    )

    # bit score
    bitscore_parser = sequence_search_subparser.add_parser(
        'bitscore',
        help='Search non-redundant protein database using HMMER.'
    )
    bitscore_parser.add_argument(
        '-incT', '--seq-bitscore-threshold', type=float, default=25,
        help=('Sequence bit score threshold. Accepted values x > 0 '
              '(default: %(default)s).')
    )
    bitscore_parser.add_argument(
        '-incdomT', '--hit-bitscore-threshold', type=float, default=23,
        help=('Hit bit score threshold. Accepted values x > 0 '
              '(default: %(default)s).')
    )
    bitscore_parser.add_argument(
        '-T', '--report-seq-bitscore-threshold', type=float, default=7,
        help=('Sequence E-value threshold (reporting). Accepted values x > 0 '
              '(default: %(default)s).')
    )
    bitscore_parser.add_argument(
        '-domT', '--report-hit-bitscore-threshold', type=float, default=5,
        help=('Hit E-value threshold (reporting). Accepted values x > 0 '
              '(default: %(default)s).')
    )

    bulk_download_parser = subparsers.add_parser(
        'bulk_download',
        help='Download result files in bulks for an entire study.'
    )

    bulk_download_parser.add_argument(
        '-a', '--accession', required=True,
        help=('Provide the study/project accession of your interest, e.g. '
              'ERP001736, SRP000319. The study must be publicly available in '
              'MGnify.')
    )

    bulk_download_parser.add_argument(
        '-o', '--output_path', required=False, default=os.getcwd(),
        help=('Location of the output directory, where the downloadable files '
              'are written to.\nDEFAULT: CWD')
    )

    bulk_download_parser.add_argument(
        '-p', '--pipeline', required=False, choices=[
            '1.0', '2.0', '3.0', '4.0', '4.1', '5.0',
        ],
        help=('Specify the version of the pipeline you are interested in. '
              'Lets say your study of interest has been analysed with '
              'multiple version, but you are only interested in a particular '
              'version then used this option to filter down the results by '
              'the version you interested in.'
              '\nDEFAULT: Downloads all versions')
    )

    bulk_download_parser.add_argument(
        '-g', '--result_group', required=False,
        choices=[
            'sequence_data', 'functional_annotations', 'taxonomic_annotations',
            'taxonomic_annot_ssu', 'taxonomic_annot_lsu', 'stats',
            'non_coding_rna'],
        help=('Provide a single result group if needed. '
              'Supported result groups are: '
              '[sequence_data (all version), '
              'functional_annotations (all version), '
              'taxonomic_annotations (1.0-3.0), '
              'taxonomic_annot_ssu (>=4.0), '
              'taxonomic_annot_lsu (>=4.0), '
              'stats, '
              'non_coding_rna (>=4.0)'
              '\nDEFAULT: Downloads all result groups if not provided.'
              '\n(default: %(default)s).')
    )

    args = parser.parse_args()

    if args.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARN

    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)

    if args.tool is not None:
        return getattr(mg_toolkit, args.tool)(args)


if __name__ == '__main__':
    main()
