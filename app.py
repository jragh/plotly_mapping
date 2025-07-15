import polars as pl
import plotly_express as px
from dash import html, dcc, Input, Output, State, Dash, _dash_renderer, get_asset_url, no_update
import dash_mantine_components as dmc
from flask import Flask, redirect

import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.javascript import assign, arrow_function





server = Flask(__name__)


app = Dash(__name__, external_stylesheets=dmc.styles.ALL, server=server,  title="Plotly Mapping Test")

## TileMap ##
tile_layer = dl.TileLayer(
    url="https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png",
    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    id="positron"
)

## base GeoJSON manipulation ##
test_style = {'weight': 1, 'opacity': 0.75, 'color': 'white', 'dashArray': '', 'fillOpacity': 0.7}

style_handling_test = assign("""function(feature, context){
                             const {style} = context.hideout;

                             style.fillColor = '#FEB24C';
                             
                             return style; }""")


base_geojson = dl.GeoJSON(

    url='./assets/census_2021_shapes.geojson',
    id='base-geojson',
    hideout={'style': test_style},
    style=style_handling_test

)


layout = dmc.AppShell([
    
    dmc.AppShellMain(
        children = [
            dmc.Container(
                dl.Map([tile_layer, base_geojson], style={'height': '50vh'}, center=[43.6, -79], zoom=6)
            )
        ]
    )]
    
)


app.layout = dmc.MantineProvider(layout)


if __name__ == "__main__":
    app.run(debug=True)