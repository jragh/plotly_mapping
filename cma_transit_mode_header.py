import dash_mantine_components as dmc
from dash import html, dcc, Input, Output, State, Dash, _dash_renderer, get_asset_url, no_update, clientside_callback, callback, ClientsideFunction
from dash_iconify import DashIconify


def _kpi_card(title, subtitle, icon, accent, value_id):
    """Builds a single KPI card. `accent` is 'transit' (orange) or 'auto' (blue)."""
    return dmc.GridCol(
        html.Div([

            ## Pill badge: icon + short metric name ##
            html.Span([
                DashIconify(icon=icon, height=18, width=18, className='kpi-pill-icon'),
                html.Span(title, className='kpi-pill-label')
            ], className='kpi-pill'),

            ## Headline number ##
            html.H1('N/A', className='kpi-value', id=value_id),

            ## Supporting description ##
            html.Small(subtitle, className='kpi-sub')

        ], className=f'transit-mode-header-inner kpi-card kpi-{accent}'),
        span={'base': 12, 'xs': 6, 'md': 3},
        className='transit-mode-header-cell'
    )


cma_transit_mode_header = dmc.Grid(
    grow=True,
    gutter='xl',
    justify='center',
    children=[

        _kpi_card(
            title='Public Transit',
            subtitle='Total work commuters using public transit',
            icon='map:transit-station',
            accent='transit',
            value_id='cma_transit_mode_header_1'
        ),

        _kpi_card(
            title='Transit Share',
            subtitle='Share of commuters using public transit',
            icon='f7:chart-pie-fill',
            accent='transit',
            value_id='cma_transit_mode_header_2'
        ),

        _kpi_card(
            title='Auto (Driver)',
            subtitle='Total work commuters driving a private vehicle',
            icon='f7:car-fill',
            accent='auto',
            value_id='cma_transit_mode_header_3'
        ),

        _kpi_card(
            title='Auto Share',
            subtitle='Share of commuters driving a private vehicle',
            icon='f7:chart-pie-fill',
            accent='auto',
            value_id='cma_transit_mode_header_4'
        ),

    ],
    id='map-grid-header'  ## This id will be used to return children based on the query that is being pulled ##
)
