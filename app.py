import polars as pl
import plotly_express as px
from dash import html, dcc, Input, Output, State, Dash, _dash_renderer, get_asset_url, no_update, clientside_callback, callback
import dash_mantine_components as dmc
from flask import Flask, redirect
from dash_iconify import DashIconify
import json

import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.javascript import assign, arrow_function

## import for CMA / CA selection ##
from cma_ca_label_generate import cma_dropdown_component





server = Flask(__name__)


app = Dash(__name__, external_stylesheets=[dmc.styles.ALL, './assets/additional_styles.css'], server=server,  title="Plotly Mapping Test")

## TileMap ##
tile_layer = dl.TileLayer(
    url="https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png",
    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    id="positron"
)

## base GeoJSON manipulation ##
test_style = {'weight': 0.5, 'opacity': 0.65, 'color': 'white', 'dashArray': '', 'fillOpacity': 0.65}

style_handling_test = assign("""function(feature, context){
    
    const {colorvalues, colorscale, style, colorprop} = context.hideout;
                             

    console.log(colorprop);
    const value = feature.properties[colorprop];

    for (let i=0; i < colorvalues.length; i++) {
    
        if (value > colorvalues[i]) { style.fillColor = colorscale[i];}
    
    }
       
    
    // Style is stored in the hideout //
    // This updates the hideout to include the fillcolor for the given feature //
    
    return style; 
}""")

base_geojson = dl.GeoJSON(

    ## url='./assets/census_2021_shapes.geojson',
    data=None,
    id='base-geojson',
    hideout={'style': test_style, 'colorscale': [], 'colorvalues':[], 'colorprop':""},
    style=style_handling_test

)


layout = dmc.AppShell([
    
    dmc.AppShellMain(
        children = [

            html.Div([

                ## HMTL Span element for our Legend above the map here ##
                dmc.Select(label='Select a Data Topic',
                           placeholder='Choose a Data Topic....',
                           clearable=False,
                           id='geojson-selection',
                           data=[
                               {'value': 'assets/test_output_2.geojson', 'label': 'Travel Mode Analysis'},
                               {'value': 'testing_value', 'label': 'Commute To Work Duration'}
                           ], style={'marginBottom': '2rem'}),
                
                ## Dropdown showing all of the CMAs available ##
                cma_dropdown_component

                
                ## DMC Select for CMA Selection ##
                ## Will Note that Selecting all CMAs is very slow ##
                # dmc.Select(
                #     label='CMA Selection',
                #     description="Please Note: 'All CMAs Option Very Slow'",
                #     clearable=False,
                #     style={'marginBottom': '2rem '},
                #     id='cma-selection',
                #     data=cma_names_codes
                # )
            ]),
            dmc.Container([
                dmc.Grid(
                    grow=True,
                    gutter='md',
                    justify='center',
                    children = [
                        ## Column Number 1 for Public Transit Commuters ##
                        dmc.GridCol(
                           [
                                   html.Span([
                                   html.H6('Total Public Transit Commuters', style={'marginTop': '0', 'marginBottom': '0'}), 
                                   DashIconify(icon="map:transit-station", height=20, width=20, style={'marginLeft': '0.5rem', 'marginRight': '0.3rem'})
                                ], 
                                style={'borderRadius': '25px', 'backgroundColor': '#ff945d', 'display': 'inline-flex', 'align-items': 'center', 'padding': '0.25rem 0.5rem', 'flexWrap': 'nowrap', 'justifyContent': 'center'})
                            ], span={'xs': 12, 'sm': 6, 'md': 3}
                        ),

                        ## Column Number 2 for Public Transit Share in CMA ##
                        dmc.GridCol([
                            html.Span([
                                html.H6('Pct CMA Transit Commuters', style={'marginTop': '0', 'marginBottom': '0'}),
                                DashIconify(icon="f7:chart-pie-fill", height=20, width=20, style={'marginLeft': '0.5rem', 'marginRight': '0.3rem'})
                            ],
                            style={'borderRadius': '25px', 'backgroundColor': '#ff945d', 'display': 'inline-flex', 'align-items': 'center', 'padding': '0.25rem 0.5rem', 'flexWrap': 'nowrap', 'justifyContent': 'center'})
                        ],
                        span={'xs': 12, 'sm': 6, 'md': 3}),

                        ## Column Number 3 for Private Automobilt Commuters in CMA ##
                        dmc.GridCol([
                            html.Span([
                                html.H6('Total Private Automobile Commuters', style={'marginTop': '0', 'marginBottom': '0'}),
                                DashIconify(icon="f7:car-fill", height=20, width=20, style={'marginLeft': '0.5rem', 'marginRight': '0.3rem'})
                            ],
                            style={'borderRadius': '25px', 'backgroundColor': '#6a9ad4', 'display': 'inline-flex', 'align-items': 'center', 'padding': '0.25rem 0.5rem', 'flexWrap': 'nowrap', 'justifyContent': 'center'})
                        ],
                        span={'xs': 12, 'sm': 6, 'md': 3}),

                        ## Column Number 4 for Private Automobile Share in CMA ##
                        dmc.GridCol([
                            html.Span([
                                html.H6('Pct CMA Private Automobile', style={'marginTop': '0', 'marginBottom': '0'}),
                                DashIconify(icon="f7:chart-pie-fill", height=20, width=20, style={'marginLeft': '0.5rem', 'marginRight': '0.3rem'})
                            ],
                            style={'borderRadius': '25px', 'backgroundColor': '#6a9ad4', 'display': 'inline-flex', 'align-items': 'center', 'padding': '0.25rem 0.5rem', 'flexWrap': 'nowrap', 'justifyContent': 'center'})
                        ],
                        span={'xs': 12, 'sm': 6, 'md': 3})
                    ],
                    id='map-grid-header' ## This id will be used to return children based on the query that is being pulled ##
                ),

                dl.Map([tile_layer, base_geojson],
                       style={'height': '60vh',
                              "borderRadius": '12px'},
                       center=[43.6, -79],
                       zoom=10,
                       className='dash-leaflet-main-map'
                )
            ]
                , style={'padding': '0.2rem', 'margin': '2rem'},
                className='dash-leaflet-main-container',
                fluid=True
            ),

            ## Empty dcc.Store to store arbitrary json ##
            dcc.Store(id='geojson-store-data', data={}),

            ## E,pty dcc.Store to keep CMA / CA Aggregated Stats JSON ##
            dcc.Store(id='cma-ca-agg-store-data', data={}),

            ## Empty Store to have the grid columns selected ##
            dcc.Store(id='header-grid-selected', data={'selectedGrid': 'Travel Mode Analysis'})
        ]
    )]
    
)

