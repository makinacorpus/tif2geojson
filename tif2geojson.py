import geojson
import xmltodict


class Converter(object):
    def __call__(self, content):
        features = self._parse_features(content)
        result = geojson.FeatureCollection(features)
        return result

    def _parse_features(self, content):
        return [geojson.Feature()]


tif2geojson = Converter()
