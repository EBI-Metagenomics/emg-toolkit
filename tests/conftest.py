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


import os
import pytest

import mongoengine

from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emgcli.settings')


def pytest_configure():
    settings.DEBUG = False
    settings.REST_FRAMEWORK['TEST_REQUEST_DEFAULT_FORMAT'] = 'vnd.api+json'
    # TODO: backend mock to replace FakeEMGBackend
    # settings.EMG_BACKEND_AUTH_URL = 'http://fake_backend/auth'
    settings.AUTHENTICATION_BACKENDS = ('test_utils.FakeEMGBackend',)
    # disconnect main database
    mongoengine.connection.disconnect()


# MongoDB connection
@pytest.fixture(scope='function')
def mongodb(request):
    db = mongoengine.connect('testdb')

    def finalizer():
        db.drop_database('testdb')
        db.close()

    request.addfinalizer(finalizer)

    return db
