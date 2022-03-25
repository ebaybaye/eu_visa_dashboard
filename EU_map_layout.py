#############################
# Import libraries
#############################

# General libraries
from re import M
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
import dash_daq as daq # toggle switch

# To convert country names and iso codes
from pycountry_convert import country_alpha2_to_country_name, country_alpha3_to_country_alpha2

# Set renderer to view in jupyter notebook
pio.renderers.default = "notebook"


####################################
# Load and prepare data
####################################

def load_data():
    # Load data globally
    df = pd.read_csv("data/df_iso_schengen_origin.csv")

    # Add columns for full Schengen country names
    df["Schengen_country"] = df["SCH_CODE"].apply(lambda x: country_alpha2_to_country_name(country_alpha3_to_country_alpha2(x)))

    # Capatilize all column names to prevent string matching conflicts
    df.columns = [x.capitalize() for x in df.columns]
    # Remove underscores from column names
    df.columns = [name.replace("_", ' ') for name in df.columns]

    # drop all nan from all country columns
    df.dropna(subset = ['Schengen country'], inplace = True)
    df.dropna(subset = ['Country'], inplace = True)

    return df

df = load_data()

####################################
# Define features that can be selected by used from columns names
# Save features in list
feature_list = df.columns.unique().to_list()
# Select features to be excluded
remove_features = ['Year', 'Country code', 'Sch code', 'Schengen country', "Country"]
# Remove those features from list
feature_list = [ele for ele in feature_list if ele not in remove_features]

# Define min and max time range for slider and graphs
min_time = min(df["Year"])
max_time = max(df["Year"])

####################################
# Define data and plotting functions
####################################

# Header content to introduce the dashboard
def drawHeader():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.H2("EU Schengen Visa Dashboard"),
                    html.P("Do you plan to visit or move to Europe? \
                            This dashboard illustrates the number of EU visas issued \
                            or rejected and relates this to the characteristics \
                            of the originating country"),
                ], style={'textAlign': 'center'}) 
            ])
        ),
    ])


# Create world map for visa statistics
def drawWorldMap(data = df, feature = "Total population"):
    figure = go.Figure(data=go.Choropleth(
                        locations = data['Country code'],
                        z = data[str(feature)].round(2),
                        text ='Feature: '+str(feature)+'<br>'+'Country: '+data['Country'],
                        colorscale = 'YlGnBu',
                        autocolorscale=False,
                        reversescale=False,
                        marker_line_color='darkgray',
                        marker_line_width=0.5,
                        colorbar_tickprefix = '',
                        colorbar_title = ' ',
                        colorbar_title_font_size=10
                    )).update_layout(
                        width=880,
                        height=500,
                        paper_bgcolor='rgba(0,0,0,0)',
                        geo=dict(
                            bgcolor='rgba(0,0,0,0)',
                            landcolor=text_color,
                            showframe=False,
                            showcoastlines=False,
                            projection_type='equirectangular'
                        ),
                        hoverlabel_font_size=15,
                        hoverlabel=dict(
                                    bgcolor="darkgray",
                                    font_size=13,
                                    font_family="Rockwell"),
                        title={
                            'text': feature,
                            'y':0.9,
                            'x':0.5,
                            'xanchor': 'center',
                            'yanchor': 'top',
                        },
                        title_font_color=text_color,
                        title_font_size=26,
                        font=dict(
                            family='Heebo', 
                            size=18, 
                            color=text_color
                        ),
                        annotations = [dict(
                            x=0.5,
                            y=0.1,
                            xref='paper',
                            yref='paper',
                            showarrow = True
                        )]
                    ).update_layout(margin={"r":0,"t":100,"l":10,"b":0},)
    return figure

# Create world map for visa statistics
worldmap_card = html.Div([
                    dbc.Card(
                        dbc.CardBody([
                            dcc.Graph(
                                id = "worldmap",
                                hoverData={'points': [{'location': 'Germany'}]}     
                            ) 
                        ])
                    ),  
                ])

# Histogram displaying map statistics in detail and ordered by country
def drawBarplot(data = df, feature = "Visas issued"):
    # Plot the bar chart
    figure = px.bar(
                        x=data['Country'],
                        y=data[str(feature)], 
                        height=450,
                        labels={'x':'Country', 'y':str(feature)},
                    ).update_layout(
                        template='plotly_dark',
                        plot_bgcolor= 'rgba(0, 0, 0, 0)',
                        paper_bgcolor= 'rgba(0, 0, 0, 0)',
                        margin={"r":0,"t":0,"l":0,"b":0}
                    )
    figure.update_xaxes(tickangle=45)
    
    return figure


# Create container for barplot
barplot_card = dbc.Card(
            dbc.CardBody(
                [
                    dcc.Graph(
                        id = "barplot",
                        config={
                            'displayModeBar': False,
                        }
                    ) 
                ]
            )
        )

