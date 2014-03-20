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

    def test_entries_have_point_geometries_from_place_coordinates(self):
        geojson = tif2geojson(self.fullsample)
        geometry = geojson['features'][0]['geometry']
        self.assertEqual(geometry['coordinates'], [1.9733232234954645,
                                                   44.22139156541433,
                                                   200.0])

    def test_entries_with_no_coordinates_have_null_geom(self):
        geojson = tif2geojson(self.fullsample)
        geometry = geojson['features'][1]['geometry']
        self.assertEqual(geometry, None)

    def test_entries_have_properties_as_dict(self):
        geojson = tif2geojson(self.fullsample)
        feature = geojson['features'][0]
        self.assertTrue(isinstance(feature['properties'], dict))

    def test_entries_have_defaut_properties_as_none(self):
        geojson = tif2geojson(self.fullsample)
        properties = geojson['features'][0]['properties']
        self.assertEqual(sorted(properties.keys()),
                         ['description', 'pictures', 'title'])

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
