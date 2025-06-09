## Assignemnt 3: GeoPython 

### Exploring sentinel1-GRD products using pystac_client package

In this exercise, I tried to use pystac_client package primarily along with other packages (geopandas, rasterio) to build the python class "Sentinel1GRDProcessor" and add search_data functionality to support folllowing activities:
- To search the sentinel-1 GRD products for the area-of-interest (AOI) using the STAC api
- visualize the thumbnail (new)
- Explore the properties and assets of data
- Read the vv and vh band and visualize
- Crop data with AOI

To setup the project environment run: 

``` conda env create -f env.yml ```

To activate the environment:

``` conda activate python_a3_temp_env ```

### Resources

[pystac_client](https://github.com/stac-utils/pystac-client?tab=readme-ov-file)
