# ----------------------- #
# author: @barguzin       # 
# Ars longa, vita brevis! #
# ----------------------- #

import geopandas as gpd 
import re
import urllib.parse 
import urllib.request

def overpass_query(txt_path, save_api_path, save_xml_path, save_xml=True): 
    '''
    Given a pre-formated wkt string, creates api call to Overpass API
        txt_path - path to file with  
    '''

    with open(txt_path, 'r') as f: 
        text_coords = f.read()

    # get coords from POLY 
    try: 
        s = re.findall('-?\d+.\d+', text_coords)
        s = " ".join(s)
        print(type(s))
        # print(s)
    except:
        print('no pattern detected in .txt')


    interpret = "http://overpass-api.de/api/interpreter?data="
    output_format = "[out:xml][timeout:100];"
    nodes = f'(node(poly:"{s}");'
    ways = f'way(poly:"{s}");'
    relations = f'relation(poly:"{s}");)'
    res = ";out;>;out skel qt;"

    url2 = output_format + nodes + ways + relations + res

    # encode 
    encoded = urllib.parse.quote_plus(url2)
    print(interpret + encoded)

    print(f'Saving Overpass API-call file to: {save_api_path}')
    with open(save_api_path, 'w') as f: 
        f.write(interpret + encoded)
        f.close()

    if save_xml: 
        urllib.request.urlretrieve(interpret + encoded, filename=save_xml_path)


def wkt_to_api(wkt):
    '''
    Converts a string with wkt geometry to polygon coordinates 
    suitable for calls to Overpass API 

    Args: 
        wkt - str - wkt geometry from geopandas / pygeos 
    '''

    coords = re.findall(r'-?\d+\.\d+', wkt)

    lng, lat = [],[]
    reversed = []
    flat = []

    for i in coords:
        #print(type(float(i)))
        if float(i)<0:
            lng.append(i)
        else: 
            lat.append(i)

    for i,j in zip(lng,lat): 
        reversed.append([j,i])

    flat = [item for sublist in reversed for item in sublist]

    s = ' '.join(flat) 

    return s

    

def prep_poly_geom(path_open, path_save, hull=False, reverse_coords=True): 
    '''
    Opens a shapefile with a polygon boundary 
    and saves wkt_geom to text file 

    IMPORTANT: the feature class must only have one feature (shape)! 

    IMPORTANT 2: the GeoPandas.to_wkt() returns lng/lat pair, which 
    needs to be revereted to lat/lng for Overpass API 

    args:
        path_open - str - dir with a shapefile 
        path_save - str - dir to save the txt to 
    '''

    gdf = gpd.read_file(path_open) 
    print('opened file with shape:', gdf.shape)

    # check if there is only one feazture in the data
    assert gdf.shape[0] == 1, "Feature class contains more than ONE geometry" 

    # reproject to GCS
    gdf = gdf.to_crs('epsg:4326')

    # multipolygons are messing geom calculations
    # here is the fix 
    gdf = gdf.explode(index_parts=False)

    if hull: 
        print('running convex hull version of the algorithm')
        geom = gdf.geometry.convex_hull.to_wkt()
    else: 
        # simplify to 100 meters
        print('running complete geometry version of the algorithm')
        #geom = gdf.geometry.simplify(0.000009).to_wkt()
        geom = gdf.geometry.to_wkt()
    
    # print(type(geom))

    # reproject back to GCS
    # gdf = gdf.to_crs('epsg:4326')

    text = geom[0]
    #print(text[0])
    #print(type(text))

    if reverse_coords:
        s = wkt_to_api(text)

    else:
        s = text
    
    print(f'Saving file to: {path_save}')
    with open(path_save, 'w') as f: 
        f.write(s)
        f.close()


if __name__=='__main__': 
    #path_open = 'C:/Users/barguzin/Documents/Github/rwmp_pipelines/rwmp_study_area.geojson'
    path_open = 'C:/Users/barguzin/Documents/Github/rwmp_pipelines/roadsevac_demo2_epsg26910.geojson' 
    path_save = 'C:/Users/barguzin/Documents/Github/rwmp_pipelines/rwmp_study_area.txt'
    save_api_path = 'C:/Users/barguzin/Documents/Github/rwmp_pipelines/overpass_api.txt'
    save_xml_path = 'C:/Users/barguzin/Documents/Github/rwmp_pipelines/study_area_osm'
    prep_poly_geom(path_open, path_save, hull=False, reverse_coords=True)
    overpass_query(path_save, save_api_path, save_xml_path)
