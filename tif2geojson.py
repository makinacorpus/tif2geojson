import geojson
import xmltodict


class Converter(object):
    def __call__(self, content):
        features = []
        result = geojson.FeatureCollection(features)
        return result


tif2geojson = Converter()
