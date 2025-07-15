import pandas as pd
import polars as pl
import json

## Testing loading in the census files geojson 
census_shapes_json = './assets/census_2021_shapes.geojson'

with open(census_shapes_json, 'r') as json_raw:

    json_dict_census_shapes = json.load(json_raw)

print(json_dict_census_shapes['features'][0])


## Open CSV file inside polars and do a print of the top 100 lines ##

travel_mode_ct_df = pl.read_csv('CTTravelByMode.csv', null_values=['X'], encoding='cp1252')

travel_mode_ct_df_grouped = travel_mode_ct_df.group_by('Geography').agg(
    pl.when(pl.col('Main mode of co') == '    Car, truck or van - as a driver')
    .then(pl.col('Total - Commuting duration'))
    .otherwise(0)
    .sum()
    .alias('Motor Vehicle Driver')
).filter(pl.col('Geography') == 'Ottawa - Gatineau (CMA) 505, Ont./Que.')

print(travel_mode_ct_df.head(10))

print(travel_mode_ct_df_grouped.head(10))


# cmas_ca = travel_mode_ct_df.filter(pl.col('Geography').str.contains_any(['(CMA)', '(CA)']))['Geography'].unique().to_list()

# print(travel_mode_ct_df.head(100))

# print(cmas_ca)

# print(len(cmas_ca))