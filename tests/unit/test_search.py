#!/bin/env python3

import os
import unittest

from mg_toolkit.search import parse_fasta_file


class FastaParseTests(unittest.TestCase):
    def _build_path(self, folder):
        return os.path.abspath("/" + os.path.dirname(__file__) + folder)

    def test_parse_fasta_file(self):
        """Test fasta parsing method"""
        test_fasta = self._build_path("/fixtures/test.fasta")

        expected = {
            "fasta_one example": "MSTHPIRVFSEIGKLKKVMLHRPGKELENLQPDYLERLLFDD",
            "fasta_two example": "EEYLEEANIRGRETKKAIRELLHGIKDNQELVEKT",
            "fasta_three example": "AVSLNHMYADTRNRETLYGKYIFKYHPVYGGNVELVYNREEDTRIEGGDELVLSKDVLAVGISQRTDAA",
        }

        fn_result = parse_fasta_file(test_fasta)

        self.assertDictEqual(fn_result, expected)