## Color Scale 
## Max Orange: #ff945d
## Second Max Orange: #fdc182
## Min Blue: #1f77b4

## Blue 2: #5891c6

## Blue 3: #81acd9

## Blue 4: #a8c8ec

## Blue 5: #cee5ff

app.layout = dmc.MantineProvider(layout)

clientside_callback(

    """
        function(selectedCMAS, storedData, selectedProperty) {

            let colorScale = ["#1f77b4", "#5891c6", "#81acd9", "#a8c8ec", "#cee5ff", "#fdc182", "#ff945d"];


            if (!selectedCMAS || selectedProperty.length === 0) {
                return [null, {
                    "colorscale": colorScale,
                    "style": {'weight': 0.5, 'opacity': 0.65, 'color': 'white', 'dashArray': '', 'fillOpacity': 0.5},
                    "colorprop": "",
                    "colorvalues": null
                }];
            }


            if (selectedProperty === "assets/test_output_2.geojson") {

                let colorValues = [0.00, 2.00, 4.00, 6.00, 8.00, 10.00, 15.00];

                let fullData = storedData;
                // Filter features by selected CMAs
                let filteredfeatures = fullData.features.filter(
                    function(feature) { return selectedCMAS.includes(feature['properties']['CMA Code']); }
                );
                let filteredData = {
                    'type': "FeatureCollection",
                    "features": filteredfeatures
                };
                let hideout = {
                    'colorscale': colorScale,
                    "style": {'weight': 0.5, 'opacity': 0.65, 'color': 'white', 'dashArray': '', 'fillOpacity': 0.5},
                    "colorprop": "Pct of Public Transit Commute",
                    "colorvalues": colorValues
                };
                return [filteredData, hideout];
            }


            return [null, {
                "colorscale": colorScale,
                "style": {'weight': 0.5, 'opacity': 0.65, 'color': 'white', 'dashArray': '', 'fillOpacity': 0.5},
                "colorprop": "",
                "colorvalues": null
            }];
        
    
        }


    """,

    Output('base-geojson', 'data'),
    Output('base-geojson', 'hideout'),
    Input('cma-ca-selection', 'value'),
    State('geojson-store-data', 'data'),
    State('geojson-selection', 'value')

)


