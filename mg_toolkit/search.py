#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021 EMBL - European Bioinformatics Institute
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

from .constants import (
    MG_SEQ_URL,
    MG_SAMPLE_URL,
    MG_RUN_URL,
)


logger = logging.getLogger(__name__)


def parse_fasta_file(file_path):
    """
    Parse fasta file
    """
    sequences = {}
    query_id = None
    with open(file_path, "r") as f:
        for line in f:
            if line.startswith(">"):
                query_id = line[1:].strip()
                sequences[query_id] = ""
            else:
                sequences[query_id] += line.strip()
    return sequences


def sequence_search(args):
    """
    Process given fasta file
    """
    args = vars(args)
    out_df = DataFrame()
    for s in args.pop("sequence"):
        sequences = parse_fasta_file(s)
        for sequence_data in sequences.items():
            query_id = sequence_data[0]
            sequence = sequence_data[1]
            print("Proccessing: {}".format(query_id))
            # Search MgnifyDB
            seq = SequenceSearch(
                sequence,
                query_id,
                database=args.pop("database", "full"),
                seq_evalue_threshold=args.pop("seq_evalue_threshold", None),
                hit_evalue_threshold=args.pop("hit_evalue_threshold", None),
                report_seq_evalue_threshold=args.pop(
                    "report_seq_evalue_threshold", None
                ),
                report_hit_evalue_threshold=args.pop(
                    "report_hit_evalue_threshold", None
                ),
                seq_bitscore_threshold=args.pop("seq_bitscore_threshold", None),
                hit_bitscore_threshold=args.pop("hit_bitscore_threshold", None),
                report_seq_bitscore_threshold=args.pop(
                    "report_seq_bitscore_threshold", None
                ),
                report_hit_bitscore_threshold=args.pop(
                    "report_hit_bitscore_threshold", None
                ),
            )
            response = seq.analyse_sequence()
            if not response:
                logger.warning("No results to report for %s" % query_id)
                return
            # Only process results when the request returned data
            results = response.get("results")
            if results:
                job_uuid = results["uuid"]
                logger.debug("Job %s" % job_uuid)
                out_df = out_df.append(
                    seq.results_to_df(seq.fetch_results(results), job_uuid)
                )
            else:
                logger.warning("No results to report for %s" % query_id)

    output_file = job_uuid + "_sequence_search.csv"
    if args["output"]:
        output_file = args["output"]

    out_df.to_csv(output_file, index=False)


