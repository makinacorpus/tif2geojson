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
        entries = parsed.get('listeOI', {}).get('OIs', {}).get('tif:OI', [])
        features = []
        for entry in entries:
            feature = self._parse_entry(entry)
            features.append(feature)
        return features

    def _parse_entry(self, entry):
        id_ = entry.get('tif:DublinCore', {}).get('dc:identifier')
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

    def _parse_properties(self, entry):
        properties = {}
        for prop in SUPPORTED_PROPERTIES:
            if self.properties is None or prop in self.properties:
                properties[prop] = getattr(self, '_parse_property_%s' % prop)(entry)
        return properties

    def _parse_property_category(self, entry):
        main = entry.get('tif:DublinCore', {})
        category = main.get('tif:Classification', {})
        return {
            'id': category.get('@code'),
            'label': category.get('#text')
        }
        return main.get('dc:title', {}).get('#text')

    def _parse_property_title(self, entry):
        main = entry.get('tif:DublinCore', {})
        return main.get('dc:title', {}).get('#text')

    def _parse_property_description(self, entry):
        main = entry.get('tif:DublinCore', {})
        for description in main.get('dc:description', []):
            if description.get('@xml:lang') == self.lang:
                return description.get('#text')

    def _parse_property_website(self, entry):
        contacts = entry.get('tif:Contacts', {}).get('tif:DetailContact')

        if isinstance(contacts, list):
            for contact in contacts:
                persons = contact.get('tif:Adresses', {}) \
                                 .get('tif:DetailAdresse', {}) \
                                 .get('tif:Personnes', {}) \
                                 .get('tif:DetailPersonne')

                if isinstance(persons, dict):
                    persons = [persons]

                if isinstance(persons, list):
                    for person in persons:
                        media = person.get('tif:MoyensCommunications', {}) \
                                      .get('tif:DetailMoyenCom')
                        if isinstance(media, list):
                            for medium in media:
                                if medium['@type'] == CODE_WEBSITE:
                                    return medium.get('tif:Coord')

    def _parse_property_pictures(self, entry):
        pictures =  []
        for multimedia in entry.get('tif:Multimedia', {}) \
                               .get('tif:DetailMultimedia'):
            if multimedia['@type'] == CODE_IMAGE:
                picture = {
                    'url': multimedia['tif:URL'],
                    'copyright': multimedia['tif:Copyright']
                }
                pictures.append(picture)
        return pictures


tif2geojson = Converter()
