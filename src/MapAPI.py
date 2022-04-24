# Calls API for information about the local area based on information given

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

load_dotenv()

class QueryData:
    query_url = "http://overpass-api.de/api/interpreter"
    heap = []

    def __init__(self, area, amenity, method):
        # Gathers user inputted information
        self.AREA = area
        self.AMENITY = amenity
        self.METHOD = method
        print("Gathering Information...")
    
    def findNearAmenities(self, amenity):
        # Finds nearby amenities via overpy api call
        if amenity == 'cafe':
            data_string = f"area[name={self.AREA}]->.a;(node(area.a)[amenity={amenity}][cuisine='coffee_shop'];way(area.a)[amenity={amenity}][cuisine='coffee_shop'];rel(area.a)[amenity={amenity}][cuisine='coffee_shop'];);out;"
        else:
            data_string = f"area[name={self.AREA}]->.a;(node(area.a)[amenity={amenity}];way(area.a)[amenity={amenity}];rel(area.a)[amenity={amenity}];);out;"

        # Extract data based on location
        res = requests.get(self.query_url, params={'data': data_string})
        obj = xmltodict.parse(res.content)
        # print(json.dumps(obj))
        return json.dumps(obj)

    def createAmenityData(self):
        # TODO add an iterative list for data for libraries and cafes
        for a in self.AMENITY:
            data = json.loads(self.findNearAmenities(a))
        nodelist = []

        # create DataFrame from raw json data
        for d in data['osm']['node']:
            node = {'lat':d['@lat'],
                    'lon':d['@lon'],
                    'name':'No Name',
                    'value':0}
            # TODO convert data to have a key-value pair, where the max-min heap will be able to keep track of value + name of amenity.
            # check if name exists 
            for tags in d['tag']:
                if tags['@k'] == 'name':
                    node['name']=tags['@v']

            nodelist.append(node)
        
        df = pd.DataFrame(nodelist) # for geoPandas(?)
        df.to_excel('NodeOutputData.xlsx')
        # print(df)

if __name__ == '__main__':
    q = QueryData('Boston', ['cafe'], ['walking'])
    # q.findNearAmenities()
    q.createAmenityData()


# TODO add a radius based on the city
# TODO order every amenity around the area via pandas dataframe
# TODO use a Max-Min Heap for listing the areas and their values? Sort them based on the equation: max first {num_of_reviews} / {star_review_number} 
