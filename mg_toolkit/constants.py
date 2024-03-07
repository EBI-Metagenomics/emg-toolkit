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

MG_SEQ_URL = "https://www.ebi.ac.uk/metagenomics/sequence-search/search/phmmer"

API_BASE = "https://www.ebi.ac.uk/metagenomics/api/latest"

MG_SAMPLE_URL = API_BASE + "/samples/{accession}"

MG_RUN_URL = API_BASE + "/runs/{accession}"

MG_ANALYSES_BASE_URL = API_BASE + "/analyses"

MG_ANALYSES_DOWNLOADS_URL = API_BASE + "/analyses/{accession}/downloads"

ENA_SEARCH_API_URL = "https://www.ebi.ac.uk/ena/portal/api/search"
ENA_XML_VIEW_URL = "https://www.ebi.ac.uk/ena/browser/api/xml"

EBI_URL_PREFIX = "https://www.ebi.ac.uk/"
REQUESTS_RETRIES = 3
