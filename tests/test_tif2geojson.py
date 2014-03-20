#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_tif2geojson
----------------------------------

Tests for `tif2geojson` module.
"""
import os
import unittest

from tif2geojson import tif2geojson


here = os.path.dirname(__file__)


class TestTif2geojson(unittest.TestCase):

    def setUp(self):
        filename = os.path.join(here, 'data', 'embedded.xml')
        self.fullsample = open(filename).read()
        self.emptysample = '<?xml version="1.0"?>'

    def test_converter_returns_dict(self):
        geojson = tif2geojson(self.fullsample)
        self.assertTrue(isinstance(geojson, dict))

    def test_converter_returns_dict_when_empty(self):
        geojson = tif2geojson(self.fullsample)
        self.assertTrue(isinstance(geojson, dict))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
