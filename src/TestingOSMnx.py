import osmnx as ox
import folium
import networkx as nx

place = "Boston"
'''
tags = {'amenity': 'cafe'}
cafe = ox.geometries_from_place(place, tags=tags)
print(cafe.head())

cafe.to_csv("TestingOSMnx.csv")
cafe_points = cafe[cafe.geom_type == 'Point'][:100]

m = folium.Map([-71.0, 42.3], zoom_start=10)
locs = zip(cafe_points.geometry.y, cafe_points.geometry.x)
for location in locs:
    folium.CircleMarker(location=location).add_to(m)
    m.save('cafes.html')
'''
G = ox.graph_from_place(place, network_type='drive')

nodes, streets = ox.graph_to_gdfs(G)
print(streets.columns)
print("streets")
print(streets.head())
print(streets.tail())

# print("nodes")
# print(nodes.head())
# print(nodes.tail())

# m1 = ox.plot_graph_folium(G, popup_attribute="name", weight=2, color="#8b0000")
# filepath="street.html"
# m1.save(filepath)

# print(type(G.nodes()))
# print(f"g nodes: {G.nodes()}")
# print(f"g streets: {list(G.edges())}")

origin_node = list(G.nodes())[0]

print(f"origin node: {origin_node}")

destination_node = list(G.nodes())[-1]

print(f"destination node: {destination_node}")

route = nx.shortest_path(G, origin_node, destination_node)
print(route)
# plot the route with folium
# like above, you can pass keyword args along to folium PolyLine to style the lines
m2 = ox.plot_route_folium(G, route, weight=10)
# save as html file then display map as an iframe
# filepath = "route.html"
# m2.save(filepath)

print("done")
