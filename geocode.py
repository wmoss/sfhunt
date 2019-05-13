import os, sys, urllib2, json, csv
from fastkml import kml, styles
from shapely.geometry import Point
from urllib import urlencode

with open('GOOGLE_API_KEY') as fp:
    PARAMETERS_BASE = {'key': fp.read() }
GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json?"

# Distance Matrix
# DISTANCE_MATRIX_URL = "https://maps.googleapis.com/maps/api/distancematrix/json?"
# PARAMETERS: origins, destinations, key, mode=bicycling

POINTS_TO_COLORS = {
    '5': 'grn',
    '10': 'ylw',
    '15': 'red',
    '20': 'wht',
    '25': 'orange',
}

CACHE = {}

def merge_dict(*args):
    result = {}
    for arg in args:
        result.update(arg)
    return result

def geocode(value):
    if value not in CACHE:
        req = GEOCODE_URL + urlencode(merge_dict(PARAMETERS_BASE, {'address': value}))
        response_handle = urllib2.urlopen(req)
        response = json.loads(response_handle.read())
        try:
            CACHE[value] = response["results"][0]["geometry"]["location"]
        except:
            raise "Failed to geocode '" + value "', response: " + str(response)

    return CACHE[value]

def run():
    k = kml.KML()
    ns = '{http://www.opengis.net/kml/2.2}'
    d = kml.Document(
        ns,
        None,
        'The Hunt 2019',
        'The Hunt 2019 Clues, on a map'
        )
    k.append(d)

    regular_folder = kml.Folder(name='Regular Clues')
    d.append(regular_folder)
    minihunt_folder = kml.Folder(name='Mini Hunts')
    d.append(minihunt_folder)

    # Potentially better icon
    # http://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png
    for color in POINTS_TO_COLORS.values():
        sty = styles.Style(id='miniHuntStyle_' + color)
        d.append_style(sty)

        sty.append_style(styles.IconStyle(
            icon_href="http://maps.google.com/mapfiles/kml/paddle/%s-stars.png" % color,
            color='ffff0000',
            ))

    for color in POINTS_TO_COLORS.values():
        sty = styles.Style(id='regularStyle_' + color)
        d.append_style(sty)

        sty.append_style(styles.IconStyle(
            icon_href="http://maps.google.com/mapfiles/kml/paddle/%s-blank.png" % color,
            ))

    with open(sys.argv[1]) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['Address']:
                latlng = geocode(row['Address'])

                p = kml.Placemark(ns, None, row['Answer'], None)

                p.geometry = Point(latlng['lng'], latlng['lat'])

                data = kml.ExtendedData()
                for field in ['Clue #','Clue','Answer','Address', 'Confidence', 'Point Value', 'Mini Hunt', 'Notes', 'Badge']:
                    data.elements.append(kml.Data(name=field, value=row[field]))
                p.extended_data = data

                if row['Mini Hunt'] == 'TRUE':
                    p.styleUrl = '#miniHuntStyle_' + POINTS_TO_COLORS[row['Point Value']]
                    minihunt_folder.append(p)
                else:
                    p.styleUrl = '#regularStyle_' + POINTS_TO_COLORS[row['Point Value']]
                    regular_folder.append(p)



    print k.to_string(prettyprint=True)

if __name__ == '__main__':
    if os.path.isfile('geocache.json'):
        with open('geoCACHE.json') as fp:
            CACHE.update(json.load(fp))

    try:
        run()
    finally:
        with open('geocache.json', 'w') as fp:
            json.dump(CACHE, fp)
