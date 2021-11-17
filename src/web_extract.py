import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

# ## Web Sources

def get_pop_table_from_web():

    url = 'https://en.wikipedia.org/wiki/List_of_London_boroughs'
    page = requests.get(url)
    parsed = BeautifulSoup(page.text, 'html.parser')

    london_table=parsed.find('table',{'class':"wikitable"})

    wiki_data = pd.DataFrame(pd.read_html(str(london_table))[0])

    pop_data = wiki_data[['Borough', 'Population (2019 est)[1]']]
    pop_data = pop_data.rename(columns={'Population (2019 est)[1]': 'Population'})
    pop_data.Borough = pop_data.Borough.apply(lambda x: x[:x.index('[')] if '[' in x else x)
    pop_data.Borough = pop_data.Borough.str.strip()
    pop_data.Borough = pop_data.Borough.apply(lambda x: x.replace(' ', '_'))

    return pop_data

def get_osm_id_from_web():

    url = 'https://wiki.openstreetmap.org/wiki/London_borough_boundaries'
    page = requests.get(url)
    parsed = BeautifulSoup(page.text, 'html.parser')

    london_table=parsed.find('table',{'class':"wikitable"})

    wiki_data = pd.DataFrame(pd.read_html(str(london_table))[0])

    osm_id_data = wiki_data[['Administrative area.2', 'OSM relation']]
    osm_id_data = osm_id_data.drop([0,len(osm_id_data)-1,len(osm_id_data)-2])
    osm_id_data = osm_id_data.sort_values('Administrative area.2', ascending=True)
    osm_id_data = osm_id_data.rename(columns={'Administrative area.2': 'Borough', 'OSM relation': 'OSM_id'})
    osm_id_data.Borough = osm_id_data.Borough.apply(lambda x: x[:x.index(' (')] if ' (' in x else x)
    osm_id_data = osm_id_data.reset_index(drop=True)
    osm_id_data.Borough = osm_id_data.Borough.apply(lambda x: x.replace(' ', '_'))

    return osm_id_data

def get_borough_options(pop_data):

    borough_options = []
    for b in pop_data.Borough:
        borough_options.append({'label': b, 'value': b.replace(' ', '_')})
    return borough_options

def get_london_map(search_path):

    if 'greater_london.osm.pbf' not in os.listdir(search_path):

        url = 'http://download.geofabrik.de/europe/great-britain/england/greater-london-latest.osm.pbf'

        print('Downloading Greater London Map...')
        r = requests.get(url)
        print('Download Complete.')
        print('Saving Greater London Map...')
        with open('Data/greater_london.osm.pbf', 'wb') as ff:
            ff.write(r.content)

def get_age_dist(pop_data, store_path):

    age_dist = pd.read_csv('https://data.london.gov.uk/download/office-national-statistics-ons-population-estimates-borough/42672cc2-f789-4652-b952-6a332066c804/population-estimates-single-year-age.csv')
    age_dist.Borough = age_dist.Borough.apply(lambda x: x.replace(' ', '_'))

    dd = age_dist[age_dist['Borough'].isin(list(pop_data['Borough']))]
    dd = dd[dd['Year'] == 2015]
    dd = dd.reset_index(drop=True)

    for ii in range(90):
        dd['A '+str(ii)] = pd.to_numeric(dd['M '+str(ii)]) + pd.to_numeric(dd['F '+str(ii)])
    dd['A 90'] = pd.to_numeric(dd['M 90+']) + pd.to_numeric(dd['F 90+'])

    cols = ['Borough']
    for i in range(91):
        cols.append('A '+str(i))

    rc = {}
    for i in range(91):
        rc['A '+str(i)]=str(i)
        
    ad = dd[cols]
    ad = ad.rename(columns=rc)

    ad = ad.rename(columns={'Borough': 'index'})
    ad = ad.set_index('index').transpose()
    ad = ad.reset_index()
    ad = ad.rename(columns={'index': 'Age'})

    add = ad.set_index('Age')
    add['Greater_London'] = add.sum(axis=1)
    add.to_csv(store_path)


    addf = pd.read_csv(store_path, index_col='Age')

    return addf
