import polars as pl
import plotly_express as px
from dash import html, dcc, Input, Output, State, Dash, _dash_renderer, get_asset_url, no_update, clientside_callback, callback, ClientsideFunction
import dash_mantine_components as dmc
from flask import Flask, redirect
from dash_iconify import DashIconify
import json

import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.javascript import assign, arrow_function

## import for CMA / CA selection ##
from cma_ca_label_generate import cma_dropdown_component, cma_dropdown_value_label_store
from cma_transit_mode_header import cma_transit_mode_header





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

## Hover highlight applied to whichever census tract the cursor is over ##
ct_hover_style = arrow_function({'weight': 2.5, 'color': '#2b2b2b', 'fillOpacity': 0.9, 'dashArray': ''})

## Binds a rich tooltip to every census tract showing the full travel-mode breakdown ##
ct_on_each_feature = assign("""function(feature, layer, context){

    const p = feature.properties;
    if (!p) { return; }

    const fmt = function(n){ return (n == null) ? '0' : Number(n).toLocaleString('en-US'); };
    const total = p['Total Commuters To Work'] || 0;
    const pct = function(v){ return total > 0 ? ((v / total) * 100).toFixed(1) + '%' : '—'; };

    const transit = p['Public Transit'] || 0;
    const auto    = p['Automobile Drivers'] || 0;
    const carpool = p['Carpool Passengers'] || 0;
    const active  = p['Active (Walk, Bike, etc)'] || 0;
    const moto    = p['Motorcycle & Similar'] || 0;

    // Inline Material-style SVG glyphs so each mode reads at a glance //
    const PATHS = {
        transit: 'M4 16c0 .88.39 1.67 1 2.22V20c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h8v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1.78c.61-.55 1-1.34 1-2.22V6c0-3.5-3.58-4-8-4S4 2.5 4 6v10zM7.5 17C6.67 17 6 16.33 6 15.5S6.67 14 7.5 14 9 14.67 9 15.5 8.33 17 7.5 17zM16.5 17c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM18 11H6V6h12v5z',
        car: 'M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16C5.67 16 5 15.33 5 14.5S5.67 13 6.5 13 8 13.67 8 14.5 7.33 16 6.5 16zM17.5 16c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z',
        carpool: 'M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zM8 11c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zM8 13c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zM16 13c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z',
        bike: 'M15.5 5.5c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zM5 12c-2.8 0-5 2.2-5 5s2.2 5 5 5 5-2.2 5-5-2.2-5-5-5zm0 8.5c-1.9 0-3.5-1.6-3.5-3.5s1.6-3.5 3.5-3.5 3.5 1.6 3.5 3.5-1.6 3.5-3.5 3.5zm5.8-10l2.4-2.4.8.8c1.3 1.3 3 2.1 5.1 2.1V9c-1.5 0-2.7-.6-3.6-1.5l-1.9-1.9c-.5-.4-1-.6-1.6-.6s-1.1.2-1.4.6L7.8 8.4c-.4.4-.6.9-.6 1.4 0 .6.2 1.1.6 1.4L11 14v5h2v-6.2l-2.2-2.3zM19 12c-2.8 0-5 2.2-5 5s2.2 5 5 5 5-2.2 5-5-2.2-5-5-5zm0 8.5c-1.9 0-3.5-1.6-3.5-3.5s1.6-3.5 3.5-3.5 3.5 1.6 3.5 3.5-1.6 3.5-3.5 3.5z',
        moto: 'M19.44 9.03L15.41 5H11v2h3.59l2 2H5c-2.8 0-5 2.2-5 5s2.2 5 5 5c2.46 0 4.45-1.69 4.9-4h1.65l2.77-2.77c-.21.54-.31 1.14-.31 1.77 0 2.76 2.24 5 5 5s5-2.24 5-5c0-2.96-2.57-5.3-5.56-4.97zM7.82 15C7.4 16.15 6.28 17 5 17c-1.63 0-3-1.37-3-3s1.37-3 3-3c1.28 0 2.4.85 2.82 2H5v2h2.82zM19 17c-1.63 0-3-1.37-3-3s1.37-3 3-3 3 1.37 3 3-1.37 3-3 3z'
    };

    const icon = function(key, color){
        return '<svg class="ct-tt-icon" viewBox="0 0 24 24" width="15" height="15" fill="' + color + '" aria-hidden="true">'
            + '<path d="' + PATHS[key] + '"></path></svg>';
    };

    const ICON_GREY = '#8a95a1';

    const row = function(label, val, key){
        return '<div class="ct-tt-row">'
            + '<span class="ct-tt-label">' + icon(key, ICON_GREY) + label + '</span>'
            + '<span class="ct-tt-val"><b>' + fmt(val) + '</b> <span class="ct-tt-pct">(' + pct(val) + ')</span></span>'
            + '</div>';
    };

    const html = '<div class="ct-tt">'
        + '<div class="ct-tt-title">Census Tract ' + (p['CTUID'] || '') + '</div>'
        + '<div class="ct-tt-sub">Total commuters to work: <b>' + fmt(total) + '</b></div>'
        + '<div class="ct-tt-rows">'
        + row('Public transit',      transit, 'transit')
        + row('Auto (driver)',       auto,    'car')
        + row('Carpool passenger',   carpool, 'carpool')
        + row('Active (walk/bike)',  active,  'bike')
        + row('Motorcycle &amp; other', moto, 'moto')
        + '</div></div>';

    layer.bindTooltip(html, {sticky: true, direction: 'top', opacity: 1, className: 'ct-tooltip'});
}""")

