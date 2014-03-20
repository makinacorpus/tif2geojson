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

    def test_entries_have_id(self):
        geojson = tif2geojson(self.fullsample)
        id_ = geojson['features'][0]['id']
        self.assertEqual(id_, u'TFO17142937971')

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

    def test_entries_have_defaut_properties(self):
        geojson = tif2geojson(self.fullsample)
        properties = geojson['features'][0]['properties']
        self.assertEqual(sorted(properties.keys()),
                         ['description', 'pictures', 'title', 'website'])

    def test_entries_properties_can_be_specified(self):
        geojson = tif2geojson(self.fullsample, properties=['title'])
        properties = geojson['features'][0]['properties']
        self.assertEqual(len(properties.keys()), 1)
        self.assertIn('title', properties)

    def test_entries_unknown_properties_are_ignored(self):
        geojson = tif2geojson(self.fullsample, properties=['age'])
        properties = geojson['features'][0]['properties']
        self.assertNotIn('age', properties)

    def test_entries_have_title(self):
        geojson = tif2geojson(self.fullsample)
        properties = geojson['features'][0]['properties']
        self.assertEqual(properties['title'], u'Le Belle Rive')

    def test_entries_have_description(self):
        geojson = tif2geojson(self.fullsample)
        properties = geojson['features'][0]['properties']
        description = "Comfortable rooms, laundry service, swimming pool, tennis, closed garage, large car park."
        self.assertEqual(properties['description'], description)

    def test_entries_have_description_in_specified_language(self):
        geojson = tif2geojson(self.fullsample, lang='FR')
        properties = geojson['features'][0]['properties']
        description = u"Chambres confortables, service buanderie, piscine, tennis, garage ferm\xe9, grand parking, Wifi.<br/>"
        self.assertEqual(properties['description'], description)

    def test_entries_have_website(self):
        geojson = tif2geojson(self.fullsample)
        properties = geojson['features'][0]['properties']
        self.assertEqual(properties['website'], u'www.lebellerive.fr/')

    def test_entries_have_pictures_as_list(self):
        geojson = tif2geojson(self.fullsample)
        properties = geojson['features'][0]['properties']
        self.assertTrue(isinstance(properties['pictures'], list))

    def test_entries_pictures_have_url_and_credits(self):
        geojson = tif2geojson(self.fullsample)
        picture = geojson['features'][0]['properties']['pictures'][0]
        self.assertEqual(picture['url'], u'http://www.caravelis.com/xml/oi/TFO17142937971/TFO17142937971-14a/medias/jpg/vueg__n__rale.jpg')
        self.assertEqual(picture['copyright'], u'HÔTEL LE BELLE RIVE')

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
