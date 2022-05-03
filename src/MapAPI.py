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

class QueryData:
    query_url = "http://overpass-api.de/api/interpreter"
    yelp_url = "https://api.yelp.com/v3/businesses/search"
    YELP_API_KEY = os.environ.get("YELP_API_KEY")
    heap = []

    def __init__(self, area, amenity, method):
        # Gathers user inputted information
        self.AREA = area
        self.AMENITY = amenity
        self.METHOD = method
        # self.client = Client(os.environ.get("YELP_API_KEY"))
        print("Gathering Information...")
    
    def callYelp(self, lon, lat, name, radius):
        headers = {'Authorization': 'Bearer {}'.format(self.YELP_API_KEY)}
        params = {
            'latitude':lat,
            'longitude':lon,
        }
        print(f"On Location {name}")
        res = requests.get(self.yelp_url, headers=headers, params=params)
        return res.content
    
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
        # TODO load API call once, then run a continuous loop using a max-min heap structure to avoid overusing the API calls?
        nodelist = []
        yelplist = []

        for a in ['cafe', 'library']:
            data = json.loads(self.findNearAmenities(a))

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
        df.to_csv('NodeOutputData.csv')
        # print(df)

        # TODO call yelp API to gather reviews to match into max-min heap
        # EXAMPLE: GET https://api.yelp.com/v3/autocomplete?text=del&latitude=37.786882&longitude=-122.399972

        # Testing YELP
        print('Testing yelp api')
        for index, row in df.iterrows():
            # print(f"{row['name']}: {row['lat']}, {row['lon']}")
            yelplist.append(self.callYelp(row['lat'], row['lon'], row['name']))
        
        print(f"length of yelplist: {len(yelplist)}")


if __name__ == '__main__':
    q = QueryData('Boston', ['cafe'], ['walking'])
    q.createAmenityData()


# TODO add a radius based on the city
# TODO order every amenity around the area via pandas dataframe
# TODO use a Max-Min Heap for listing the areas and their values? Sort them based on the equation: max first {num_of_reviews} / {star_review_number} 
