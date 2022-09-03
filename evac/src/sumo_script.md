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
> this fucker returns 400-Bad Request with polygon. Try bbox: 

```{bash}
python "C:\Program Files (x86)\Eclipse\Sumo\tools\osmGet.py" --bbox "-119.731015, 34.445925, -119.704025, 34.465305"
```

> this returns 504-Gateway Timeout (need to check if this is related to public Wi-Fi settings)

5. Altenatively, use script that I wrote to download data using Overpass API that does not depend on SUMO API. **Make sure to change all of the paths in the python script.** 
```{bash}
cd rwmp_pipelines
python get_osm_by_poly.py 
```

6. Convert downloaded OSM data into a SUMO network (using recommended options)
```{bash}
netconvert --osm-files berlin.osm.xml -o berlin.net.xml --type-files C:\ C:\Program Files (x86)\Eclipse\Sumo\data\typemap\osmNetconvert.typ.xml --geometry.remove --ramps.guess --junctions.join --tls.guess-signals --tls.discard-simple --tls.join --tls.default-type actuated
```

# convert donwloaded data into SUMO network (recommended options)
# have to specify the typemap manually 
netconvert --osm-files study_area.osm.xml -o study_area.net.xml --type-files C:\Program Files (x86)\Eclipse\Sumo\data\typemap\osmNetconvert.typ.xml --geometry.remove --ramps.guess --junctions.join --tls.guess-signals --tls.discard-simple --tls.join --tls.default-type actuated