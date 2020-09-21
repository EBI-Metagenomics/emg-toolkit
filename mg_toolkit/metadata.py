#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2020 EMBL - European Bioinformatics Institute
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
import xml.etree.ElementTree as ET

import requests

from pandas import DataFrame

from .constants import ENA_SEARCH_API_URL, ENA_XML_VIEW_URL

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


logger = logging.getLogger(__name__)


def original_metadata(args):

    """
    Process given accessions
    """

    for accession in args.accession:
        logger.debug("Accession %s" % accession)
        om = OriginalMetadata(accession)
        om.save_to_csv(om.fetch_metadata())


class OriginalMetadata:
    """
    Helper tool allowing to download original metadata for the given accession from ENA.
    """

    accession = None

    def __init__(self, accession, *args, **kwargs):
        self.accession = accession

    def get_metadata(self, sample_accession):
        """Get the sample metadata from ENA API."""
        return_meta = {}

        response = requests.get(ENA_XML_VIEW_URL + "/" + sample_accession)

        if not response.ok:
            logger.error("Metadata fetch failed for accession:" + self.accession)
            return

        metadata_xml = ET.fromstring(response.content)

        for sample_attribute in metadata_xml.findall(
            "./SAMPLE/SAMPLE_ATTRIBUTES/SAMPLE_ATTRIBUTE"
        ):
            tag = sample_attribute.find("TAG")
            value = sample_attribute.find("VALUE")
            # optional
            units = sample_attribute.find("UNITS")
            if tag is None:
                # broken metadata but not fatal
                continue

            key = tag.text.strip()
            key_value = None
            if value is not None:
                key_value = value.text.strip()
            if units is not None:
                key_value += units.text.strip()

            return_meta[key] = key_value

        return return_meta

    def fetch_metadata(self):
        """Get metadata from ENA API."""
        response = requests.get(
            ENA_SEARCH_API_URL,
            params={
                "result": "read_run",
                "query": " OR ".join(
                    [
                        "study_accession=" + self.accession,
                        "secondary_study_accession=" + self.accession,
                    ]
                ),
                "fields": ",".join(
                    [
                        "run_accession",
                        "secondary_sample_accession",
                        "sample_accession",
                        "depth",
                    ]
                ),
                "format": "json",
            },
        )

        if response.status_code in (
            requests.codes.no_content,
            requests.codes.not_found,
        ):
            logger.error("Accession not found in ENA")
            return
        if response.status_code in (
            requests.codes.unauthorized,
            requests.codes.forbidden,
        ):
            logger.error("Not authorized.")
            return

        try:
            response_data = response.json()
        except JSONDecodeError:
            logger.error(
                "Error decoding ENA sample_metadata response for accession: "
                + self.accession
            )
            return

        _accessions = {
            r["run_accession"]: {
                "sample_accession": r["secondary_sample_accession"],
                "read_depth": r["depth"],
            }
            for r in response_data
        }

        meta_csv = dict()
        _sample = None
        _meta = None

        for (run, sample) in _accessions.items():
            if sample != _sample:
                _meta = self.get_metadata(sample["sample_accession"])
            meta_csv[run] = _meta
            meta_csv[run]["Sample"] = sample["sample_accession"]
            meta_csv[run]["Read depth"] = sample["read_depth"]
            _sample = sample["sample_accession"]

        return meta_csv

    def save_to_csv(self, meta_csv, filename=None):
        """Store the CSV in a file"""
        df = DataFrame(meta_csv).T
        df.index.name = "Run"
        if filename is None:
            filename = "{}.csv".format(self.accession)
        df.to_csv(filename)
