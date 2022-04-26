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
'''

class LocationsData():
    overpass_url = "http://overpass-api.de/api/interpreter"
    yelp_url = "https://api.yelp.com/v3/businesses/search"
    YELP_API_KEY = os.environ.get("YELP_API_KEY")
    def __init__(self, area, amenity):
        self.area = area
        self.amenity = amenity
        print(f"Gathering nearby study spots based on {area}")

    def convertArea(self):
        # Find nearby amenities based on preferences and area selected
        for a in self.amenity:
            if a == 'cafe':
                data_string = f"area[name={self.area}]->.a;(node(area.a)[amenity={a}][cuisine='coffee_shop'];way(area.a)[amenity={a}][cuisine='coffee_shop'];rel(area.a)[amenity={amenity}][cuisine='coffee_shop'];);out;"
            else:
                data_string = f"area[name={self.area}]->.a;(node(area.a)[amenity={a}];way(area.a)[amenity={a}];rel(area.a)[amenity={a}];);out;"
    
            params={'data':data_string}
            # Extract location to generate an average coordinate value (lon, lat)
            res = requests.get(self.overpass_url, params=params)
            raw_data = xmltodict.parse(res.content)
            data = json.dumps(raw_data)

            # TODO for d in data
    
    def callYelp(self):
        pass


    def heapVal(self):
        pass