# Calls API for information about the local area based on information given

import overpy
import pandas as pd
import requests
import json
import xmltodict

AREA = "Boston"
AMENITY = "cafe"

query_url = "http://overpass-api.de/api/interpreter"

data_string = f"area[name={AREA}]->.a;(node(area.a)[amenity={AMENITY}];way(area.a)[amenity={AMENITY}];rel(area.a)[amenity={AMENITY}];);out;"

# Extract data based on location
res = requests.get(query_url, params={'data': data_string})
obj = xmltodict.parse(res.content)
print(json.dumps(obj))

# TODO order every amenity around the area via pandas dataframe