class SequenceSearch(object):
    """
    Helper tool allowing to search non-redundant protein database using HMMER
    and fetch environmental metadata.
    """

    sequence = None
    database = "full"

    def __init__(self, sequence, query_id, database="full", *args, **kwargs):
        self.sequence = sequence
        self.query_id = query_id
        self.database = database
        self.seq_evalue_threshold = kwargs.pop("seq_evalue_threshold", None)
        self.hit_evalue_threshold = kwargs.pop("hit_evalue_threshold", None)
        self.report_seq_evalue_threshold = kwargs.pop(
            "report_seq_evalue_threshold", None
        )
        self.report_hit_evalue_threshold = kwargs.pop(
            "report_hit_evalue_threshold", None
        )
        self.seq_bitscore_threshold = kwargs.pop("seq_bitscore_threshold", None)
        self.hit_bitscore_threshold = kwargs.pop("hit_bitscore_threshold", None)
        self.report_seq_bitscore_threshold = kwargs.pop(
            "report_seq_bitscore_threshold", None
        )
        self.report_hit_bitscore_threshold = kwargs.pop(
            "report_hit_bitscore_threshold", None
        )

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
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        logger.debug("POST: %r" % data)
        request_data = requests.post(MG_SEQ_URL, data=data, headers=headers)
        # Check if data was returned
        if request_data:
            return request_data.json()
        else:
            return False

    def make_request(self, accession):
        if accession is None:
            return None
        headers = {
            "Accept": "application/json",
        }
        r = requests.get(
            MG_SAMPLE_URL.format(**{"accession": accession}), headers=headers
        )
        if r.status_code != requests.codes.ok:
            r = requests.get(
                MG_RUN_URL.format(**{"accession": accession}),
                headers=headers,
                params={"include": "sample"},
            )
        return r.json()

    def get_sample_metadata(self, accession, request):
        _meta = {}
        try:
            metadata = request["data"]["attributes"]["sample-metadata"]
            logger.debug(metadata)
        except KeyError:
            try:
                metadata = request["included"][0]["attributes"]["sample-metadata"]
                logger.debug(metadata)
            except KeyError:
                return _meta
        for m in metadata:
            unit = html.unescape(m["unit"]) if m["unit"] else ""
            _meta[m["key"].replace(" ", "_")] = "{value} {unit}".format(
                value=m["value"], unit=unit
            )  # noqa

        try:
            _meta["biome"], _meta["lineage"] = self.get_biome(request)
        except ValueError:
            pass
        return _meta

    def get_biome(self, request):
        _biome = None
        try:
            _biome = request["data"]["relationships"]["biome"]["data"]["id"]
            logger.debug(_biome)
        except KeyError:
            try:
                _biome = request["included"][0]["relationships"]["biome"]["data"][
                    "id"
                ]  # noqa
                logger.debug(_biome)
            except KeyError:
                pass
        if _biome is not None:
            return _biome.split(":")[-1], _biome
        raise ValueError("Biome doesn't exist.")

    def prepare_rows(self, hit):
        return {
            "kg": hit.get("kg", ""),
            "taxid": hit.get("taxid", ""),
            "desc": hit.get("desc", ""),
            "pvalue": hit.get("pvalue", ""),
            "species": hit.get("species", ""),
            "score": hit.get("score", ""),
            "evalue": hit.get("evalue", ""),
            "nreported": hit.get("nreported", ""),
            "uniprot": ",".join([i[0] for i in hit.get("uniprot_link", [])]),
        }

    def fetch_results(self, results):
        """
        Complete the HMMER hits with MGnify metadata from the API
        TODO: This could be parallelized for better performance
        """
        csv_rows = dict()
        for hit in results.get("hits", []):
            _row = self.prepare_rows(hit)
            mgnify = hit.get("mgnify", [])
            for res in mgnify.get("samples") or []:
                accession = res[0]
                logger.debug("Accession %s" % accession)
                uuid = "{n} {a}".format(**{"n": hit["name"], "a": accession})
                csv_rows[uuid] = dict()
                csv_rows[uuid].update(_row)
                req = self.make_request(accession)
                _meta = self.get_sample_metadata(accession=accession, request=req)
                csv_rows[uuid].update(_meta)
            for res in mgnify.get("runs") or []:
                accession = res[0]
                logger.debug("Accession %s" % accession)
                uuid = "{n} {a}".format(**{"n": hit["name"], "a": accession})
                csv_rows[uuid] = dict()
                csv_rows[uuid].update(_row)
                req = self.make_request(accession)
                _meta = self.get_sample_metadata(accession=accession, request=req)
                csv_rows[uuid].update(_meta)
        return csv_rows

    def results_to_df(self, csv_rows, uuid):
        """
        Convert search results to dataframe
        """

        df = DataFrame(csv_rows).T
        df.reset_index(inplace=True)
        df.rename(columns={"index": "name"}, inplace=True)
        # Split index to subject_id and accession
        df[["subject_id", "accession"]] = df["name"].str.split(" ", 1, expand=True)

        # Put query_id, subject_id, and accession as first three columns
        subject_id = df.subject_id
        accession = df.accession
        df.drop(["name", "subject_id", "accession"], axis=1, inplace=True)
        df.insert(0, "query_id", self.query_id)
        df.insert(1, "subject_id", subject_id)
        df.insert(1, "accession", accession)

        def _clean_column(col):
            return (
                col.replace(")", "")
                .replace("(", "")
                .replace("/", "_")
                .replace(",", "_")
            )

        # Clean columns from (),\
        df.rename(_clean_column, axis="columns", inplace=True)

        return df
