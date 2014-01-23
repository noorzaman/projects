import sys
import json
import requests

geoname_api_username = 'pheno@jonnymoon.com'

def get_lat_long_for_zip(zip_code):
    url = "http://api.geonames.org/findNearbyPostalCodesJSON?username=%s&country=US&postalcode=%s" % (geoname_api_username, zip_code)
    r = requests.get(url)
    data = r.json()
    if('status' in data and data['status']['value'] == 17):
        raise RuntimeError('Invalid ZIP code')
    lat = data["postalCodes"][0]['lat']
    lng = data["postalCodes"][0]['lng']
    return (float(lat), float(lng))

def get_zip_for_lat_long(lat, lng):
    url = "http://api.geonames.org/findNearbyPostalCodesJSON?username=%s&country=US&lat=%s&lng=%s" % (geoname_api_username, lat, lng)
    r = requests.get(url)
    data = r.json()
    if('status' in data and data['status']['value'] == 12):
        raise RuntimeError('Invalid coordinates')
    zip_code = data["postalCodes"][0]['postalCode']
    return str(zip_code)


def getForecast():
    if('lat' in params and 'lng' in params and params['lat'] != ''):
        coords = (params['lat'], params['lng'])
        zip_code = get_zip_for_lat_long(coords[0], coords[1])
    else:
        coords = get_lat_long_for_zip(params['zip_code'])
        zip_code = params['zip_code']


    result = [
        {'date': '2013-11-01', 'chance': 43, 'event': 'leaves budding', 'lat': coords[0], 'long': coords[1], 'zip_code': zip_code},
        {'date': '2013-11-02', 'chance': 52, 'event': 'leaves budding', 'lat': coords[0], 'long': coords[1], 'zip_code': zip_code},
        {'date': '2013-11-03', 'chance': 67, 'event': 'leaves budding', 'lat': coords[0], 'long': coords[1], 'zip_code': zip_code},
        {'date': '2013-11-04', 'chance': 73, 'event': 'leaves budding', 'lat': coords[0], 'long': coords[1], 'zip_code': zip_code},
        {'date': '2013-11-05', 'chance': 85, 'event': 'leaves budding', 'lat': coords[0], 'long': coords[1], 'zip_code': zip_code},
        {'date': '2013-11-06', 'chance': 93, 'event': 'leaves budding', 'lat': coords[0], 'long': coords[1], 'zip_code': zip_code},
        {'date': '2013-11-07', 'chance': 95, 'event': 'leaves budding', 'lat': coords[0], 'long': coords[1], 'zip_code': zip_code},
        {'date': '2013-11-08', 'chance': 86, 'event': 'leaves budding', 'lat': coords[0], 'long': coords[1], 'zip_code': zip_code},
        {'date': '2013-11-09', 'chance': 72, 'event': 'leaves budding', 'lat': coords[0], 'long': coords[1], 'zip_code': zip_code},
        {'date': '2013-11-10', 'chance': 61, 'event': 'leaves budding', 'lat': coords[0], 'long': coords[1], 'zip_code': zip_code},
    ]

    return {'days':result}

##########################################################
# Keep this bottom section at the bottom of the file
##########################################################

#sys.argv[0] # this is the file name
#sys.argv[1] # this is the variable passed from php

params = json.loads(sys.argv[1])
action = 'getForecast'; #default to getForecast if nothing is set
if('action' in params):
    action = params['action']

result = locals()[action]()
print(json.dumps(result))
#params['days'] = int(params['days']) + 10
#print(json.dumps(data)) this will return the input.