#############################
# Import libraries
#############################

# General libraries
import numpy as np
import pandas as pd
# Import plotly
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
# Import dash
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from jupyter_dash import JupyterDash


# Set renderer to view in jupyter notebook
pio.renderers.default = "notebook"


####################################
# Define data and plotting functions
####################################

# Load and prepare map data
def prepare_data():
    df = pd.read_csv("data/bluecard_EU_df.csv")
    # Remove index column named "unnamed: 0"
    df.drop(df.filter(regex="Unname"),axis=1, inplace=True)
    return df

# Load data
df = prepare_data()

# Header content to introduce the dashboard
def drawHeader():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.H2("EU Visa Dashboard"),
                    html.P("Do you plan to visit or move to Europe? \
                            This dashboard illustrates the number of EU visas issued \
                            or rejected and relates this to the characteristics \
                            of the originating country"),
                ], style={'textAlign': 'center'}) 
            ])
        ),
    ])


# Create world map for visa statistics
def drawWorldMap(feature = "total_population"):
    figure = go.Figure(data=go.Choropleth(
                        locations = df['Country_CODE'],
                        z = df[str(feature)].round(2),
                        #text = df['duration_days'],
                        #hover_name=df_blue['duration_days'].round(2), 
                        colorscale = 'YlGnBu',
                        autocolorscale=False,
                        reversescale=False,
                        marker_line_color='darkgray',
                        marker_line_width=0.5,
                        colorbar_tickprefix = '',
                        colorbar_title = ' ',
                        colorbar_title_font_size=15
                    )).update_layout(
                        width=880,
                        height=500,
                        geo=dict(
                            showframe=False,
                            showcoastlines=False,
                            projection_type='equirectangular'
                            #paper_bgcolor='#4E5D6C',
                            #plot_bgcolor= 'rgba(0,0,0,0)'
                        ),
                        title={
                            'text': feature,
                            'y':0.9,
                            'x':0.5,
                            'xanchor': 'center',
                            'yanchor': 'top',
                        },
                        title_font_color='#525252',
                        title_font_size=26,
                        font=dict(
                            family='Heebo', 
                            size=18, 
                            color='#525252'
                        ),
                        annotations = [dict(
                            x=0.5,
                            y=0.1,
                            xref='paper',
                            yref='paper',
                            showarrow = True
                        )]
                    )
    return figure

# Create world map for visa statistics
worldmap_card = html.Div([
                    dbc.Card(
                        dbc.CardBody([
                            dcc.Graph(
                                id = "worldmap",     
                            ) 
                        ])
                    ),  
                ])

# Histogram displaying map statistics in detail and ordered by country
def drawHistogram(feature = "age"):
    # plot
    figure = px.histogram(
                        x=df[str(feature)], 
                        height=300,
                        labels={'x':feature, 'y':'count'},
                    ).update_layout(
                        template='plotly_dark',
                        plot_bgcolor= 'rgba(0, 0, 0, 0)',
                        paper_bgcolor= 'rgba(0, 0, 0, 0)',
                    )
    return figure

# Create container for histogram
histogram_card = dbc.Card(
            dbc.CardBody(
                [
                    dcc.Graph(
                        id = "histogram",
                        config={
                            'displayModeBar': False,
                        }
                    ) 
                ]
            )
        )

# Correlation scatter plot with size displaying a third feature
def drawBubbleChart():
    return  html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    figure=px.line(df, x="age", y="duration_days", height=300
                    ).update_layout(
                        template='plotly_dark',
                        plot_bgcolor= 'rgba(0, 0, 0, 0)',
                        paper_bgcolor= 'rgba(0, 0, 0, 0)',
                    ),
                    config={
                        'displayModeBar': False
                    }
                ) 
            ])
        ),  
    ])

