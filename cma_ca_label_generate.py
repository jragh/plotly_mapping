import polars as pl
from cma_ct_mapping_functions import extract_cma_code, extract_cma_string
import dash_mantine_components as dmc


## Open the CSV
travel_mode_ct_df = pl.read_csv('CTTravelByMode.csv', encoding='cp1252', null_values=['X'])

## Only take in geography records where it contains CMA or CA
travel_mode_ct_df_cmas_only = travel_mode_ct_df.filter(pl.col('Geography').str.contains_any(['(CMA)', '(CA)']))

## Maps the extract cmastring & cmacode to columns based on the dataframe entries ##
travel_mode_ct_df_cmas_only = travel_mode_ct_df_cmas_only.with_columns([
    pl.col('Geography').map_elements(extract_cma_string).alias('CMA Name'),
    pl.col('Geography').map_elements(extract_cma_code).alias('CMA Code')
])

## Provides just the CMA Name and the CMA Code ##
travel_mode_ct_df_cmas_grouped = travel_mode_ct_df_cmas_only.group_by(['CMA Name', 'CMA Code']).len()

## Return Array of Dictionaries for our multiselect ##
cma_names_codes = [{'value': row[1], 'label': f'{row[0]} ({row[1]})'} for row in travel_mode_ct_df_cmas_grouped.iter_rows()]

cma_names_codes.append({'value': "All CMAs / CAs", 'label': "All CMAs / CAs"})

cma_dropdown_component = dmc.Select(
                    label='CMA Selection',
                    description="Please Note: 'All CMAs Option Very Slow'",
                    clearable=False,
                    style={'marginBottom': '2rem '},
                    ## Need to use Styles to deal with styles api ##,
                    styles={'option': {'fontSize': '0.8em'}},
                    data=cma_names_codes, 
                    searchable=True,
                    id='cma-ca-selection'
                
                )


## Print Statement for Debugging Down the Road ##
# print(cma_names_codes)
# print(len(cma_names_codes))
