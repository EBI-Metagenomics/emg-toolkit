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
    meta = dict()
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
        meta[key] = value
    return meta


def original_metadata(args):

    for accession in args.accession:
        logger.debug("Accession %s" % accession)

        resp = requests.get(sample_url().format(**{'accession': accession}))
        try:
            resp = resp.json()
        except JSONDecodeError:
            logger.error("%s is not valid." % accession)
            continue

        _accessions = {
            r['run_accession']:
                {
                    'sample_accession': r['secondary_sample_accession'],
                    'read_depth': r['depth']
                }
            for r in resp
        }

        meta_csv = dict()
        _sample = None
        _meta = None
        for (run, sample) in _accessions.items():
            if sample != _sample:
                _meta = get_metadata(sample['sample_accession'])
            meta_csv[run] = _meta
            meta_csv[run]['Sample'] = sample['sample_accession']
            meta_csv[run]['Read depth'] = sample['read_depth']
            _sample = sample['sample_accession']

        df = DataFrame(meta_csv).T
        df.index.name = 'Run'
        fname = "{}.csv".format(accession)
        df.to_csv(fname)