style_handling_test = assign("""function(feature, context){
    
    const {colorvalues, colorscale, style, colorprop} = context.hideout;
                             
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
    style=style_handling_test,
    hoverStyle=ct_hover_style,
    onEachFeature=ct_on_each_feature

)

cma_bounds_dict = None

## Reading json file for CMA bounds to be loaded directly to DCC Store later on ##
with open('assets/cma_bounds.json', 'r') as f:

    cma_bounds_dict = json.load(f)

print(cma_bounds_dict)


layout = dmc.AppShell([
    
    dmc.AppShellMain(
        children = [ dmc.Container(fluid=True, className='app-root-container', children=[

            ## ---- Title / intro banner ---- ##
            html.Div([
                html.Div([
                    DashIconify(icon="solar:map-point-rotate-bold-duotone",
                                height=34, width=34, className='app-title-icon'),
                    html.Div([
                        html.H1('Canadian Commute Explorer', className='app-title'),
                        html.P(
                            'Explore how people travel to work across Canada’s census '
                            'metropolitan areas. Pick a data topic and a region to map '
                            'commuting patterns down to the census-tract level.',
                            className='app-subtitle')
                    ])
                ], className='app-title-row')
            ], className='app-header'),

            ## ---- Controls: responsive two-up row ---- ##
            dmc.Paper(
                withBorder=True, radius='lg', className='controls-card',
                children=[
                    dmc.SimpleGrid(
                        cols={'base': 1, 'sm': 2}, spacing='lg', verticalSpacing='md',
                        children=[
                            dmc.Select(label='Data topic',
                                       description='What you want to map',
                                       placeholder='Choose a data topic…',
                                       leftSection=DashIconify(icon='solar:layers-bold-duotone'),
                                       clearable=False,
                                       id='geojson-selection',
                                       data=[
                                           {'value': 'assets/test_output_2.geojson', 'label': 'Travel Mode Analysis'},
                                           {'value': 'testing_value', 'label': 'Commute To Work Duration'}
                                       ]),

                            ## Dropdown showing all of the CMAs available ##
                            cma_dropdown_component
                        ]
                    )
                ]
            ),

            dmc.Container([

                ## Header section for key stat ##
                html.H3(
                    'Key Statistics: Select a Topic and CMA to view',
                    id='key-stats-card-header',
                    className='key-stats-card-header',
                    style={'margin': '0'})

            ], fluid=True, className='key-stats-header-container',
               style={'padding': '0', 'margin': '0'}),

            dmc.Container([

                ## Component imported which is the header for our map ##
                cma_transit_mode_header

            ], style={'padding': '0', 'margin': '0'}
            ,className='dash-leaflet-header-container'
            ,id='dash-leaflet-header-container'
            ,fluid=True
            ),

            dmc.Container([
                dl.Map([tile_layer, base_geojson],
                       style={'height': '62vh',
                              'minHeight': '420px',
                              "borderRadius": '14px'},
                       center=[43.6, -79],
                       zoom=10,
                       className='dash-leaflet-main-map',
                       id='dash-leaflet-main-map',
                       viewport={
                           'transition': 'flyTo',
                           'options': {'animate': True, 'duration': 1.5, 'easeLinearity': 0.2}
                        }
                ),

                ## ---- Choropleth legend ---- ##
                html.Div([
                    html.Span('Public transit share of commuters', className='map-legend-title'),
                    html.Div([
                        html.Div([
                            html.Span(className='map-legend-swatch',
                                      style={'background': c}) for c in
                            ["#1f77b4", "#5891c6", "#81acd9", "#a8c8ec", "#cee5ff", "#fdc182", "#ff945d"]
                        ], className='map-legend-swatches'),
                        html.Div([
                            html.Span('Lower', className='map-legend-end'),
                            html.Span('Higher', className='map-legend-end')
                        ], className='map-legend-labels')
                    ], className='map-legend-scale'),
                    html.Span('Hover any tract on the map for a full travel-mode breakdown.',
                              className='map-legend-hint')
                ], className='map-legend')
            ]
                , style={'padding': '0', 'margin': '0'},
                className='dash-leaflet-map-container',
                fluid=True
            ),

            ## Empty dcc.Store to store arbitrary json ##
            dcc.Store(id='geojson-store-data', data={}),

            ## E,pty dcc.Store to keep CMA / CA Aggregated Stats JSON ##
            dcc.Store(id='cma-ca-agg-store-data', data={}),

            ## Empty Store to have the grid columns selected ##
            dcc.Store(id='header-grid-selected', data={'selectedGrid': ''}),

            ## dcc Store for CMA names and aggregated attribution ##
            cma_dropdown_value_label_store,

            ## dcc.Store for CMA bounds, total JSON should be ~ 6kb so this should be light ##
            dcc.Store(id='cma-bounds-store', data=cma_bounds_dict)
        ])]
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

## Clientside Callback for dropdown disablement and enablement ##
clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='updateCMADropdown'
    ),
    Output('cma-ca-selection', 'disabled'),
    Output('cma-ca-selection', 'value'),
    Input('geojson-selection', 'value')

)


clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='updateCMATransitModeHeader'
    ),
    Output('cma_transit_mode_header_1', 'children'),
    Output('cma_transit_mode_header_2', 'children'),
    Output('cma_transit_mode_header_3', 'children'),
    Output('cma_transit_mode_header_4', 'children'),
    Input('cma-ca-selection', 'value'),
    State('cma-ca-agg-store-data', 'data'),
    State('geojson-selection', 'value')
)

app.clientside_callback(

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




    

## Callback for our columns ##
@callback(
    Output(component_id='header-grid-selected', component_property='data'),
    Output(component_id='dash-leaflet-header-container', component_property='children'),
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
                cma_transit_mode_header
            ]

            return {'selectedGrid': 'Travel Mode Analysis', 'selectedGeography': 'All of Canada'}, return_children
        

    ## Boilerplate no_update for now ##    
    return no_update

## Clientside callback for stats overview section ##
clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='updateKeyStatsHeader'
    ),

    Output('key-stats-card-header', 'children'),
    Input('geojson-selection', 'value'),
    Input('cma-ca-selection', 'value'),
    State('geojson-selection', 'value'),
    State('cma-ca-selection', 'value'),
    State('cma-dropdown-data-store', 'data')
)

## Clientside callback to update leaflet map bounds ##
## leaflet bounds based on CMA selection ##
clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='updateLeafletMapBounds'
    ),

    Output('dash-leaflet-main-map', 'viewport'),
    Input('cma-ca-selection', 'value'),
    State('cma-bounds-store', 'data')
)



if __name__ == "__main__":
    app.run(debug=True) 
