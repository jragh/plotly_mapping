import pandas as pd
import polars as pl
import json
import re

from merge_dataframe_to_json import merge_geojson_with_polars, reduce_geojson_precision
from cma_ct_mapping_functions import extract_cma_code, extract_cma_string, extract_ct_string, extract_ct_uid_code

## Testing loading in the census files geojson 
census_shapes_json = './assets/census_2021_shapes.geojson'

with open(census_shapes_json, 'r') as json_raw:

    json_dict_census_shapes = json.load(json_raw)

## print(json_dict_census_shapes['features'][0])


## Open CSV file inside polars and do a print of the top 100 lines ##

travel_mode_ct_df = pl.read_csv('CTTravelByMode.csv', null_values=['X'], encoding='cp1252')

print(extract_cma_code('Ottawa - Gatineau (CMA) 505, Ont./Que.'))
print(extract_cma_string('Ottawa - Gatineau (CMA) 505, Ont./Que.'))
print(extract_ct_string('0001.06 - Ottawa - Gatineau'))
print(extract_ct_uid_code('0001.06 - Ottawa - Gatineau'))


## Part 1: Assign CMA Name to each Census Tract ##
travel_mode_ct_df_cleaned = travel_mode_ct_df.filter(~pl.col('Geography').str.contains_any(['(CMA)', '(CA)']))
travel_mode_ct_df_cleaned = travel_mode_ct_df_cleaned.with_columns([
    pl.col('Geography').map_elements(extract_ct_string).alias('CMA Name'),
    pl.col('Geography').map_elements(extract_ct_uid_code).alias('UID')])


## Part 2: Assign CMA Code and CMA Name from each CMA filtered from original dataframe ##
travel_mode_ct_df_cmas_only = travel_mode_ct_df.filter(pl.col('Geography').str.contains_any(['(CMA)', '(CA)']))
travel_mode_ct_df_cmas_only = travel_mode_ct_df_cmas_only.with_columns([
    pl.col('Geography').map_elements(extract_cma_string).alias('CMA Name'),
    pl.col('Geography').map_elements(extract_cma_code).alias('CMA Code')
])

travel_mode_ct_df_cmas_grouped = travel_mode_ct_df_cmas_only.group_by(['CMA Name', 'CMA Code']).len()

## Part 3: Joining together the CMA names and prefix with the CTs ##
travel_mode_ct_df_joined = travel_mode_ct_df_cleaned.join(travel_mode_ct_df_cmas_grouped, on='CMA Name', how='left')

travel_mode_ct_df_final = travel_mode_ct_df_joined.with_columns()
travel_mode_ct_df_final = travel_mode_ct_df_final.with_columns(pl.concat_str([
    pl.col('CMA Code'),
    pl.col('UID')
]).alias('CTUID'))


## Part 4: Summation into different columns for display on a map ##
## Setting up Commute Mode Columns ##
travel_mode_ct_df_final = travel_mode_ct_df_final.with_columns([
    pl.when(pl.col('Main mode of co') == '    Car, truck or van - as a driver').then(pl.col('Total - Commuting duration')).otherwise(0).alias('Automobile Drivers'),

    pl.when(pl.col('Main mode of co') == '    Car, truck or van - as a passenger').then(pl.col('Total - Commuting duration')).otherwise(0).alias('Carpool Passengers'),

    pl.when(pl.col('Main mode of co') == '    Public transit').then(pl.col('Total - Commuting duration')).otherwise(0).alias('Public Transit'),
  
    pl.when(pl.col('Main mode of co') == '    Active transportation').then(pl.col('Total - Commuting duration')).otherwise(0).alias('Active (Walk, Bike, etc)'),

    pl.when(pl.col('Main mode of co') == '  Motorcycle, scooter or moped').then(pl.col('Total - Commuting duration')).otherwise(0).alias('Motorcycle & Similar')
])

travel_mode_ct_df_final_grouped = travel_mode_ct_df_final.group_by(['CTUID', 'CMA Code', 'Geography']).agg([

    pl.col('Total - Commuting duration').sum().alias('Total Commuters To Work'), ## Total Commuters going into CT
    pl.col('Automobile Drivers').sum(), ## Total Automobile Drivers
    pl.col('Carpool Passengers').sum(), ## Total Carpoolers (Automobile Passengers)
    pl.col('Public Transit').sum(),
    pl.col('Active (Walk, Bike, etc)').sum(),
    pl.col('Motorcycle & Similar').sum()

])

## Calculate Public Transit Commute to Each Census Tract ##
travel_mode_ct_df_final_grouped = travel_mode_ct_df_final_grouped.with_columns(

    ((pl.col('Public Transit') / pl.col('Total Commuters To Work')) * 100.00).alias('Pct of Public Transit Commute')

)

