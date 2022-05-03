# A graph library created from OSM nodes and ways
# Edges - Ways
# Vertices - Nodes
from tkinter import S
import numpy as np
import pandas as pd
import requests
import xmltodict
import json
import networkx as nx
from MapAPI import QueryData as qd
import sys

class Graph:
    def __init__(self):
        print("Creating Graph Class")
    
    # for testing purposes
    def createGraph(self):
        self.G = nx.Graph()
        self.G.add_edge(0,1,weight=4)
        self.G.add_edge(0,7,weight=8)
        self.G.add_edge(1,7,weight=11)
        self.G.add_edge(1,2,weight=8)
        self.G.add_edge(2,8,weight=2)
        self.G.add_edge(7,8,weight=7)
        self.G.add_edge(8,6,weight=6)
        self.G.add_edge(7,6,weight=1)
        self.G.add_edge(6,5,weight=2)
        self.G.add_edge(5,4,weight=10)
        self.G.add_edge(3,4,weight=9)
        self.G.add_edge(2,5,weight=4)
        self.G.add_edge(3,5,weight=14)
        self.G.add_edge(2,3,weight=7)

    def Dijkstra(self,source,target):
        # source, target are IDs referring to nodes in the graph 
        unmarked_nodes = list(self.G.nodes)
        dist = {} # shortest path
        pred = {} # predecessor matrix
        max_value = sys.maxsize
        for node in unmarked_nodes:
            dist[node] = max_value # initialize all distances as infinity
        dist[source] = 0

        while(unmarked_nodes):
            currmin = None
            for node in unmarked_nodes:
                if currmin == None:
                    currmin = node
                elif dist[node] < dist[currmin]:
                    currmin = node

            neighbors = list(self.G.adj[currmin])
            for neighbor in neighbors:
                val = dist[currmin] + self.G[currmin][neighbor]['weight']
                if val < dist[neighbor]:
                    dist[neighbor] = val
                    pred[neighbor] = currmin
            unmarked_nodes.remove(currmin)

        # find path to target
        path = []
        node = target
        while node != source:
            path.append(node)
            node = pred[node]
        path.append(source)
        mindist = 0
        for i in range(len(path)-1):
            mindist += self.G[path[i]][path[i+1]]['weight']

        return path, mindist

if __name__ == '__main__':
    mygraph = Graph()
    mygraph.createGraph()
    out,dist = mygraph.Dijkstra(0,3)   