# Correlation scatter plot with size displaying a third feature
def drawBubblePlot(data = df, feature_x = "Visas issued", feature_y = "Visas denied", country_code = None):

    figure = px.scatter(data, # plot for selected country
                    x=feature_x,
                    y=feature_y,
                    size="Number of visa applications", 
                    #color="Schengen country",
                    size_max=60).update_layout(
                                showlegend=False,
                                template='plotly_dark',
                                plot_bgcolor= 'rgba(0, 0, 0, 0)',
                                paper_bgcolor= 'rgba(0, 0, 0, 0)',
                                margin={"r":0,"t":0,"l":0,"b":0}
                                )

    # Highlight points for selected country of origin
    # Extract data points
    df_origin_country = data[data['Country code'].str.contains(country_code)] # includes all rows for selected Schengen countries
    x = df_origin_country[feature_x]
    y = df_origin_country[feature_y]

    if country_code:
        figure.add_trace(go.Scatter(
                            x=x, 
                            y=y,
                            opacity=0.8,
                            mode = 'markers',
                            marker_size = 30,
                            marker_color = "orange"))

    return figure

# Create container for barplot
bubbleplot_card = dbc.Card(
            dbc.CardBody(
                [
                    dcc.Graph(
                        id = "bubble_plot",
                        config={
                            'displayModeBar': False,
                        }
                    ) 
                ]
            )
        )


# Time series plot for each feature
def drawLinePlot(data = df, feature_x = "Year", feature_y = "Visas denied"):

    figure = px.scatter(data, # plot for selected country
                    x=feature_x,
                    y=feature_y,
                    size_max=60).update_layout(
                                showlegend=False,
                                #yaxis_range=[0,max_yaxis],
                                xaxis_range=[min_time,max_time],
                                template='plotly_dark',
                                plot_bgcolor= 'rgba(0, 0, 0, 0)',
                                paper_bgcolor= 'rgba(0, 0, 0, 0)',
                                margin={"r":0,"t":0,"l":0,"b":0}
                                )
    figure.update_traces(mode='lines+markers')
    figure.update_xaxes(showgrid=False)
    #fig.update_layout(yaxis_range=[-3,3])
    figure.add_annotation(x=0, y=0.85, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left',
                       text=feature_y)

    return figure



# Create container for barplot
lineplot_card = dbc.Card(
            dbc.CardBody(
                [
                    dcc.Graph(
                        id = "line_plot",
                        config={
                            'displayModeBar': False,
                        }
                    ) 
                ]
            )
        )


# Define dropdown field
def dropdown(label, label_list):
    # Remove nans
    list_items = label_list[~pd.isnull(label_list)]
    # Convert all features to lower case to allow ordering
    #list_items = [x.capitalize() for x in list_items]
    # Sort items alphabetically
    list_items.sort()
    # Create dictionary with labels and name to pass to the dropdown list
    list_items = [{'label':name, 'value':name} for name in list_items]

    return  html.Div([
        dbc.Card(
            dbc.CardBody([
                #dcc.Dropdown(id = "dd", label = "dfdf", value = "sd")
                html.H6(label),
                dcc.Dropdown(id = label, options=list_items, \
                searchable = True, value =list_items[0].get("label")), # first_label
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
                    dcc.RangeSlider(
                                    id='time_slider',
                                    min = min_time, 
                                    max = max_time, 
                                    step = 1, 
                                    value=[min_time, max_time],
                                    allowCross=False,
                                    marks={
                                            2014: '2014',
                                            2016: '2016',
                                            2018: '2018',
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

# Define text color
text_color = "#9F9F9F"

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
                    dropdown(label = "Schengen country", label_list = df["Schengen country"].unique()),#, first_label= "Germany"),
                    dropdown(label = "Country feature 1", label_list = np.array(feature_list)),#, first_label= "All countries"), # Column pandas index needs conversion to array to allow sorting
                    dropdown(label = "Country feature 2", label_list = np.array(feature_list)),#, first_label= "All countries"),
                    timeSlider(),
                    html.P(id = "item_display")
                ], width=4),
            ], align='top'), 
            html.Br(),
            dbc.Row([
                # Container for barplot
                dbc.Col([
                    barplot_card
                ], width=4),
                # Container for bubble chart
                dbc.Col([
                    bubbleplot_card
                ], width=4),
                dbc.Col([
                    lineplot_card
                ], width=4),
            ], align='center'),
            dbc.Row([
                dbc.Col([
                    daq.ToggleSwitch(id='my-toggle-switch', size=30, value=True),   #
                    html.Div(id='my-toggle-switch-output')
                ], width=4),
            ], align='left'),    
        ]), color = 'dark'
    )
])

