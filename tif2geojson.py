from xml.parsers.expat import ExpatError

import geojson
import xmltodict


DEFAULT_LANGUAGE = 'EN'
SUPPORTED_PROPERTIES = ['title', 'description', 'category',
                        'pictures', 'website']

CODE_WEBSITE = '04.02.05'
CODE_IMAGE = '03.01.01'


class Converter(object):
    def __init__(self):
        self.content = ''
        self.properties = None
        self.lang = DEFAULT_LANGUAGE

    def __call__(self, content, properties=None, lang=None):
        self.content = content
        self.properties = properties
        self.lang = lang if lang else self.lang
        features = self._parse_content()
        result = geojson.FeatureCollection(features)
        return result

    def _parse_content(self):
        try:
            parsed = xmltodict.parse(self.content)
        except ExpatError:
            parsed = dict()
        entries = _deep_value(parsed, 'listeOI', 'OIs', 'tif:OI')
        features = []
        for entry in entries:
            feature = self._parse_entry(entry)
            features.append(feature)
        return features

    def _parse_entry(self, entry):
        id_ = _deep_value(entry, 'tif:DublinCore', 'dc:identifier')
        geometry = self._parse_location(entry)
        properties = self._parse_properties(entry)
        return geojson.Feature(id=id_,
                               geometry=geometry,
                               properties=properties)

    def _parse_location(self, entry):
        """
        Return the **first** location as `geojson.Point`.
        """
        locations = entry.get('tif:Geolocalisations')

        if not isinstance(locations, list):
            return None

        coords = []
        for location in locations:
            coords = _deep_value(location, 'tif:DetailGeolocalisation',
                                           'tif:Zone',
                                           'tif:Points',
                                           'tif:DetailPoint',
                                           'tif:Coordonnees',
                                           'tif:DetailCoordonnees')
            if 'tif:Latitude' not in coords:
                continue
            lat = float(coords['tif:Latitude'])
            lng = float(coords['tif:Longitude'])
            altitude = float(coords['tif:Altitude'])
            coords = [lng, lat, altitude]
            return geojson.Point(coords)

        return None

    def _parse_properties(self, entry):
        properties = {}
        for prop in SUPPORTED_PROPERTIES:
            if self.properties is None or prop in self.properties:
                properties[prop] = getattr(self, '_parse_property_%s' % prop)(entry)
        return properties

    def _parse_property_category(self, entry):
        category = _deep_value(entry, 'tif:DublinCore', 'tif:Classification')
        return {
            'id': category.get('@code'),
            'label': category.get('#text')
        }

    def _parse_property_title(self, entry):
        return _deep_value(entry, 'tif:DublinCore', 'dc:title').get('#text')

    def _parse_property_description(self, entry):
        descriptions = _deep_value(entry, 'tif:DublinCore', 'dc:description',
                                   default=[])
        for description in descriptions:
            if description.get('@xml:lang') == self.lang:
                return description.get('#text')

    def _parse_property_website(self, entry):
        contacts = _deep_value(entry, 'tif:Contacts', 'tif:DetailContact')
        for contact in contacts:
            persons = _deep_value(contact, 'tif:Adresses',
                                           'tif:DetailAdresse',
                                           'tif:Personnes',
                                           'tif:DetailPersonne')
            if isinstance(persons, dict):
                persons = [persons]

            if isinstance(persons, list):
                for person in persons:
                    media = _deep_value(person, 'tif:MoyensCommunications',
                                                'tif:DetailMoyenCom')
                    if isinstance(media, list):
                        for medium in media:
                            if medium['@type'] == CODE_WEBSITE:
                                return medium.get('tif:Coord')

    def _parse_property_pictures(self, entry):
        multimedia = _deep_value(entry, 'tif:Multimedia',
                                        'tif:DetailMultimedia')
        pictures =  []
        for multimedium in multimedia:
            if multimedium['@type'] == CODE_IMAGE:
                picture = {
                    'url': multimedium['tif:URL'],
                    'copyright': multimedium['tif:Copyright']
                }
                pictures.append(picture)
        return pictures


def _deep_value(*args, **kwargs):
    """ Drills down into tree using the keys
    """
    node, keys = args[0], args[1:]
    for key in keys:
        node = node.get(key, {})
    default = kwargs.get('default', {})
    if node in ({}, [], None):
        node = default
    return node


tif2geojson = Converter()
