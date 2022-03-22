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
from dash.dependencies import Input, Output


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

# define country collection
bluecard_country = df['nationality_country'].unique().tolist()
country_list = []
country_list.append({'label': 'All countries', 'value': 'All countries'})
for country in bluecard_country:
    country_list.append({'label': country, 'value': country})

# define (numeric) feature collection
bluecard_feature = df.describe().columns.tolist()
feature_list = []
for feature in bluecard_feature:
    feature_list.append({'label': feature, 'value': feature})


#################################### dataframe for plotting ###########################################
# create new Dataframe which contains the median of all numeric values grouped by nationality country
talent_bluecard_median = pd.DataFrame(df.groupby('nationality_country').median()).reset_index()
# count number of clients per country
talent_bluecard_client = df.groupby("nationality_country").size().to_frame('total_clients').reset_index()
# merge two dataframes for plotting
df = talent_bluecard_median.merge(talent_bluecard_client, on = 'nationality_country')
#######################################################################################################

# Correlation scatter plot with size displaying a third feature
def plot_bubble(country_dropdown, feature_dropdown):
    if (country_dropdown == 'All countries'): # plot for all countries
        figure = px.scatter(df,
            x=feature_dropdown, #"age", 
            y="duration_days",
	        size="total_clients", 
            color="nationality_country",
            hover_name="nationality_country", 
            labels=dict(duration_days="Median Processing Time (days)", age="Median Age (years)", nationality_country='Country of Origin', total_clients='Total number of clients'),
            size_max=60).update_layout(
                        showlegend=False,
                        template='plotly_dark',
                        plot_bgcolor= 'rgba(0, 0, 0, 0)',
                        paper_bgcolor= 'rgba(0, 0, 0, 0)',
                        margin={"r":0,"t":0,"l":0,"b":0}
                        )
    else:
        #df = df.loc[df['nationality_country']== country_dropdown]
        figure = px.scatter(df[df["nationality_country"] == country_dropdown], # plot for selected country
            x=feature_dropdown,#"age", 
            y="duration_days",
	        size="total_clients", 
            color="nationality_country",
            hover_name="nationality_country", 
            labels=dict(duration_days="Median Processing Time (days)", age="Median Age (years)", nationality_country='Country of Origin', total_clients='Total number of clients'),
            size_max=60).update_layout(
                        showlegend=False,
                        template='plotly_dark',
                        plot_bgcolor= 'rgba(0, 0, 0, 0)',
                        paper_bgcolor= 'rgba(0, 0, 0, 0)',
                        margin={"r":0,"t":0,"l":0,"b":0}
                        )
    return figure


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
app = JupyterDash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# define card for bubble plot, which will be pasted in the app.layout below
plot_bubble_card = dbc.Card(
    dbc.CardBody(
        [
            html.H2('Just a Test'),
            dcc.Dropdown(id = 'country_dropdown', options=country_list, \
                    searchable = True, value= 'All countries'),
            dcc.Dropdown(id = 'feature_dropdown', options=feature_list, \
                    searchable = True, value= 'age'),
            dcc.Graph(id='bubbleplot')
        ]
    )
)

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
                    drawHeader()#drawWorldMap() 
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
                    drawHeader()#drawHistogram()
                ], width=4),
                # Container for bubble chart
                dbc.Col([plot_bubble_card], width=4), ########### here the layout for bubble plot will be pasted 
            ], align='center'),      
        ]), color = 'dark'
    )
])

# callback for bubbleplot with two input variables
@app.callback(
            Output(component_id='bubbleplot', component_property = 'figure'),
            Input(component_id='country_dropdown', component_property='value'),
            Input(component_id='feature_dropdown', component_property='value'))

# function updates bubbleplot after changing input variables
def update_bubbleplot(country_dropdown, feature_dropdown):
    plot = plot_bubble(country_dropdown, feature_dropdown)
    return plot

# if __name__ == "__main__":
#      app.run_server(debug=False, port=8050, host='0.0.0.0')

if __name__ == '__main__':
    app.run_server(debug=True)