################################
# Interactive callback functions
################################

# Callback function to update the map
@app.callback(
    Output('worldmap', 'figure'),
    [
        Input("Schengen country", "value"),
        Input("Country feature 1", "value"),
        Input("time_slider", "value")
    ],
)
# Function for callback
def update_worldmap(schengen_country, feature_1, year_range):

    # Filter by Schengen country if not all countries are selected
    if schengen_country != "All countries":
        df_schengen_country = df[df['Schengen country'].str.contains(schengen_country)] # includes all rows for selected Schengen countries

    # Filter dataset by year range
    df_filtered_year = df_schengen_country[(df_schengen_country['Year'] >= year_range[0]) & (df_schengen_country['Year'] <= year_range[1])]

    # Display selected feature on worldmap
    worldmap = drawWorldMap(data = df_filtered_year, feature = feature_1)
    
    return worldmap

# Callback function for barplot
@app.callback(
    Output('barplot', 'figure'),
    Output('my-toggle-switch-output', 'children'),    
    Input('my-toggle-switch', 'value'),
    Input("Country feature 1", "value"),
    Input("Schengen country", "value"),
    Input("time_slider", "value")
)
def update_barplot(toggle, feature, schengen_country, year_range):
    
    # Filter by Schengen country if not all countries are selected
    if schengen_country != "All countries":
        df_schengen_country = df[df['Schengen country'].str.contains(schengen_country)] # includes all rows for selected Schengen countries
    # Filter dataset by year range
    df_filtered_year = df_schengen_country[(df_schengen_country['Year'] >= year_range[0]) & (df_schengen_country['Year'] <= year_range[1])]
    # Calculate median across all years
    df_filtered_year = df_filtered_year.groupby('Country').median()[feature].reset_index()
    
    if toggle == False:
        df_filtered_year = pd.DataFrame(df_filtered_year.sort_values(by=[str(feature)], ascending=False)).reset_index()
        df_filtered_year = df_filtered_year.head(10)
    else:
        df_filtered_year = pd.DataFrame(df_filtered_year.sort_values(by=[str(feature)], ascending=True)).reset_index()
        df_filtered_year = df_filtered_year.head(10)
    # Draw bar plot with selected feature
    barplot = drawBarplot(data = df_filtered_year, feature = feature)
    
    return barplot, 'Change order: {}.'.format(toggle)


# Callback to update bubble plot by the country, where the user hovers over
@app.callback(
    Output("bubble_plot", "figure"),
    Input("Schengen country", "value"),
    Input('worldmap', 'hoverData'),
    Input("Country feature 1", "value"),
    Input("Country feature 2", "value"),
    Input("time_slider", "value"))
# Function to update bubble plot
def update_bubbleplot(schengen_country, hoverData, feature_1, feature_2, year_range):

    # Filter by Schengen country if not all countries are selected
    if schengen_country != "All countries":
        df_schengen_country = df[df['Schengen country'].str.contains(schengen_country)] # includes all rows for selected Schengen countries

    # Filter dataset by year range
    df_filtered_year = df_schengen_country[(df_schengen_country['Year'] >= year_range[0]) & (df_schengen_country['Year'] <= year_range[1])]

    # Draw bubbleplot
    bubbleplot = drawBubblePlot(data = df_filtered_year, 
                                        feature_x = feature_2, 
                                        feature_y = feature_1, 
                                        country_code = hoverData['points'][0]['location'])

    return bubbleplot


# Callback to update line plot by the country, where the user hovers over
@app.callback(
    Output('line_plot', 'figure'),
    Input("Schengen country", "value"),
    Input('worldmap', 'hoverData'),
    Input("Country feature 1", "value"),
    Input("time_slider", "value"))
# Function to update line plot
def update_lineplot(schengen_country, hoverData, feature_1, year_range):

    # Filter by Schengen country if not all countries are selected
    if schengen_country != "All countries":
        df_schengen_country = df[df['Schengen country'].str.contains(schengen_country)] # includes all rows for selected Schengen countries

    # Filter by country of origin
    # Extract country names from map hover data and the displayed alpha country code
    origin_country = hoverData['points'][0]['location']
    # Then filter by country
    df_origin_country = df_schengen_country[df_schengen_country['Country code'].str.contains(origin_country)] # includes all rows for selected Schengen countries

    # Filter dataset by year range
    df_filtered_year = df_origin_country[(df_origin_country['Year'] >= year_range[0]) & (df_origin_country['Year'] <= year_range[1])]

    # Plot bubble plot
    lineplot = drawLinePlot(data = df_filtered_year, feature_x = "Year", feature_y = feature_1)

    return lineplot


# Run the dashbord on a local server
if __name__ == "__main__":
    app.run_server(debug=True, port=8050, host='0.0.0.0')