#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import osmnx as ox
import networkx as nx
import folium
import geopy
from geopy.geocoders import Nominatim
from transliterate import translit

def Find_path(x1,y1,x2,y2,city,country,optim_param):

    ox.config(log_console=True, use_cache=True)

    # define the start and end locations in latlng
    start_latlng = (x1,y1)
    end_latlng = (x2,y2)

    # location where you want to find your route
    place = f'{city},{country}'

    # find shortest route based on the mode of travel
    mode = 'walk' # 'drive', 'bike', 'walk'

    # find shortest path based on distance or time
    optimizer = f'{optim_param}' # 'length','time'

    # create graph from OSM within the boundaries of some 
    # geocodable place(s)
    graph = ox.graph_from_place(place, network_type = mode)

    # find the nearest node to the start location
    orig_node = ox.get_nearest_node(graph, start_latlng)

    # find the nearest node to the end location
    dest_node = ox.get_nearest_node(graph, end_latlng)

    # find the shortest path
    shortest_route = nx.shortest_path(graph, orig_node,dest_node,
                                      weight=optimizer)
    return graph,shortest_route


# In[ ]:


def map_shower(graph,shortest_route):
    shortest_route_map = ox.plot_route_folium(graph, shortest_route)
    shortest_route_map


# In[ ]:


def geo_lock_coord(ad):
    geolocator = Nominatim(user_agent = 'cum')
    name = ad #translit(ad, 'ru', reversed=True)
    location = geolocator.geocode(name, exactly_one =True)
    return location.latitude,location.longitude



# In[ ]:


user_input = input("Введите(скажите) свой адрес расположения(Город и улица):")
l1,w1 = geo_lock_coord(user_input)

user_destination = input("Введите(скажите) куда бы вы хотели прогуляться(Город и улица/):")
l2,w2 = geo_lock_coord(user_input)
how_to_go = input("Вы бы хотели дойти до финиша как можно _быстрее_ или хотели бы _прогуляться_?")

if how_to_go == 'время':  ## тут надо синонимы ко времени подобрать
    how_to_go = 'time'
else:
     how_to_go = 'length'

g,sh_r = Find_path(l1,w1,l2,w2,translit(user_input.split()[0], 'uk', reversed=True),"Russia",how_to_go)


# In[ ]:


map_shower(g,sh_r)

