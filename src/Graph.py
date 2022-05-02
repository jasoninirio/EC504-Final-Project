# A graph library created from OSM nodes and ways
# Edges - Ways
# Vertices - Nodes
import numpy as np
import pandas as pd
import requests
import xmltodict
import json
import networkx as nx

class Graph:
    def __init__(self, amenity):

        print("Creating Graph Class")
    
    def createGraph(self):
        self.G = nx.Graph()

