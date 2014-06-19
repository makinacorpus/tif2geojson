from xml.parsers.expat import ExpatError

import geojson
import xmltodict


DEFAULT_LANGUAGE = 'EN'
SUPPORTED_PROPERTIES = ['title', 'description', 'category',
                        'pictures', 'website', 'phone']

CODE_WEBSITE = '04.02.05'
CODE_IMAGE = '03.01.01'
CODE_PHONE = '04.02.01'
CODE_MAIN_CONTACT = '04.03.13'


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
        entries = _deep_value_list(parsed, 'listeOI',
                                           'OIs',
                                           'tif:OI')
        features = []
        for entry in entries:
            feature = self._parse_entry(entry)
            features.append(feature)
        return features

    def _parse_entry(self, entry):
        id_ = _deep_value(entry, 'tif:DublinCore',
                                 'dc:identifier')
        geometry = self._parse_location(entry)
        properties = self._parse_properties(entry)
        return geojson.Feature(id=id_,
                               geometry=geometry,
                               properties=properties)

    def _parse_location(self, entry):
        """
        Return the **first** location as `geojson.Point`.
        """
        locations = _deep_value_list(entry, 'tif:Geolocalisations')
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
            lat = float(coords.get('tif:Latitude', 0))
            lng = float(coords.get('tif:Longitude', 0))
            altitude = float(coords.get('tif:Altitude', 0))
            coords = [lng, lat, altitude]
            return geojson.Point(coords)

        return None

    def _parse_properties(self, entry):
        properties = {}
        for prop in SUPPORTED_PROPERTIES:
            if self.properties is None or prop in self.properties:
                method = getattr(self, '_parse_property_%s' % prop)
                properties[prop] = method(entry)
        return properties

    def _parse_property_category(self, entry):
        category = _deep_value(entry, 'tif:DublinCore',
                                      'tif:Classification')
        return {
            'id': category.get('@code'),
            'label': category.get('#text')
        }

    def _parse_property_title(self, entry):
        title = _deep_value(entry, 'tif:DublinCore', 'dc:title')
        if isinstance(title, dict):
            # If has attribute like xml:lang
            title = title.get('#text')
        return title

    def _parse_property_description(self, entry):
        descriptions = _deep_value_list(entry, 'tif:DublinCore',
                                               'dc:description',
                                               default=[])
        for description in descriptions:
            desc_language = description.get('@xml:lang', '').lower()
            if self.lang.lower().startswith(desc_language):
                return description.get('#text')

    def _parse_communication_media(self, entry, contact_type=None):
        contacts = _deep_value_list(entry, 'tif:Contacts',
                                           'tif:DetailContact')

        for contact in contacts:
            if contact and contact.get("@type") != contact_type:
                continue

            adresses = _deep_value_list(contact, 'tif:Adresses',
                                                 'tif:DetailAdresse')
            for address in adresses:
                if address:
                    persons = _deep_value_list(address, 'tif:Personnes',
                                                        'tif:DetailPersonne')
                    for person in persons:
                        media = _deep_value(person, 'tif:MoyensCommunications',
                                                    'tif:DetailMoyenCom')
                        return media
        return []

    def _parse_property_website(self, entry):
        media = self._parse_communication_media(entry,
                                                contact_type=CODE_MAIN_CONTACT)
        for medium in media:
            is_website = (isinstance(medium, dict) and
                          medium.get('@type') == CODE_WEBSITE)
            if is_website:
                return medium.get('tif:Coord')

    def _parse_property_phone(self, entry):
        media = self._parse_communication_media(entry,
                                                contact_type=CODE_MAIN_CONTACT)
        for medium in media:
            if isinstance(medium, dict) and medium.get('@type') == CODE_PHONE:
                return medium.get('tif:Coord')

    def _parse_property_pictures(self, entry):
        multimedia = _deep_value_list(entry, 'tif:Multimedia',
                                             'tif:DetailMultimedia')
        pictures = []
        for medium in multimedia:
            if isinstance(medium, dict) and medium.get('@type') == CODE_IMAGE:
                url = medium.get('tif:URL')
                if not url:
                    continue
                picture = {
                    'url': url,
                    'copyright': medium.get('tif:Copyright', '')
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


def _deep_value_list(*args, **kwargs):
    val = _deep_value(*args, **kwargs)
    if val and not isinstance(val, list):
        val = [val]
    return val


tif2geojson = Converter()


if __name__ == '__main__':
    import sys
    import fileinput
    import json

    content = ''.join(fileinput.input())
    result = tif2geojson(content)
    sys.stdout.write(json.dumps(result) + "\n")
