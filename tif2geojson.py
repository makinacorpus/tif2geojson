from xml.parsers.expat import ExpatError

import geojson
import xmltodict


DEFAULT_LANGUAGE = 'EN'
SUPPORTED_PROPERTIES = ['title', 'description', 'pictures', 'website']

CODE_WEBSITE = '04.02.05'
CODE_IMAGE = '03.01.01'


class Converter(object):
    def __init__(self):
        self.content = ''
        self.properties = None
        self.lang = DEFAULT_LANGUAGE

    def __call__(self, content, properties=None, lang=None):
        self.content = content
        self.properties = properties if properties else SUPPORTED_PROPERTIES
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
        geometry = self._parse_location(entry)
        properties = self._parse_properties(entry)
        return geojson.Feature(geometry=geometry, properties=properties)

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
        for prop in self.properties:
            properties[prop] = None

        main = entry.get('tif:DublinCore', {})

        if 'title' in self.properties:
            properties['title'] = main.get('dc:title', {}).get('#text')

        if 'description' in self.properties:
            for description in main.get('dc:description', []):
                if description.get('@xml:lang') == self.lang:
                    properties['description'] = description.get('#text')

        if 'website' in self.properties:
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
                                        properties['website'] = medium.get('tif:Coord')

        if 'pictures' in self.properties:
            pictures =  []
            for multimedia in entry.get('tif:Multimedia', {}) \
                                   .get('tif:DetailMultimedia'):
                if multimedia['@type'] == CODE_IMAGE:
                    picture = {
                        'url': multimedia['tif:URL'],
                        'copyright': multimedia['tif:Copyright']
                    }
                    pictures.append(picture)
            properties['pictures'] =  pictures

        return properties


tif2geojson = Converter()
