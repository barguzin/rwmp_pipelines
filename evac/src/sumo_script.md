# Pre-requisites 
1. Install the latest version of ECLIPSE SUMO 
2. Add SUMO to the PATH by editing system variables (otherwise python scripts will not run unless you navigate to those directories)

# Creating working directory 
1. Create folder for sumo project the following code was executed and tested in Anaconda command line on Windows 10 

```{bash}
cd C:\
mkdir sumo
cd sumo
```
2. Move the shapefile with study 

3. Reproject original demo file into epsg:4326. Make sure to specify paths according to where the files are stored and run these in GDAL command line (if on Windows) 

```{bash}
ogr2ogr evac_demo.geojson -t_srs "EPSG:4326" roadsevac_demo2_epsg26910.geojson

```

4. Download OSM data for study area 

```{bash}
cd sumo_sim/data
python "C:\Program Files (x86)\Eclipse\Sumo\tools\osmGet.py" --polygon evac_demo.geojson 
```
> this tool returns 400-Bad Request with polygon. Try bbox: 

```{bash}
python "C:\Program Files (x86)\Eclipse\Sumo\tools\osmGet.py" --bbox "-119.731015, 34.445925, -119.704025, 34.465305"
```

> this returns 504-Gateway Timeout (need to check if this is related to public Wi-Fi settings). This works sometimes (different PC)

5. Altenatively, use script that I wrote to download data using Overpass API that does not depend on SUMO API. **Make sure to change all of the paths in the python script.** 
```{bash}
cd rwmp_pipelines
python get_osm_by_poly.py 
```

> plotting this network is troublesome (Goole wrote their own code of >300 lines). The PyPI package I tried (SumoNetVis) did not work with OSM formatted file. 


6. Convert downloaded OSM data into a SUMO network (using recommended options)
```{bash}
netconvert --osm-files study_area.osm.xml -o study_area.net.xml --type-files "C:\Program Files (x86)\Eclipse\Sumo\data\typemap\osmNetconvert.typ.xml" --geometry.remove --ramps.guess --junctions.join --tls.guess-signals --tls.discard-simple --tls.join --tls.default-type actuated --remove-edges.isolated
```

> Or run this on WSL 

```{bash}
netconvert --osm-files study_area.osm.xml -o study_area.net.xml --type-files /usr/share/sumo/data/typemap/osmNetconvert.typ.xml --geometry.remove --ramps.guess --junctions.join --tls.guess-signals --tls.discard-simple --tls.join --tls.default-type actuated --remove-edges.isolated
```

7. Generate TAZs(polygons) by buffering exit roads (10m) and creating a convex hull of points for residential buildings. Then run polyconvert tool. As far as I understand there is no need to run the polyconvert twice. From examples and tutorials online those could be coming from one file. 
```{bash}
polyconvert -n study_area.net.xml --shapefile-prefixes exit_taz --shapefile.guess-projection --shapefile.traditional-axis-mapping -o converted.exit.xml
```
> This fails on windows returning *pj_obj_create: C:\Users\barguzin\Anaconda3\Library\share\proj\proj.db lacks DATABASE.LAYOUT.VERSION.MAJOR / DATABASE.LAYOUT.VERSION.MINOR metadata. It comes from another PROJ installation.*. Trying this under WSL. Install SUMO on WSL next time. Or try drawing them.  

> The command runs fine under the WSL 

```{bash}
polyconvert -n study_area.net.xml --shapefile-prefixes bld_taz --shapefile.guess-projection  --shapefile.traditional-axis-mapping -o converted.origs.xml
```

> Try combining two shapefiles and feed it to SUMO at once. And assign edges to TAZs. 

```{bash}
polyconvert -n study_area.net.xml --shapefile-prefixes merged_taz --shapefile.guess-projection  --shapefile.traditional-axis-mapping -o converted.merged.xml

python3 /usr/share/sumo/tools/edgesInDistricts.py -n study_area.net.xml -t converted.merged.xml
```

<!-- 8. Assign edges to each TAZ via SUMO Python tool. The paths are for Ubuntu on WSL. This generates file 'districts.taz.xml' 
```{bash}
cd /mnt/c/Users/barguzin/Documents/Github/rwmp_pipelines
python3 /usr/share/sumo/tools/edgesInDistricts.py -n study_area.net.xml -t converted.exit.xml,converted.origs.xml
``` -->

> I dissolved the exits so that there is only one TAZ for all corresponding exits. Now the districts.taz.xml looks incorrect. Perhaps this happens because these TAZ overlap. Might need to run 'difference' before processing this further. 

9. Try importing test OD matrix to see if it works. 
```{bash}
od2trips -c od2trips.config.xml -n study_area.net.xml, districts.taz.xml -d od_test.od -o trips
```

10. To-do: try running findAllRoutes.py and feed it 1) net file; 2) source-edges; 3) target-edge; outputting a file. See more info [here](https://github.com/eclipse/sumo/blob/main/tools/findAllRoutes.py). 

If running on a Windows machine. 
```{bash}
python "C:/Program Files (x86)/Eclipse/Sumo/tools/findAllRoutes.py" -n study_area.net.xml -o routes.xml -s -16262970\#1,-679909983\#0,616970620,16253433\#1 -t "-627887423#5","-886568238#0","627887423#4","-16263932#1"
```

If running on a Linux machine. 
```{bash}
python3 /usr/share/sumo/tools/findAllRoutes.py -n study_area.net.xml -o routes.xml -s "-16262970#1,-679909983#0,616970620,16253433#1" -t ["-627887423#5","-886568238#0","627887423#4","-16263932#1"]
```

> I tried running this under different configurations, but was not successful. There is something wrong with how the list argument is parsed by argparser. When feeding the comma separated list of source edges in double quotes it would return 'expected one argument error". If I were to add square brackets it would read it fine but return KeyError when subsetting the inputted net file. 

11. To-do: try running *evacuateAreas.py*. See more info [here](https://github.com/eclipse/sumo/blob/main/tools/evacuateAreas.py).