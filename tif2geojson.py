from xml.parsers.expat import ExpatError
from collections import OrderedDict

import geojson
import xmltodict


class Converter(object):
    def __call__(self, content):
        features = self._parse_content(content)
        result = geojson.FeatureCollection(features)
        return result

    def _parse_content(self, content):
        try:
            parsed = xmltodict.parse(content)
        except ExpatError:
            parsed = dict()
        entries = parsed.get('listeOI', {}).get('OIs', {}).get('tif:OI', [])
        features = []
        for entry in entries:
            feature = self._parse_entry(entry)
            features.append(feature)
        return features

    def _parse_entry(self, entry):
        geometry = self._parse_location(entry)
        return geojson.Feature(geometry=geometry)

    def _parse_location(self, entry):
        """
        Return the **first** location as `geojson.Point`.
        """
        locations = entry.get('tif:Geolocalisations')

        if not isinstance(locations, list):
            return None

        coords = []
        for location in locations:
            coords = location.get('tif:DetailGeolocalisation', {}) \
                             .get('tif:Zone', {}) \
                             .get('tif:Points', {}) \
                             .get('tif:DetailPoint', {}) \
                             .get('tif:Coordonnees', {}) \
                             .get('tif:DetailCoordonnees', {})
            if 'tif:Latitude' not in coords:
                continue
            lat = float(coords['tif:Latitude'])
            lng = float(coords['tif:Longitude'])
            altitude = float(coords['tif:Altitude'])
            coords = [lng, lat, altitude]
            return geojson.Point(coords)

        return None


tif2geojson = Converter()
