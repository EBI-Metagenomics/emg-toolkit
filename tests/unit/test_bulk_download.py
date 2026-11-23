#!/bin/env python3

import importlib
import os
import unittest
from unittest import mock

from mg_toolkit import constants
from mg_toolkit.bulk_download import BulkDownloader


class FakeResponse:
    """Minimal stand-in for a requests response."""

    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.ok = status_code < 400

    def json(self):
        return self._payload


class UnexpectedResponseTests(unittest.TestCase):
    """The API layout is versioned; a mismatch must not surface as a KeyError."""

    def setUp(self):
        self.downloader = BulkDownloader("MGYS00002098", os.getcwd(), "4.0", None)
        self.downloader.http = mock.Mock()

    def test_v2_style_response_raises_informative_error(self):
        # v2 answers with a top level "count"/"items" envelope, no "meta".
        self.downloader.http.get.return_value = FakeResponse({"count": 1, "items": []})

        with self.assertRaises(ValueError) as raised:
            self.downloader.run()

        message = str(raised.exception)
        self.assertIn("meta.pagination.count", message)
        self.assertIn("MG_TOOLKIT_API_BASE", message)
        self.assertIn("count", message)


class ApiBaseTests(unittest.TestCase):
    def test_default_api_base_is_pinned_to_a_version(self):
        self.assertTrue(
            constants.DEFAULT_API_BASE.endswith("/api/v1"),
            "the API base must be pinned to a version, not to the floating "
            "'latest' alias",
        )

    def test_api_base_can_be_overridden_from_the_environment(self):
        try:
            with mock.patch.dict(
                os.environ, {"MG_TOOLKIT_API_BASE": "http://localhost:8000/api/v9/"}
            ):
                importlib.reload(constants)
                self.assertEqual(constants.API_BASE, "http://localhost:8000/api/v9")
                self.assertEqual(
                    constants.MG_ANALYSES_BASE_URL,
                    "http://localhost:8000/api/v9/analyses",
                )
        finally:
            importlib.reload(constants)
