import overpy
import pandas as pd
import numpy as np
import requests
import json
import os
from dotenv import load_dotenv
import heapq
import pprint
from yelp.client import Client
from tqdm import tqdm
import osmnx as ox
import folium
import networkx as nx
from src.Graph import Graph
from geopy.geocoders import Nominatim

load_dotenv()

'''
Find longtidude and latitude of location with the overpy api:
    - Decreases time needed to load API calls, but also produces an average of all locations surrounding cafes + libraries? (2 requests)

New method of approaching the query search to find distance based on current location, and using a radius based on a dictionary
of method of transportation:
    - Walking = 4825m
    - Car = MAX_VALUE (10,000m)
    - Bike = 12875m
    NOTE For Yelp-API: "The max value is 40000 meters (about 25 miles)."

Produce a max-min heap based on the equation: 
    ({num_of_reviews} / {average_star_review}) / {distance_to_location}
    NOTE distance_to_location is based on the yelp api, but can be changed by using best algorithm time using OSM

Create a Graph based on Nodes and Ways from OSM:
    Call Graph library and pass a dictionary of every node (Called from OSM) and every amenity
'''

class LocationsData():
    # urls and keys
    # overpass_url = "http://overpass-api.de/api/interpreter"
    yelp_url = "https://api.yelp.com/v3/businesses/search"
    YELP_API_KEY = 'WNgMAbFZaTpl301U15VWKbezoCefoxQhvG3tNEJhcNWL6j8Bf2POdJb6BWxNs58ULttWeWiwjunPJ3ctIMDcWaiv4WiqTXNBJUPTkDu5HeWhrEg1pAw7gCnIcNdxYnYx'

    # constants
    MAX_VALUE = 10000

    # data structures
    json_data = {
        'cafe': [],
        'library': [],
        'local_area': []
    }

    method_data = {
        'walk': 0,
        'bike': 0,
        'drive': 0,
    }

    rejected = []

    def __init__(self, area, amenity, method, location=(42.3492, -71.1060)):
        # assign values to each class variable
        self.area = area
        self.amenities = amenity

        # convert method to match OSMnx
        _method = ""
        if method == 'Car': _method = 'drive'
        if method == 'Bike': _method = 'bike'
        if method == 'Walking': _method = 'walk'

        self.method = _method

        # finding location based on latitude, longitude with geopy
        locator = Nominatim(user_agent="StudySpot")
        geolocation = locator.geocode(location)

        self.location = (geolocation.latitude, geolocation.longitude)

        # create key-value pair for each method of transportation
        self.method_data['walk'] = 4500
        self.method_data['bike'] = 5000
        self.method_data['car'] = self.MAX_VALUE

        print(f"Gathering nearby study spots all around {area}!")
    
    def findLocalAmenity(self, rejectedNode=None):
        # find best local amenity with yelp API
        if rejectedNode != None:
            self.rejected.append(rejectedNode['address']) # keep track of rejected nodes

        # gets max radius
        radius = self.method_data[self.method]
        
        # print(f"Radius is: {radius}")

        headers = {'Authorization': 'Bearer {}'.format(self.YELP_API_KEY)}
        
        # finding amenities based on search
        if self.amenities == 'Cafe':
            params = {
                'latitude': self.location[0],
                'longitude': self.location[1],
                'radius': radius,
                'categories': 'coffee, internetcafe, cafes'
            }
        
        elif self.amenities == 'Library':
            params = {
                'latitude': self.location[0],
                'longitude': self.location[1],
                'radius': radius,
                'categories': 'libraries'
            }
        
        else:
            params=None
        
        res = requests.get(self.yelp_url, headers=headers, params=params)
        data = json.loads(res.content)

        # query through nearby business from yelp API
        index = 0
        maxValue = 0 
        currNode = None
        prevNode = None
        for d in data['businesses']:
            # using equation for finding best result: max{({review_count} / {rating}) / distance}
            val = ((d['review_count'] / d['rating']) / d['distance'])
            if val > maxValue:
                if currNode != None:
                    prevNode = currNode
                
                currNode = {
                    'latitude': d['coordinates']['latitude'],
                    'longitude': d['coordinates']['longitude'],
                    'name': d['name'],
                    'address': d['location']['address1'],
                    'zipcode': d['location']['zip_code'],
                    'city': d['location']['city'],
                    'state': d['location']['state']
                }
                if rejectedNode != None and currNode['address'] in self.rejected:
                    currNode = prevNode
        
        # check if any nodes were found
        if currNode == None:
            print("no amenities were found - sorry :(")
            return None
        else:
            print(f"Found {currNode['name']}!")
            return currNode
    
    def createBBox(self, target):
        # creates a bbox around the target node and starting location
        # uses an equation for expanding the box to narrow space and time complexity (but could limit some traveling options)
        deltaLat = abs(self.location[0] - target['latitude'])
        deltaLong = abs(self.location[1] - target['longitude'])
        multi = 1

        north = max(self.location[0], target['latitude'])
        south = min(self.location[0], target['latitude'])
        east = max(self.location[1], target['longitude'])
        west = min(self.location[1], target['longitude'])

        # set bbox to be from north, south, west, east by 2x the delta
        self.bbox = [
            north + (multi * deltaLat),
            south - (multi * deltaLat),
            east + (multi * deltaLong),
            west - (multi * deltaLong)
        ]
    
    def callOSM(self):
        # Calls the OSMnx API to create a graph bounded by the target and starting node's coordinates
        # Allows for an easier and quicker way of finding places!
        print("Creating OSMnx Graph Object!")
        self.StudySpotGraph = ox.graph.graph_from_bbox(self.bbox[0], self.bbox[1], self.bbox[2], self.bbox[3], truncate_by_edge=True, network_type=self.method)

    def planRoute(self, path, name):
        #ox.plot.plot_graph_route(self.StudySpotGraph, path, route_color='r')
        map = ox.plot_route_folium(self.StudySpotGraph, path, weight=10)
        filepath = "Routes/"
        if not os.path.exists(filepath):
            os.makedirs(filepath)

        map.save(f"{filepath}StudySpotRoute_{name}.html")
        print(f"Generated html file!\nLook for filename StudySpotRoute_{name}.html in the Routes folder!")

# Debugging
if __name__ == '__main__':
    ld = LocationsData('Boston', 'Cafe', 'Walking', "8 St Mary's St, Boston, MA 02215")
    testnode = ld.findLocalAmenity()

    print("Test Node")
    if testnode != None:
        for keys in testnode.keys():
            print(f"{keys} : {testnode[keys]}")
    ld.createBBox(testnode)
    ld.callOSM()
    
    testGraph = Graph(ld.StudySpotGraph)
    target = testGraph.findNearestNode(testnode['latitude'], testnode['longitude'])
    source = testGraph.findNearestNode(ld.location[0], ld.location[1])

    print(f"Source:\t{source}\nTarget:\t{target}")

    path = testGraph.Dijkstra(source, target)
    print(f"Path:\n{path}")

    ld.planRoute(path, testnode['name'])
