import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from graph_extract import extract_boundary

# ## Map Plot

def generate_map(region=None, osm_id_data=None, pop_data=None, path=None):
        
    if region == None:
        region = 'greater_london'

    df = extract_boundary(region, osm_id_data, pop_data, path)
    
    df['Type'] = 'boundary'
    df['Area'] = 0
    df = df[['Type', 'Longitude', 'Latitude', 'Area']]
    
    if region == 'greater_london':
        zoom = 8.5
    else:
        zoom = 10.0
    
    if region != 'greater_london':
        ddf = pd.read_csv(path + region + '_data_combined.csv', names=['Type', 'Longitude', 'Latitude', 'Area'])
        fig = px.scatter_mapbox(ddf, lon='Longitude', lat='Latitude', color='Type', zoom=zoom)
        fig.add_trace(px.line_mapbox(df, lon='Longitude', lat='Latitude').data[0])
        fig.update_traces(line=dict(color="Black", width=5))
    else:
        fig = px.line_mapbox(df, lon='Longitude', lat='Latitude', zoom=zoom)
        fig.update_traces(line=dict(color="Black", width=5))
        
#     fig = px.scatter_mapbox(df, lat='Latitude', lon='Longitude', color='Amenity Type', zoom=10.3)

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    return fig


# ## Demographics Plot Functions

def dem_plot(region=None, age_dist_df=None):
    if region == None:
        region = 'Greater_London'
    fig = px.line(age_dist_df[region], labels={'value': 'Population'}, title='Population Distribution by Age')
    return fig


# ## Results Plot Function

def plot_results_overall(filename):

    df = pd.read_csv(filename)
    df = df.drop('Unnamed: 0', axis=1)
    df = df.rename(columns={'#time': 'time'})
    df = df.set_index('time')
    
    df = df[['susceptible', 'exposed', 'infectious', 'recovered', 'dead']]
    
    fig = px.line(df, labels={'value': 'Population', 'time':'No. of Days'}, title='Number of Cases over Time')
    
    return fig

def plot_results_hospitals(filename):

    df = pd.read_csv(filename)
    df = df.drop('Unnamed: 0', axis=1)
    df = df.rename(columns={'#time': 'time'})
    df = df.set_index('time')
    
    df = df[['num hospitalisations today', 'hospital bed occupancy', 'cum num hospitalisations today']]
    
    fig = px.line(df, labels={'value': 'Population', 'time':'No. of Days'}, title='Hospitalisations over Time')
    
    return fig

## Aggregate Plot

def compile_data(borough, observable, scenario, res_dir):

    file_list = os.listdir(res_dir)
    borough_files = [res_dir + x for x in file_list if borough in x.split('-') and scenario in x.split('-') and 'latest.csv' not in x.split('-')]
    df = [pd.read_csv(x) for x in borough_files]
    ll = list((x[observable] for x in df))
    for i in range(len(ll)):
        ll[i].name = 'Trial_' + str(i+1)
    dd = pd.concat(ll, axis=1)

    assert not dd.isnull().values.any()

    dd['mean'] = dd.mean(axis=1)
    dd['std'] = dd.std(axis=1)
    ds = pd.concat([dd['mean'], dd['mean'] + (1.96/np.sqrt(len(ll)))*dd['std'], dd['mean'] - (1.96/np.sqrt(len(ll)))*dd['std']], axis=1)
    ds = ds.rename(columns={0: 'upper', 1: 'lower'})
    ds = ds.reset_index()
    ds = ds.rename(columns={'index': 'time'})

    return ds

def create_traces(ds, obs, label):
    return [
        go.Scatter(
        name=label,
        x=ds['time'],
        y=ds['mean'],
        mode='lines',
        showlegend=True,
        ),

        go.Scatter(
        name='Upper',
        x=ds['time'],
        y=ds['upper'],
        mode='lines',
        showlegend=False,
        line=dict(width=0),
        ),

        go.Scatter(
        name='Lower',
        x=ds['time'],
        y=ds['lower'],
        mode='lines',
        showlegend=False,
        line=dict(width=0),
        fillcolor='rgba(68, 68, 68, 0.3)',
        fill='tonexty'
        )
    ]

def plot_aggregated_data(borough, observable, scenario, res_dir):

    traces = []
    for sc in scenario:
        if sc == 'no':
            label = 'No measures'
        elif sc == 'uk':
            label = 'UK measures'
        for obs in observable:
            ds = compile_data(borough, obs, sc, res_dir)
            traces.extend(create_traces(ds, obs, label=label))

    fig = go.Figure(traces)

    return fig