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
import xmltodict
import json

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

from pandas import DataFrame

from .utils import (
    sample_url,
    metadata_url
)

logger = logging.getLogger(__name__)


def get_metadata(accession):
    sample = requests.get(metadata_url().format(**{'accession': accession}))
    x = json.loads(json.dumps(xmltodict.parse(sample.content)))
    for m in x['ROOT']['SAMPLE']['SAMPLE_ATTRIBUTES']['SAMPLE_ATTRIBUTE']:
        try:
            key = m['TAG']
        except KeyError:
            continue
        try:
            value = m['VALUE']
        except KeyError:
            value = None
        return key, value


def original_metadata(args):

    for accession in args.accession:
        logger.debug(accession)

        resp = requests.get(sample_url().format(**{'accession': accession}))
        try:
            resp = resp.json()
        except JSONDecodeError:
            logger.error("%r is not valid." % accession)
            continue

        sample_accession = [r['secondary_sample_accession'] for r in resp]

        meta_csv = dict()
        for s in sample_accession:
            key, value = get_metadata(s)
            try:
                meta_csv[s][key] = value
            except KeyError:
                meta_csv[s] = {key: value}

        df = DataFrame(meta_csv).T
        if args.export:
            fname = "{}_{}".format(accession, args.export)
            df.to_csv(fname)
        else:
            logger.info(df)
