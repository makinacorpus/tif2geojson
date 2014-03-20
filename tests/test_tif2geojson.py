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
        geojson = tif2geojson(self.emptysample)
        self.assertTrue(isinstance(geojson, dict))

    def test_provides_features_collection(self):
        geojson = tif2geojson(self.fullsample)
        self.assertEqual(geojson['type'], 'FeatureCollection')

    def test_provides_entries_as_features_list(self):
        geojson = tif2geojson(self.fullsample)
        self.assertTrue(isinstance(geojson['features'], list))

    def test_entries_are_feature(self):
        geojson = tif2geojson(self.fullsample)
        feature = geojson['features'][0]
        self.assertEqual(feature['type'], 'Feature')

    def test_entries_have_point_geometries(self):
        geojson = tif2geojson(self.fullsample)
        feature = geojson['features'][0]
        geometry = feature['geometry']
        self.assertEqual(geometry['type'], 'Point')

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
