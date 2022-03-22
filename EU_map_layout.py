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
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from jupyter_dash import JupyterDash


# Set renderer to view in jupyter notebook
pio.renderers.default = "notebook"


####################################
# Define data and plotting functions
####################################

# Load and prepare map data
def prepare_data():
    df = pd.read_csv("data/talent_bluecard.csv")
    return df

# Load data
df = prepare_data()
df = px.data.iris()

# Header content to introduce the dashboard
def drawHeader():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.H2("EU visa data"),
                    html.P("This dashboard illustrates visa statistics"),
                ], style={'textAlign': 'left'}) 
            ])
        ),
    ])

# Create world map for visa statistics
def drawWorldMap():
    return  html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    figure=px.bar(
                        df, x="sepal_width", y="sepal_length", color="species"
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

# Histogram displaying map statistics in detail and ordered by country
def drawHistogram():
    return  html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    figure=px.bar(
                        df, x="sepal_width", y="sepal_length", color="species", height=300
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

# Correlation scatter plot with size displaying a third feature
def drawBubbleChart():
    return  html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    figure=px.line(df, x="sepal_width", y="sepal_length", height=300
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


# Drop down field for visa feature
def dropdownVisa():
    return  html.Div([
        dbc.Card(
            dbc.CardBody([
                dbc.DropdownMenu(
                    label="Select visa feature",
                    children=[
                        dbc.DropdownMenuItem("Schengen visa"),
                        dbc.DropdownMenuItem("Visa processing time"),
                        dbc.DropdownMenuItem("Item 3"),
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
                    label="Select geographic feature",
                    children=[
                        dbc.DropdownMenuItem("Life expectancy"),
                        dbc.DropdownMenuItem("Item 2"),
                        dbc.DropdownMenuItem("Item 3"),
                    ],
                ) 
            ])
        ),  
    ])

# Container for user input via drop down and slider fields
def drawText():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.H2("Text"),
                ], style={'textAlign': 'center'}) 
            ])
        ),
    ])

# Slider to select time frame
def timeSlider():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    dbc.Label("Slider", html_for="slider"),
                    dcc.Slider(id="slider", min=0, max=10, step=0.5, value=3),
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
                    drawWorldMap() 
                ], width=8),
                # Container for user input
                dbc.Col([
                    dropdownVisa(),
                    dropdownGeoFeature(),
                    timeSlider()
                ], width=4),
            ], align='center'), 
            html.Br(),
            dbc.Row([
                # Container for histogram
                dbc.Col([
                    drawHistogram()
                ], width=4),
                # Container for bubble chart
                dbc.Col([
                    drawBubbleChart()
                ], width=4),
            ], align='center'),      
        ]), color = 'dark'
    )
])

if __name__ == "__main__":
    app.run_server(debug=False, port=8050, host='0.0.0.0')