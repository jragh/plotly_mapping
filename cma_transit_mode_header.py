import dash_mantine_components as dmc
from dash import html, dcc, Input, Output, State, Dash, _dash_renderer, get_asset_url, no_update, clientside_callback, callback, ClientsideFunction
from dash_iconify import DashIconify

cma_transit_mode_header = dmc.Grid(
    grow=True,
    gutter='xl',
    justify='center',
    children = [
        ## Column Number 1 for Public Transit Commuters ##
        dmc.GridCol(
            [
                    html.Span([
                    html.H6('Total Public Transit Commuters', style={'marginTop': '0', 'marginBottom': '0'}), 
                    DashIconify(icon="map:transit-station", height=20, width=20, style={'marginLeft': '0.5rem', 'marginRight': '0.3rem'})
                ], 
                style={
                    'borderRadius': '25px',
                    'backgroundColor': '#ff945d',
                    'display': 'inline-flex',
                    'align-items': 'center',
                    'padding': '0.25rem 0.5rem',
                    'flexWrap': 'nowrap',
                    'justifyContent': 'center'}),

                    html.H1('N/A', style={
                        'color': '#ff945d',
                        'fontWeight': '900',
                        'margin': '0',
                        'padding': '0',
                        'marginBottom': '.5rem',
                        'marginTop': '0.5rem'
                    }, id='cma_transit_mode_header_1')
            ], span={'xs': 12, 'sm': 6, 'md': 3},
            style={'maxWidth': '100vw', }
        ),

        ## Column Number 2 for Public Transit Share in CMA ##
        dmc.GridCol([
            html.Span([
                html.H6('Pct CMA Transit Commuters', style={'marginTop': '0', 'marginBottom': '0'}),
                DashIconify(icon="f7:chart-pie-fill", height=20, width=20, style={'marginLeft': '0.5rem', 'marginRight': '0.3rem'})
            ],
            style={
                'borderRadius': '25px', 
                'backgroundColor': '#ff945d', 
                'display': 'inline-flex', 
                'align-items': 'center', 
                'padding': '0.25rem 0.5rem', 
                'flexWrap': 'nowrap', 
                'justifyContent': 'center'}),

                html.H1('N/A', style={
                    'color': '#ff945d',
                    'fontWeight': '900',
                    'margin': '0',
                    'padding': '0'
                }, id='cma_transit_mode_header_2')
            ], span={'xs': 12, 'sm': 6, 'md': 3},
            style={'maxWidth': '60vw'}
        ),

        ## Column Number 3 for Private Automobilt Commuters in CMA ##
        dmc.GridCol([
            
            html.Div([

                html.Span([
                html.H6('Total Private Automobile Commuters', style={'marginTop': '0', 'marginBottom': '0'}),
                DashIconify(icon="f7:car-fill", height=20, width=20, style={'marginLeft': '0.5rem', 'marginRight': '0.3rem'})
                ],
                style={
                    'borderRadius': '25px',
                    'backgroundColor': '#4d86cc',
                    'display': 'inline-flex',
                    'align-items': 'center',
                    'padding': '0.25rem 0.5rem',
                    'flexWrap': 'nowrap',
                    'justifyContent': 'center'}),

                html.H1('N/A', style={
                    'color': '#4d86cc',
                    'fontWeight': '900',
                    'margin': '.8rem 0 0 0',
                    'padding': '0'
                }, id='cma_transit_mode_header_3')

            ], style={'background-color': '#c4d7ee'}, className='transit-mode-header-inner')
            
            ],span={'xs': 12, 'sm': 6, 'md': 3},
            style={'maxWidth': '60vw'},
            className='transit-mode-header-cell'
        ),

        ## Column Number 4 for Private Automobile Share in CMA ##
        dmc.GridCol([
            html.Span([
                html.H6('Pct CMA Private Automobile', style={'marginTop': '0', 'marginBottom': '0'}),
                DashIconify(icon="f7:chart-pie-fill", height=20, width=20, style={'marginLeft': '0.5rem', 'marginRight': '0.3rem'})
            ],
            style={
                'borderRadius': '25px',
                'backgroundColor': '#6a9ad4', 
                'display': 'inline-flex', 
                'align-items': 'center', 
                'padding': '0.25rem 0.5rem', 
                'flexWrap': 'nowrap', 
                'justifyContent': 'center'}),

            html.H1('N/A', style={
                'color': '#6a9ad4',
                'fontWeight': '900',
                'margin': '0',
                'padding': '0'
            }, id='cma_transit_mode_header_4')
            ],span={'xs': 12, 'sm': 6, 'md': 3},
        style={'maxWidth': '60vw', 'background-color': '#c4d7ee'},
        className='transit-mode-header-cell')
    ],
    id='map-grid-header' ## This id will be used to return children based on the query that is being pulled ##
)