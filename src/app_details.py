import os
import subprocess
import yaml

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

from jupyter_dash import JupyterDash

from web_extract import get_osm_id_from_web, get_age_dist, get_borough_options, get_london_map, get_pop_table_from_web
from plot_functions import generate_map, dem_plot, plot_results_overall, plot_results_hospitals

from main_dash import app

def app_design(file_paths):

    get_london_map(search_path=file_paths['data_path'])
    pop_data = get_pop_table_from_web()
    borough_options = get_borough_options(pop_data)

    heading = dcc.Markdown('## **FADE: FACS Application Dashboard for End-users**')

    heading1 = html.H4('Select the Scenario')
    heading2 = html.H4('Enter the simulation period in days')
    heading3 = html.H4('Enter the number of runs')

    borough_select = dcc.Dropdown(id='Select_Borough', options=borough_options, multi=False)

    scenario_select = dcc.Dropdown(
                    options=[
                        {'label': 'No Measures', 'value': 'no-measures'},
                        {'label': 'Extend Lockdown', 'value': 'extend-lockdown'},
                        {'label': 'Periodic Lockdown', 'value': 'periodic-lockdown'},
                        {'label': 'Open All', 'value': 'open-all'},
                        {'label': 'Open Schools', 'value': 'open-schools'},
                        {'label': 'Open Shopping', 'value': 'open-shopping'},
                        {'label': 'Open Leisure', 'value': 'open-leisure'},
                        {'label': 'Work at 50%', 'value': 'work50'},
                        {'label': 'Work at 70%', 'value': 'work75'},
                        {'label': 'Work at 100%', 'value': 'work100'},
                        {'label': 'Dynamic Lockdown', 'value': 'dynamic-lockdown'},
                        {'label': 'UK Forecast', 'value': 'uk-forecast'},
                    ],
                    id='Select_Scenario',
                    multi=False
                )

    sim_time = dbc.Input(id='range', type='number', min=10, max=5000, step=1)
    n_runs = dbc.Input(id='run_no', type='number', min=1, max=5000, step=1)
        
    status_bar = html.Div(id='Status', children='Click the button')

    layout = html.Div([
        
        dbc.Row(
            [
                dbc.Col(heading, width={'size': 6}),
                dbc.Col(html.Img(src=app.get_asset_url('bitmap.png'), height=60), width={'offset': 3}),
            ]
        ),
        
        html.H2("Select the Borough"),
        
        html.Div([borough_select], style={'columnCount': 1}),    

        
        html.Div([
                dbc.Button('Prepare Input', id='Run', n_clicks=0, block=True),
        ], 
                style={'columnCount': 1}
                ),    

        
        dbc.Collapse([
            html.H2("Select Simulation Parameters"),
            
            dbc.Row(
                [
                    dbc.Col(heading1),
                    dbc.Col(heading2),
                    dbc.Col(heading3),
                ]
            ),
            
            dbc.Row(
                [
                    dbc.Col(scenario_select),
                    dbc.Col(sim_time),
                    dbc.Col(n_runs),
                ]
            ),
            
            html.Div([
                dbc.Button('Run Simulation', id='Execute', n_clicks=0, block=True),
            ],
                style={'columnCount': 1}),    
        ], id='Simulate_Block', is_open=True),

        status_bar,
        
        dbc.Tabs([
            dbc.Tab(label="Input", tab_id="input_tab"),
            dbc.Tab(label="Output", tab_id="output_tab"),

        ],id='tabs', active_tab='input_tab',),
        
        html.Div(id='Graphs', style={'columnCount': 2}),
        
        dbc.Collapse([
            html.Div([
                dcc.Graph(id='Map', figure={}),
                dcc.Graph(id='Population', figure={}),
            ],
                style={'columnCount': 2}),    
        ], is_open=False),
            
        dbc.Collapse([
            html.Div([
                dcc.Graph(id='Result', figure={})        
            ],
                style={'columnCount': 1}),    
        ], is_open=False),

        ])

    return layout


@app.callback(
    [dash.dependencies.Output('Status', 'children'),
    dash.dependencies.Output('Simulate_Block', 'is_open'),
    dash.dependencies.Output('Graphs', 'children'),],
    [dash.dependencies.Input('Run', 'n_clicks'),
     dash.dependencies.Input('Execute', 'n_clicks'),
    dash.dependencies.Input('tabs', 'active_tab'),
    dash.dependencies.State('Select_Borough', 'value'),
    dash.dependencies.State('Select_Scenario', 'value'),
    dash.dependencies.State('range', 'value'),
    dash.dependencies.State('run_no', 'value'),])
def update_app(n_clicks_collect, n_clicks_simulate, tab, borough, scenario, time, n_runs):

    with open('src/file_paths.yml', 'r') as f:
        fp = yaml.safe_load(f)

    pop_data = get_pop_table_from_web()
    osm_id_data = get_osm_id_from_web()
    age_dist_df = get_age_dist(pop_data, fp['data_path']+'age.csv')

    ctx = dash.callback_context

    if n_clicks_collect == 0 and n_clicks_simulate == 0:

        subprocess.call('cp ' + fp['data_path']+'age.csv ' + fp['trial_data_path']+'age-dist.csv', shell=True)
        
        s = 'Select a borough and click Prepare Input'
        c = False
        g = 'Nothing to show'
        
    elif borough == None:
        
        s = 'Select a borough first!'
        c = False
        g = 'Nothing to show'
        
    else:
        
        cmd = 'cp ' + fp['data_path'] + borough + '_data_combined.csv ' + fp['trial_data_path'] + borough.lower() + '_buildings.csv'
        subprocess.call(cmd, shell=True)

        
        fig1 = generate_map(borough, osm_id_data, pop_data, path=fp['data_path'])
        fig2 = dem_plot(borough, age_dist_df)
        
        s = 'Showing Information about ' + borough
        c = True
        
        click_button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if click_button_id == 'Execute':
            
            if scenario != None and time != None and n_runs != None:
                for i in range(int(n_runs)):
                    print('Run', i+1)
                    cmd = 'bash ' + fp['code_path'] + 'facs_script.sh '  + borough.lower() + ' ' + str(time) + ' ' + scenario
                    subprocess.call(cmd, shell=True)
                s = 'Run Complete'
            else:
                s = 'Error'

        
        if tab == 'input_tab':
            g = [dcc.Graph(id='Map', figure=fig1), dcc.Graph(id='Population', figure=fig2),]
        else:
            res_file = borough.lower() + '-latest.csv'
            if res_file in os.listdir('Results'):
                fig3 = plot_results_overall(fp['results_path']+res_file)
                fig4 = plot_results_hospitals(fp['results_path']+res_file)
                g = [dcc.Graph(id='Map', figure=fig3), dcc.Graph(id='Population', figure=fig4),]
            else:
                g = 'Nothing to Show'
        
    return [s, c, g]