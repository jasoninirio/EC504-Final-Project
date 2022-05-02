import overpy
import pandas as pd
import numpy as np
import requests
import json
import xmltodict
import os
from dotenv import load_dotenv
import heapq
import pprint
from yelp.client import Client
from tqdm import tqdm

load_dotenv()

'''
Find longtidude and latitude of location with the overpy api:
    - Decreases time needed to load API calls, but also produces an average of all locations surrounding cafes + libraries? (2 requests)

New method of approaching the query search to find distance based on current location, and using a radius based on a dictionary
of method of transportation:
    - Walking = 4825m
    - Car = MAX_VALUE (40,000m)
    - Bike = 12875m
    - Public = MAX_VALUE (40,000m)
    NOTE For Yelp-API: "The max value is 40000 meters (about 25 miles)."

Produce a max-min heap based on the equation: 
    ({num_of_reviews} / {average_star_review}) / {distance_to_location}
    NOTE distance_to_location is based on the yelp api, but can be changed by using best algorithm time using OSM

Create a Graph based on Nodes and Ways from OSM:
    Call Graph library and pass a dictionary of every node (Called from OSM) and every amenity
'''

class LocationsData():
    # urls and keys
    overpass_url = "http://overpass-api.de/api/interpreter"
    yelp_url = "https://api.yelp.com/v3/businesses/search"
    YELP_API_KEY = os.environ.get("YELP_API_KEY")

    # constants
    MAX_VALUE = 40000

    # data structures
    json_data = {
        'cafe': [],
        'library': [],
        'local_area': []
    }

    method_data = {
        'walking': 0,
        'bike': 0,
        'car': 0,
        'public': 0
    }

    def __init__(self, area, amenity, method):
        # assign values to each class variable
        self.area = area
        self.amenities = amenity
        self.methods = method

        # create key-value pair for each method of transportation
        self.method_data['walking'] = 4825
        self.method_data['bike'] = 12875
        self.method_data['car'] = self.MAX_VALUE
        self.method_data['public'] = self.MAX_VALUE

        print(f"Gathering nearby study spots based on {area}")
    
    def findNodes(self, amenity, allNodes=False, radius=0):
        # Finds all nodes via Overpass api call
        if allNodes:
            data_string = f"area[name={self.area}]->.a;(node(around.a:{radius});way(around.a:{radius}););out;"
        else:
            if amenity == 'cafe':
                data_string = f"area[name={self.area}]->.a;(node(area.a)[amenity={amenity}][cuisine='coffee_shop'];way(area.a)[amenity={amenity}][cuisine='coffee_shop'];rel(area.a)[amenity={amenity}][cuisine='coffee_shop'];);out;"
            else:
                data_string = f"area[name={self.area}]->.a;(node(area.a)[amenity={amenity}];way(area.a)[amenity={amenity}];rel(area.a)[amenity={amenity}];);out;"

        # Extract data based on location through overpass API
        res = requests.get(self.overpass_url, params={'data': data_string})
        obj = xmltodict.parse(res.content)
        # print(json.dumps(obj))
        return json.dumps(obj)

    def callOSM(self):
        # Calls Overpass API once to create a structure with it -> helps with timing if searching for same location
        # Find nearby amenities based on preferences and area selected
        for a in self.amenities:
            data = json.loads(self.findNodes(a))
            # Extract amenities to generate an average coordinate value (lon, lat)
            for d in tqdm(data['osm']['node']):
                node = {
                    'lat': d['@lat'],
                    'lon': d['@lon'],
                    'name': 'No Name',
                    'heap_value': 0
                }

                # check for name, if needed
                for tags in d['tag']:
                    if tags['@k'] == 'name':
                        node['name'] = tags['@v']
                
                # append to full json data under amenity name
                self.json_data[str(a)].append(node)

        # call Overpass API again, but with a {radius} around the area mentioned
        # radius is determined by max{methods}
        radius = 0
        for key in self.methods:
            radius = max(self.method_data[key], radius) # gets max radius

        # For local area
        data = json.loads(self.findNodes(None, allNodes=True, radius=radius))
        for d in tqdm(data['osm']['node']):
            node = {
                'lat': d['@lat'],
                'lon': d['@lon'],
            }
            
            # append to full json data under amenity name
            self.json_data['local_area'].append(node)

        for key in self.json_data.keys():
            df = pd.DataFrame(self.json_data[key])
            df.to_csv(f"LocationsDataOutput_{key}.csv")
        
    def callYelp(self):
        pass


    def assignHeapVal(self):
        # call yelp API to assign heap value
        # assign values based on the equation:  ({num_of_reviews} / {average_star_review}) / {distance_to_location}
        pass


if __name__ == '__main__':
    ld = LocationsData('Boston', ['cafe'], ['walking'])
    ld.callOSM()