## Fill in nan values where there are no commuters ##
travel_mode_ct_df_final_grouped = (
    travel_mode_ct_df_final_grouped
    .with_columns(pl.when(pl.col('Pct of Public Transit Commute').is_nan()).then(0)
              .otherwise(pl.col('Pct of Public Transit Commute')).alias('Pct of Public Transit Commute'))
)



# print(travel_mode_ct_df_final_grouped.head(25))
# print(travel_mode_ct_df_final_grouped['Pct of Public Transit Commute'].describe())
# print([travel_mode_ct_df_final_grouped['Pct of Public Transit Commute'].mean(), travel_mode_ct_df_final_grouped['Pct of Public Transit Commute'].median()])



## Step 5: Calculate Weighted score as
## Weighted Score = (1 - TUR / City_AVG_TUR) * (CP / City_AVG_CP)
## TUR = Transit Use Rate in tract

## CP = Commuting population in tract

## City_AVG_TUR = Average transit use rate for the city

## City_AVG_CP = Average commuting population per tract in the city

## Score_mean = (1 - TUR / City_AVG_TUR) * (CP / City_AVG_CP)
## Score_median = (1 - TUR / City_MEDIAN_TUR) * (CP / City_MEDIAN_CP)
## Final_Score = 0.5 * Score_mean + 0.5 * Score_median

## Gather CMA / CA  wide statistics
ct_median_average_transit_underserve = travel_mode_ct_df_final_grouped.group_by('CMA Code').agg([
    ## Commuting Population ##
    pl.col('Total Commuters To Work').mean().alias('CMA Average Commuters'),
    pl.col('Total Commuters To Work').median().alias('CMA Median Commuters'),

    ## Average CMA Rates ##
    ## Had to min the totoal commuters to work as 5 in each CT to handle 0 denomoinator issue ##
    ((pl.when(pl.col('Public Transit').is_nan()).then(0).otherwise(pl.col('Public Transit'))) / (pl.when(pl.col('Total Commuters To Work') == 0).then(5).otherwise(pl.col('Total Commuters To Work')))).mean().alias('CMA Average Public Transit Rate'),
    ((pl.when(pl.col('Public Transit').is_nan()).then(0).otherwise(pl.col('Public Transit'))) / (pl.when(pl.col('Total Commuters To Work') == 0).then(5).otherwise(pl.col('Total Commuters To Work')))).median().alias('CMA Median Public Transit Rate')

])

## Joining back to generate scores ##
travel_mode_ct_df_final_grouped = travel_mode_ct_df_final_grouped.join(ct_median_average_transit_underserve,
                                                                       on = 'CMA Code',
                                                                       how='left')

travel_mode_ct_df_final_grouped = travel_mode_ct_df_final_grouped.with_columns([

    ((1 - pl.col('Pct of Public Transit Commute') / pl.col('CMA Average Public Transit Rate')) * (pl.col('Total Commuters To Work') / pl.col('CMA Average Commuters'))).alias('Transit Score Average'),
    ((1 - pl.col('Pct of Public Transit Commute') / pl.when(pl.col('CMA Median Public Transit Rate') == 0.00).then(pl.col('CMA Average Public Transit Rate')).otherwise(pl.col('CMA Median Public Transit Rate'))) * (pl.col('Total Commuters To Work') / pl.col('CMA Median Commuters'))).alias('Transit Score Median')

])

travel_mode_ct_df_final_grouped = travel_mode_ct_df_final_grouped.with_columns([

    ((0.5 * pl.col('Transit Score Average')) + (0.5 * pl.col('Transit Score Median'))).alias('Transit Score Final')

])

print(travel_mode_ct_df_final_grouped.columns)


pt_ct = travel_mode_ct_df_final_grouped['CTUID',
                                'CMA Code',
                                'Total Commuters To Work',
                                'Automobile Drivers',
                                'Carpool Passengers',
                                'Public Transit',
                                'Active (Walk, Bike, etc)',
                                'Motorcycle & Similar',
                                'Pct of Public Transit Commute',
                                'Transit Score Final'
]
## print(travel_mode_ct_df_final_grouped.head(25).to_dicts())


## print(travel_mode_ct_df_final_grouped['Transit Score Final'].describe())

merge_geojson_with_polars('./assets/census_2021_shapes.geojson', pt_ct, 'CTUID', './assets/test_output.geojson')
reduce_geojson_precision('./assets/test_output.geojson', './assets/test_output_2.geojson', 4)


## Step 5: Join Polars Dataframe into census geojson dictionary, save as new geojson potentially depending on performance ##



# cmas_ca = travel_mode_ct_df.filter(pl.col('Geography').str.contains_any(['(CMA)', '(CA)']))['Geography'].unique().to_list()

# print(travel_mode_ct_df.head(100))

# print(cmas_ca)

# print(len(cmas_ca))