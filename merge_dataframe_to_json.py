import json
import pandas as pd
import polars as pl

def merge_geojson_with_polars(geojson_path, dataframe, join_column, output_path, encoding='cp1252'):

    with open(geojson_path, 'r', encoding=encoding) as input_file:

        input_geojson = json.load(input_file)

    ## Close the file so as to not waste any additional computing for any random reason ##
    input_file.close()

    ## Conver the Polars Dataframe to Dictionary with leading ctuid as the index ##
    dataframe_dicts = dataframe.to_dicts()

    dataframe_dict = {d['CTUID']: {k: v for k, v in d.items() if k != 'CTUID'} for d in dataframe_dicts}

    ## Loop through features in geojson ##
    for feature in input_geojson['features']:

        if 'gml_id' in feature['properties'].keys():

            del feature['properties']['gml_id']

        if 'DGUID' in feature['properties'].keys():

            del feature['properties']['DGUID']

        if 'CTNAME' in feature['properties'].keys():

            del feature['properties']['CTNAME']

        ## Get CTUID data based on join column ##
        ctuid = feature['properties'].get(join_column)

        if ctuid is not None and ctuid in dataframe_dict:

            feature['properties'].update(dataframe_dict[ctuid])

        else:

            print(f'Warning: Feature not found for {join_column}: {ctuid}')

    with open(output_path, 'w') as fi:

        json.dump(input_geojson, fi, separators=(',', ':'))

        print(f'File has successfully been written to {output_path}')


## function to reduce geojson precision if needed ##
def reduce_geojson_precision(input_file, output_file, decimal_places=5):

    def round_coords(obj):

        if isinstance(obj, dict):

            if obj.get('type') in ['Point', 'LineString', 'Polygon', 'MultiPoint', 'MultiLineString', 'MultiPolygon']:

                ## True: This is a geometry that needs to be rounded
                if 'coordinates' in obj:
                    obj['coordinates'] = round_coords(obj['coordinates'])

            else: 
                ## Regular dictionary: Loop through and round each value ##
                for key, val in obj.items():
                    obj[key] = round_coords(val)

        ## Else if it's a list like a multi polygon ##
        elif isinstance(obj, list):
            ## Final Layer of the nested list
            if len(obj) > 0 and isinstance(obj[0], (int, float)):

                return [round(x, decimal_places) for x in obj]
            
            else:

                return [round_coords(item) for item in obj]
    
        return obj

    print(f'Processing Input file: {input_file}...')

    with open(input_file, 'r') as f:

        input_geojson = json.load(f)

    original_size = len(json.dumps(input_geojson))

    print(f"Original size: {original_size:,} characters")

    ## Rounding of the coordinates ##
    round_coords(input_geojson)

    with open(output_file, 'w') as file_output:

        json.dump(input_geojson, file_output, separators=(',', ':'))

    new_size = len(json.dumps(input_geojson))
    reduction = ((original_size - new_size) / original_size) * 100
    
    print(f"New size: {new_size:,} characters")
    print(f"Reduction: {reduction:.1f}%")
    print(f"Saved to: {output_file}")