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


class FailToGetException(Exception):
    """Fail to get an url exception"""

    def __init__(self, url, status_code, message, *arg, **kwargs):
        self.url = url
        self.status_code = status_code
        message = "Failed to get URL: %s. HTTP Status Code: %s" % (
            self.url,
            self.status_code,
        )
        super().__init__(message)

    def __str__(self):
        print(self.message)
