from xml.parsers.expat import ExpatError

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
        geometry = geojson.Point()
        return geojson.Feature(geometry=geometry)


tif2geojson = Converter()
