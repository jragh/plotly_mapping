import json
import pandas as pd
import polars as pl
import numpy as np
from osgeo import gdal as gd

def generate_centroids_per_cma(cleaned_cma_json: str):

    try:

        with open(cleaned_cma_json, 'r', encoding='cp1252') as input_file:

            cleaned_input_json = json.load(input_file)

        ## Close the input file to avoid wasting resources once done ##
        input_file.close()

        ## For each multi polygon, i want to generate the centroid
        ## centroids will be grouped back to the CMA inside of the tracking dictionary
        ## Then cast the average and the zoom as the zoom to bounds to be pulled 


        ## Checks if the given is a coordinate pair ##
        ## Checks if the item is a list, if the length is 2, and all items im the list are int or float
        def check_coordinate_pair(list_item):

            return (isinstance(list_item, list) and len(list_item) == 2 and all(isinstance(x, (int, float)) for x in list_item))
        
        ## Function to generate the centroid from a list of coordinates ##
        ## Supposed to be very fast from stack overflow ##
        def centroid_generate(arr):

            return np.mean(arr, axis=0)


        cma_centroids = {}

        for feature in cleaned_input_json['features']:

            polygon_tracking_list = []

            ctuid_id = str(feature['properties']['CTUID'])

            cma_code = str(feature['properties']['CMA Code'])

            ## Recursive function that loops through the lists of multipolygons for coordinates
            ## if fits the criteria for coordiate list, then append the coordinates to the tracking list
            ## else use recursion to go a level deeper inside the multipolygon ##
            def extract_coordinate_pair_recursive(obj):

                ## If condition where the object is a coordinate pair
                if check_coordinate_pair(obj):

                    polygon_tracking_list.append(obj)

                ## condition to go deeper in the recursion hold
                elif isinstance(obj, list):

                    for val in obj:

                        extract_coordinate_pair_recursive(val)

            
            extract_coordinate_pair_recursive(feature['geometry']['coordinates'])

            polygon_centroid = centroid_generate(polygon_tracking_list)

            # print(f"{cma_code} ---- {ctuid_id}")
            
            ## print(list(polygon_centroid))

            ## Check to see if centroid exists in dictionary yet, if not then add else append ##
            if cma_code in cma_centroids.keys():

                cma_centroids[cma_code].append([float(polygon_centroid[0]), float(polygon_centroid[1])])

            else:

                cma_centroids[cma_code] = [[float(polygon_centroid[0]), float(polygon_centroid[1])]]

        cma_bounds = {}
        
        for cma in cma_centroids.keys():

            lats, longs = zip(*cma_centroids[cma])

            bounds = [[min(lats), min(longs)], [max(lats), max(longs)]]

            cma_bounds[cma] = bounds

        print(cma_bounds)

    except Exception as e:

        print('Error occurred with function `generate_centroids_per_cma`')
        print(f"Exception from the function is as follows: {e}")

generate_centroids_per_cma('assets/test_output_2.geojson')