@callback(
    Output(component_id='geojson-store-data', component_property='data'),
    Output(component_id='cma-ca-agg-store-data', component_property='data'),
    Input(component_id='geojson-selection', component_property='value')
)
def geojson_selection(selected_data):

    if selected_data == 'assets/test_output_2.geojson':

        ## Open file geojson from value ##
        with open(selected_data, 'r') as f:

            return_data_1 = json.load(f)

        ## Open json for cma / ca aggregated stats ##
        with open('./assets/cma_ct_travel_stats_agg.json', 'r') as f:

            return_data_2 = json.load(f)
        
        return return_data_1, return_data_2

    
    else:

        return no_update
    

## Callback for our columns ##
@callback(
    Output(component_id='header-grid-selected', component_property='data'),
    Output(component_id='map-grid-header', component_property='children'),
    Input(component_id='geojson-selection', component_property='value'),
    State(component_id='header-grid-selected', component_property='data')
)

def update_grid_header(geojson_selected, hg_store_data):

    working_data = hg_store_data.copy()

    if geojson_selected == 'assets/test_output_2.geojson':

        if working_data['selectedGrid'] == 'Travel Mode Analysis':

            return no_update
        
        else:

            return_children = [
                        ## Column Number 1 for Public Transit Commuters ##
                        dmc.GridCol(
                           [
                                   html.Span([
                                   html.H6('Total Public Transit Commuters', style={'marginTop': '0', 'marginBottom': '0'}), 
                                   DashIconify(icon="map:transit-station", height=20, width=20, style={'marginLeft': '0.5rem', 'marginRight': '0.3rem'})
                                ], 
                                style={'borderRadius': '25px', 'backgroundColor': '#ff945d', 'display': 'inline-flex', 'align-items': 'center', 'padding': '0.25rem 0.5rem', 'flexWrap': 'nowrap', 'justifyContent': 'center'})
                            ], span={'xs': 12, 'sm': 6, 'md': 3}
                        ),

                        ## Column Number 2 for Public Transit Share in CMA ##
                        dmc.GridCol([
                            html.Span([
                                html.H6('Pct CMA Transit Commuters', style={'marginTop': '0', 'marginBottom': '0'}),
                                DashIconify(icon="f7:chart-pie-fill", height=20, width=20, style={'marginLeft': '0.5rem', 'marginRight': '0.3rem'})
                            ],
                            style={'borderRadius': '25px', 'backgroundColor': '#ff945d', 'display': 'inline-flex', 'align-items': 'center', 'padding': '0.25rem 0.5rem', 'flexWrap': 'nowrap', 'justifyContent': 'center'})
                        ],
                        span={'xs': 12, 'sm': 6, 'md': 3}),

                        ## Column Number 3 for Private Automobilt Commuters in CMA ##
                        dmc.GridCol([
                            html.Span([
                                html.H6('Total Private Automobile Commuters', style={'marginTop': '0', 'marginBottom': '0'}),
                                DashIconify(icon="f7:car-fill", height=20, width=20, style={'marginLeft': '0.5rem', 'marginRight': '0.3rem'})
                            ],
                            style={'borderRadius': '25px', 'backgroundColor': '#6a9ad4', 'display': 'inline-flex', 'align-items': 'center', 'padding': '0.25rem 0.5rem', 'flexWrap': 'nowrap', 'justifyContent': 'center'})
                        ],
                        span={'xs': 12, 'sm': 6, 'md': 3}),

                        ## Column Number 4 for Private Automobile Share in CMA ##
                        dmc.GridCol([
                            html.Span([
                                html.H6('Pct CMA Private Automobile', style={'marginTop': '0', 'marginBottom': '0'}),
                                DashIconify(icon="f7:chart-pie-fill", height=20, width=20, style={'marginLeft': '0.5rem', 'marginRight': '0.3rem'})
                            ],
                            style={'borderRadius': '25px', 'backgroundColor': '#6a9ad4', 'display': 'inline-flex', 'align-items': 'center', 'padding': '0.25rem 0.5rem', 'flexWrap': 'nowrap', 'justifyContent': 'center'})
                        ],
                        span={'xs': 12, 'sm': 6, 'md': 3})
                    ]

            return {'selectedGrid': 'Travel Mode Analysis'}, return_children
        

    ## Boilerplate no_update for now ##    
    return no_update


if __name__ == "__main__":
    app.run(debug=True)