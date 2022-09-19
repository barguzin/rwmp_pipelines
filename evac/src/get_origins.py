####################
# author: barguzin #
# created: 9/9/22  #
####################

import geopandas as gpd
import pandas as pd
import sumolib 
import osmnx as ox
import numpy as np

def get_origins(netfile, origin_points, save_origin): 
    '''
    Finds edge_id in a SUMO net file that are closest to 
    places of residence on a map

    Args: 
        netfile - str - path to a stored SUMO net file 
        origin_points - str - path to geojson/shapefile with origins (places of residence)
        save_origin - str - path to save the file with closest edges to resid buildings 
    '''
    
    bld = gpd.read_file(origin_points)
    net = sumolib.net.readNet(netfile)

    all_dist = []
    all_edges = []
    all_ids = []

    lng, lat = bld.geometry.x, bld.geometry.y 

    radius=50 # meters

    xlon, xlat = net.convertLonLat2XY(lng, lat)

    for x,y in zip(xlon, xlat): 
        edges = net.getNeighboringEdges(x, y, radius)

        if len(edges) > 0: 
            distancesAndEdges = sorted([(dist, edge) for edge, dist in edges], key=lambda x: x[0])
            dist, closestEdge = distancesAndEdges[0]

            all_dist.append(dist)
            all_edges.append(closestEdge)
            all_ids.append(closestEdge.getID())

    
    # save to file
    # convert to pandas 
    df = pd.DataFrame(list(zip(all_ids, all_dist, all_edges)), columns=['id', 'dist', 'from_to'])
    print(df.shape)
    df.to_csv(save_origin)

def get_destinations(netfile, study_area, save_destination): 
    '''
    Finds edge_id in a SUMO net file that are closest to 
    places exits on major highways (OSM tags highway=primary|secondary|trunk|motorway)

    Args: 
        netfile - str - path to a stored SUMO net file 
        study_area - str - path to geojson/shapefile with study area
        save_destination - str - path to save the file with closest edges to resid buildings 
    '''

    # read SUMO net file 
    net = sumolib.net.readNet(netfile)
    # read study area 
    sa = gpd.read_file(study_area)
    sa.to_crs('epsg:4326', inplace=True)

    # construct an OSM graph based on studya area
    poly = sa.geometry.iloc[0]
    G = ox.graph_from_polygon(poly, network_type="drive_service") # include drive and service roads

    # extract nodes and edges from OSM graph
    nodes, edges = ox.graph_to_gdfs(G)

    # get exits
    exits = edges.loc[(edges.highway=='primary')|(edges.highway=='secondary')|(edges.highway=='motorway')|(edges.highway=='trunk')]
    print(exits.shape)

    all_dist = []
    all_edges = []
    all_ids = []

    lng, lat = exits.geometry.centroid.x, exits.geometry.centroid.y 

    radius=50 # meters

    xlon, xlat = net.convertLonLat2XY(lng, lat)

    for x,y in zip(xlon, xlat): 
        edges = net.getNeighboringEdges(x, y, radius)

        if len(edges) > 0: 
            distancesAndEdges = sorted([(dist, edge) for edge, dist in edges], key=lambda x: x[0])
            dist, closestEdge = distancesAndEdges[0]

            all_dist.append(dist)
            all_edges.append(closestEdge)
            all_ids.append(closestEdge.getID())

    # save to file
    # convert to pandas 
    df = pd.DataFrame(list(zip(all_ids, all_dist, all_edges)), columns=['id', 'dist', 'from_to'])
    print(df.shape)
    df.to_csv(save_destination)

def generate_s_curve(save_origin): 
    '''
    generate evacuation S-curve from Gaussian distribution
    '''
    # draw a sample from Gaussian distribution
    mu, sd = (12,12,12), (1,2,3)
    
    # read csv 
    df = pd.read_csv(save_origin)
    n = df.shape[0]

    # generate
    norm = np.random.normal(loc = mu, scale = sd, size=(n, 3))




def short_path(origin_points, exits):
    '''
    Generate shortest path routes/trips from origins and destinations 
    '''
    return 0 


def generate_OD(): 
    return 0      

if __name__ == "__main__":
    netfile = "C:/Users/barguzin/Documents/Github/rwmp_pipelines/study_area.net.xml"
    origin_points = "C:/Users/barguzin/Documents/Github/rwmp_pipelines/resid_centr_mc.geojson"
    save_origin = "C:/Users/barguzin/Documents/Github/rwmp_pipelines/close_resid_bldg.csv"
    save_destination = "C:/Users/barguzin/Documents/Github/rwmp_pipelines/exits_destinations.csv"
    study_area = "C:/Users/barguzin/Documents/Github/rwmp_pipelines/roadsevac_demo2_epsg26910.geojson"
    get_origins(netfile, origin_points, save_origin)
    get_destinations(netfile, study_area, save_destination)