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
from pandas import DataFrame

logger = logging.getLogger(__name__)


SAMPLES_URL = "https://www.ebi.ac.uk/ena/portal/api/search?result=read_run&query=study_accession%3D{accession}%20OR%20secondary_study_accession%3D{accession}&fields=secondary_sample_accession&format=json"

METADATA_URL = "https://www.ebi.ac.uk/ena/data/view/{accession}&display=xml"


def full_metadata(args):

    for accession in args.accession:
        logger.debug(accession)

        resp = requests.get(SAMPLES_URL.format(**{'accession': accession }))
        sample_accession = [r['secondary_sample_accession'] for r in resp.json()]

        meta_csv = dict()
        for s in sample_accession:
            sr = requests.get(METADATA_URL.format(**{'accession': s }))
            x = json.loads(json.dumps(xmltodict.parse(sr.content)))
            for m in x['ROOT']['SAMPLE']['SAMPLE_ATTRIBUTES']['SAMPLE_ATTRIBUTE']:
                try:
                    key = m['TAG']
                except KeyError:
                    continue
                try:
                    value = m['VALUE']
                except KeyError:
                    value = None
                try:
                    meta_csv[s][key] = value
                except KeyError:
                    meta_csv[s] = {key: value}

        df = DataFrame(meta_csv).T
        if args.export:
            df.to_csv(args.export)
        else:
            logger.info(df)
