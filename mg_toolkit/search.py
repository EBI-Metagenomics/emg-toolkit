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

import logging
import requests
import html
from pandas import DataFrame

from .utils import (
    MG_SEQ_URL,
    MG_SAMPLE_URL,
    MG_RUN_URL,
)


logger = logging.getLogger(__name__)


def sequence_search(args):

    """
    Process given fasta file
    """
    args = vars(args)
    for s in args.pop("sequence"):
        with open(s) as f:
            sequence = f.read()
            seq = SequenceSearch(
                sequence,
                database=args.pop("database", "full"),
                seq_evalue_threshold=args.pop(
                    "seq_evalue_threshold", None),
                hit_evalue_threshold=args.pop(
                    "hit_evalue_threshold", None),
                report_seq_evalue_threshold=args.pop(
                    "report_seq_evalue_threshold", None),
                report_hit_evalue_threshold=args.pop(
                    "report_hit_evalue_threshold", None),
                seq_bitscore_threshold=args.pop(
                    "seq_bitscore_threshold", None),
                hit_bitscore_threshold=args.pop(
                    "hit_bitscore_threshold", None),
                report_seq_bitscore_threshold=args.pop(
                    "report_seq_bitscore_threshold", None),
                report_hit_bitscore_threshold=args.pop(
                    "report_hit_bitscore_threshold", None),
            )
            results = seq.analyse_sequence()
            job_uuid = results['results']['uuid']
            logger.debug("Job %s" % job_uuid)
            seq.save_to_csv(seq.fetch_results(results), filename=job_uuid)


class SequenceSearch(object):

    """
    Helper tool allowing to search non-redundant protein database using HMMER
    and fetch environmental metadata.
    """

    sequence = None
    database = "full"

    def __init__(self, sequence, database="full", *args, **kwargs):
        self.sequence = sequence
        self.database = database
        self.seq_evalue_threshold = kwargs.pop(
            "seq_evalue_threshold", None)
        self.hit_evalue_threshold = kwargs.pop(
            "hit_evalue_threshold", None)
        self.report_seq_evalue_threshold = kwargs.pop(
            "report_seq_evalue_threshold", None)
        self.report_hit_evalue_threshold = kwargs.pop(
            "report_hit_evalue_threshold", None)
        self.seq_bitscore_threshold = kwargs.pop(
            "seq_bitscore_threshold", None)
        self.hit_bitscore_threshold = kwargs.pop(
            "hit_bitscore_threshold", None)
        self.report_seq_bitscore_threshold = kwargs.pop(
            "report_seq_bitscore_threshold", None)
        self.report_hit_bitscore_threshold = kwargs.pop(
            "report_hit_bitscore_threshold", None)

    def analyse_sequence(self):
        data = {
            "seqdb": self.database,
            "seq": self.sequence,
        }
        if self.seq_evalue_threshold is not None:
            data["incE"] = self.seq_evalue_threshold
        if self.hit_evalue_threshold is not None:
            data["incdomE"] = self.hit_evalue_threshold
        if self.report_seq_evalue_threshold is not None:
            data["E"] = self.report_seq_evalue_threshold
        if self.report_hit_evalue_threshold is not None:
            data["domE"] = self.report_hit_evalue_threshold
        if self.seq_bitscore_threshold is not None:
            data["incT"] = self.seq_bitscore_threshold
        if self.hit_bitscore_threshold is not None:
            data["incdomT"] = self.hit_bitscore_threshold
        if self.report_seq_bitscore_threshold is not None:
            data["T"] = self.report_seq_bitscore_threshold
        if self.report_hit_bitscore_threshold is not None:
            data["domT"] = self.report_hit_bitscore_threshold

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        logger.debug("POST: %r" % data)
        return requests.post(MG_SEQ_URL, data=data, headers=headers).json()

    def make_request(self, accession):
        if accession is None:
            return None
        headers = {
            'Accept': 'application/vnd.api+json',
        }
        r = requests.get(
            MG_SAMPLE_URL.format(**{'accession': accession}),
            headers=headers
        )
        if r.status_code != requests.codes.ok:
            r = requests.get(
                MG_RUN_URL.format(**{'accession': accession}),
                headers=headers
            )
        return r.json()

    def get_sample_metadata(self, accession, request):
        _meta = {}
        try:
            metadata = request['data']['attributes']['sample-metadata']
            logger.debug(metadata)
        except KeyError:
            try:
                metadata = \
                    request['included'][0]['attributes']['sample-metadata']
                logger.debug(metadata)
            except KeyError:
                return _meta
        for m in metadata:
            unit = html.unescape(m['unit']) if m['unit'] else ""
            _meta[m['key'].replace(" ", "_")] = "{value} {unit}".format(value=m['value'], unit=unit)  # noqa

        try:
            _meta['biome'], _meta['lineage'] = self.get_biome(request)
        except ValueError:
            pass
        return _meta

    def get_biome(self, request):
        _biome = None
        try:
            _biome = request['data']['relationships']['biome']['data']['id']
            logger.debug(_biome)
        except KeyError:
            try:
                _biome = request['included'][0]['relationships']['biome']['data']['id']  # noqa
                logger.debug(_biome)
            except KeyError:
                pass
        if _biome is not None:
            return _biome.split(":")[-1], _biome
        raise ValueError("Biome doesn't exist.")

    def prepare_rows(self, hit):
        _row = dict()
        _row['kg'] = hit.get('kg', '')
        _row['taxid'] = hit.get('taxid', '')
        _row['name'] = hit.get('name', '')
        _row['desc'] = hit.get('desc', '')
        _row['pvalue'] = hit.get('pvalue', '')
        _row['species'] = hit.get('species', '')
        _row['score'] = hit.get('score', '')
        _row['evalue'] = hit.get('evalue', '')
        _row['nreported'] = hit.get('nreported', '')
        _row['uniprot'] = ",".join(
            [i[0] for i in hit.get('uniprot_link', [])])
        return _row

    def fetch_results(self, results):
        csv_rows = dict()
        for hit in results['results']['hits']:
            _row = self.prepare_rows(hit)
            mgnify = hit.get('mgnify', [])
            for res in mgnify.get('samples') or []:
                accession = res[0]
                logger.debug("Accession %s" % accession)
                uuid = "{n} {a}".format(**{'n': hit['name'], 'a': accession})
                csv_rows[uuid] = dict()
                csv_rows[uuid].update(_row)
                req = self.make_request(accession)
                _meta = self.get_sample_metadata(
                    accession=accession, request=req
                )
                csv_rows[uuid].update(_meta)
            for res in mgnify.get('runs') or []:
                accession = res[0]
                logger.debug("Accession %s" % accession)
                uuid = "{n} {a}".format(**{'n': hit['name'], 'a': accession})
                csv_rows[uuid] = dict()
                csv_rows[uuid].update(_row)
                req = self.make_request(accession)
                _meta = self.get_sample_metadata(
                    accession=accession, request=req
                )
                csv_rows[uuid].update(_meta)
        return csv_rows

    def save_to_csv(self, csv_rows, filename):
        df = DataFrame(csv_rows).T
        df.index.name = 'name'
        filename = "{}_sequence_search.csv".format(filename)
        df.to_csv(filename)
