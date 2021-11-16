import numpy as np
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go

def compile_data(borough, observable, res_dir):

    file_list = os.listdir(res_dir)
    borough_files = [res_dir + x for x in file_list if borough in x.split('-') and 'latest.csv' not in x.split('-')]
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

def create_traces(ds, obs):
    return [
        go.Scatter(
        name=obs,
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

def plot_aggregated_data(ds, observable):

    traces = []
    for obs in observable:
        ds = compile_data(borough, obs, res_dir)
        traces.extend(create_traces(ds, obs))

    fig = go.Figure(traces)

    return fig

if __name__ == '__main__':
    res_dir = '/home/arindam/Dropbox/FADE/src/Results/'
    borough = 'westminster'
    observable = ['infectious', 'hospital bed occupancy', 'susceptible']
    ds = compile_data(borough, observable, res_dir)
    fig = plot_aggregated_data(ds, observable)
    fig.update_layout(
        title=borough
    )

    fig.show()