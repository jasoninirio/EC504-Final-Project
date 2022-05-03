from unittest import TestProgram
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
import osmnx as ox
import folium
import networkx as nx
from Graph import Graph

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
    # overpass_url = "http://overpass-api.de/api/interpreter"
    yelp_url = "https://api.yelp.com/v3/businesses/search"
    YELP_API_KEY = os.environ.get("YELP_API_KEY")

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

    def __init__(self, area, amenity, method, location=(42.3492, -71.1060)):
        # assign values to each class variable
        self.area = area
        self.amenities = amenity
        self.method = method
        self.location = location

        # create key-value pair for each method of transportation
        self.method_data['walk'] = 4500
        self.method_data['bike'] = 5000
        self.method_data['car'] = self.MAX_VALUE

        print(f"Gathering nearby study spots based in {area}")
    
    def findLocalAmenity(self):
        # find max radius for yelp api
        # gets max radius
        radius = self.method_data[self.method]
        
        print(f"Radius is: {radius}")

        headers = {'Authorization': 'Bearer {}'.format(self.YELP_API_KEY)}
        params = {
            'latitude': self.location[0],
            'longitude': self.location[1],
            'radius': radius,
            'categories': 'coffee, internetcafe, cafes'
        }
        res = requests.get(self.yelp_url, headers=headers, params=params)
        data = json.loads(res.content)
        # print("Local Amenities")
        # print(res.content)

        index = 0
        maxValue = 0
        currNode = None
        for d in tqdm(data['businesses']):
            # using equation for finding best result: max{({review_count} / {rating}) / distance}
            val = ((d['review_count'] / d['rating']) / d['distance'])
            if val > maxValue:
                currNode = {
                    'latitude': d['coordinates']['latitude'],
                    'longitude': d['coordinates']['longitude'],
                    'name': d['name'],
                    'address': d['location']['address1'],
                    'zipcode': d['location']['zip_code'],
                    'city': d['location']['city'],
                    'state': d['location']['state']
                }
        
        # check if any nodes were found
        if currNode == None:
            print("no amenities found - sorry :(")
            return None
        else:
            return currNode
    
    def createBBox(self, target):
        # creates a bbox around the target node and starting location
        # uses an equation for expanding the box to narrow space and time complexity (but could limit some traveling options)
        deltaLat = abs(self.location[0] - target['latitude'])
        deltaLong = abs(self.location[1] - target['longitude'])

        north = max(self.location[0], target['latitude'])
        south = min(self.location[0], target['latitude'])
        east = max(self.location[1], target['longitude'])
        west = min(self.location[1], target['longitude'])

        # set bbox to be from north, south, west, east
        self.bbox = [
            north + deltaLat,
            south - deltaLat,
            east + deltaLong,
            west - deltaLong
        ]
    
    def callOSM(self):
        # Calls the OSMnx API to create a graph bounded by the target and starting node's coordinates
        # Allows for an easier and quicker way of finding places!

        self.StudySpotGraph = ox.graph.graph_from_bbox(self.bbox[0], self.bbox[1], self.bbox[2], self.bbox[3], network_type=self.method)
        # nodes, streets = ox.graph_to_gdfs(self.StudySpotGraph)

        # print("streets")
        # print(streets.head())
        # print(streets.tail())

        # print("nodes")
        # print(nodes.head())
        # print(nodes.tail())

        # m1 = ox.plot_graph_folium(self.StudySpotGraph, popup_attribute="name", weight=2, color="#8b0000")
        # filepath="studyspots.html"
        # m1.save(filepath)

if __name__ == '__main__':
    ld = LocationsData('Boston', ['cafe'], 'walk')
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

    path, dist = testGraph.Dijkstra(source, target)
    print(f"Path:\n{path}\nDistance:\t{dist}")