# Drop down field for country selection
def dropdownCountry(data, label, feature):
    # Extract header names
    list_items = data[feature].unique()
    # Remove nans
    list_items = list_items[~pd.isnull(list_items)]
    # Sort items alphabetically
    list_items.sort()
    #list_items = {'children': list_items, 'id':list_items}
    list_items = [{'label':name, 'value':name} for name in list_items]

    return  html.Div([
            dbc.Card(
                dbc.CardBody([
                    #dcc.Dropdown(id = "dd", label = "dfdf", value = "sd")
                    html.H6(label),
                    dcc.Dropdown(id = label, options=list_items, \
                    searchable = True, value =list_items[0].get("label")),
                ])
            ),  
        ])

# Drop down field for visa feature
def dropdownVisa():
    return  html.Div([
        dbc.Card(
            dbc.CardBody([
                dbc.DropdownMenu(
                    label="Select visa feature",
                    children=[
                        dbc.DropdownMenuItem("Number of Visa Applications", id = "Number of Visa Applications"),
                        dbc.DropdownMenuItem("Schengen visas issued", id = "Visas Issued"),
                        dbc.DropdownMenuItem("Schengen visas denied", id = "Visas Denied"),
                        dbc.DropdownMenuItem("Total population", id = "total_population"),
                    ],
                ) 
            ])
        ),  
    ])



# Drop down field for geographic feature
def dropdownGeoFeature():
    return  html.Div([
        dbc.Card(
            dbc.CardBody([
                dbc.DropdownMenu(
                    label="Select visa feature",
                    children=[
                        dbc.DropdownMenuItem("Total population", id = "mortality_rate_infants"),
                        dbc.DropdownMenuItem("Life expectancy", id = "life_expectancy_index"),
                    ],
                )
            ])
        ),  
    ])


# Slider to select time frame
def timeSlider():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    dbc.Label("Select time period", html_for="slider"),
                    dcc.RangeSlider(min = 2014, 
                                    max = 2022, 
                                    step = 1, 
                                    value=[2014, 2020], 
                                    id='my-range-slider', 
                                    marks={
                                            2014: '2014',
                                            2016: '2016',
                                            2018: '2018',
                                            2020: '2020',
                                            2022: '2022'
                                    },
                    ),
                ], className="mb-3"
                )
            ])
        ),
    ])


#############################
# Build app layout
#############################

# Build App
app = JupyterDash(external_stylesheets=[dbc.themes.SLATE])

app.layout = html.Div([
    dbc.Card(
        dbc.CardBody([
            dbc.Row([
                # Container for header
                dbc.Col([
                    drawHeader()
                ], width=12),
            ], align='center'), 
            html.Br(),
            dbc.Row([
                # Container for world map
                dbc.Col([
                    worldmap_card
                ], width=8),
                # Container for user input
                dbc.Col([
                    dropdownCountry(data = df, label = "Country of origin", feature = "cap_country"),
                    dropdownCountry(data = df, label = "Schengen country", feature = "Schengen State"),
                    dropdownVisa(),
                    dropdownGeoFeature(),
                    timeSlider(),
                    html.P(id = "item_display")
                ], width=4),
            ], align='top'), 
            html.Br(),
            dbc.Row([
                # Container for histogram
                dbc.Col([
                    histogram_card
                ], width=4),
                # Container for bubble chart
                dbc.Col([
                    drawBubbleChart()
                ], width=4),
            ], align='center'),      
        ]), color = 'dark'
    )
])

################################
# Interactive callback functions
################################

@app.callback(
    Output("item_display", "children"),
    Output('histogram', 'figure'),
    Output('worldmap', 'figure'),
    [
        Input("Number of Visa Applications", "n_clicks"),
        Input("Visas Issued", "n_clicks"),
        Input("Visas Denied", "n_clicks"),
        Input("total_population", "n_clicks"),
    ],
)
# Function for callback
def make_graph(*args):
    # Extract content of callback
    ctx = dash.callback_context

    # If no list item selected set default entry
    if not ctx.triggered:
        feature = "Visas Issued"
    else:
        # Extract id of list item
        feature = ctx.triggered[0]["prop_id"].split(".")[0]
    fig = drawHistogram(feature)

    worldmap = drawWorldMap(feature)
    print(feature)
    return feature, fig, worldmap


if __name__ == "__main__":
    app.run_server(debug=True, port=8050, host='0.0.0.0')