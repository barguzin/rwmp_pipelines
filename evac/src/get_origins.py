####################
# author: barguzin #
# created: 9/9/22  #
####################

import geopandas as gpd
import pandas as pd
import sumolib 

def get_origins(netfile, origin_points, save_csv): 
    '''
    Finds edge_id in a SUMO net file that are closest to 
    places of residence on a map

    Args: 
        netfile - str - path to a stored SUMO net file 
        origin_points - str - path to geojson/shapefile with origins (places of residence)
        save_csv - str - path to save the file with closest edges to resid buildings 
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
    df.to_csv(save_csv)
     

if __name__ == "__main__":
    netfile = "C:/Users/barguzin/Documents/Github/rwmp_pipelines/study_area.net.xml"
    origin_points = "C:/Users/barguzin/Documents/Github/rwmp_pipelines/resid_centr_mc.geojson"
    save_csv = "C:/Users/barguzin/Documents/Github/rwmp_pipelines/close_resid_bldg.csv"
    get_origins(netfile, origin_points, save_csv)