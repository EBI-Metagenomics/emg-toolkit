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

import os

MG_SEQ_URL = "https://www.ebi.ac.uk/metagenomics/sequence-search/search/phmmer"

# Pin the MGnify API version instead of using the versionless "latest" alias.
# "latest" used to resolve to v1 but was re-pointed to v2, which returns a
# different response envelope (no "meta", no "links", "count"/"items" instead
# of "meta.pagination.count"/"data") and does not honour the study_accession
# and pipeline_version query parameters used by bulk_download.
DEFAULT_API_BASE = "https://www.ebi.ac.uk/metagenomics/api/v1"

# Allow overriding the API location, e.g. to talk to a different MGnify
# deployment or to follow a future API version without a new release.
API_BASE = os.environ.get("MG_TOOLKIT_API_BASE", DEFAULT_API_BASE).rstrip("/")

MG_SAMPLE_URL = API_BASE + "/samples/{accession}"

MG_RUN_URL = API_BASE + "/runs/{accession}"

MG_ANALYSES_BASE_URL = API_BASE + "/analyses"

MG_ANALYSES_DOWNLOADS_URL = API_BASE + "/analyses/{accession}/downloads"

ENA_SEARCH_API_URL = "https://www.ebi.ac.uk/ena/portal/api/search"
ENA_XML_VIEW_URL = "https://www.ebi.ac.uk/ena/browser/api/xml"

EBI_URL_PREFIX = "https://www.ebi.ac.uk/"
REQUESTS_RETRIES = 3
