'''
webscraper that gets data & images from the multiple mrtg websites
'''

import pandas as pd
from bs4 import BeautifulSoup
import requests
import matplotlib.pyplot as plt
import pandas as pd
# from pandas.plotting import table
import numpy as np
import dataframe_image as dfi

def save_df_as_image(df, path="dashboard_img.png"):
    df_styled = df.style.background_gradient() #adding a gradient based on values in cell
    dfi.export(df_styled, path)

# returns tuple of daily average (in, out)
def daily_in_out(url):
    # page to scrape
    request = requests.get(url, timeout=5)
    soup = BeautifulSoup(request.text, features="html.parser")

    in_lst = []
    out_lst = []
    mrtg = ""
    port = ""

    for item in soup.find("font", string=lambda text: "|" in text):
        port = item.split("|")[-1]
    for item in soup.findAll("tr", {"class":"in"}):
        for i in item.findAll("td"):
            if 'Traffic' not in i.text:
                in_lst.append(i.text)
                # print(i.text)
    for item in soup.findAll("tr", {"class":"out"}):
        for i in item.findAll("td"):
            if 'Traffic' not in i.text:
                out_lst.append(i.text)

    for item in soup.findAll("img", {"alt":"day"}):
        # print(item["src"])
        mrtg = item["src"]

    # print(in_lst[2])
    day_cur_in = float(in_lst[2].split()[0])
    day_cur_out = float(out_lst[2].split()[0])

    if "kb/s" in in_lst[2]:
        day_cur_in *= 0.001
    if "kb/s" in out_lst[2]:
        day_cur_out *= 0.001

    # print(day_cur_in)

    return (day_cur_in, day_cur_out, mrtg, port)

# convert df to dictionary of congestion_data
def convert_df_to_dict(df):
    congestion_data = {}
    space_list={'Duffield atrium':'green','ECE lounge':'green','Upson 2nd floor':'green','Upson 3rd floor':'green','CIS lounge':'green','Rhodes 3rd floor':'green','Rhodes 4th floor':'green','Rhodes 5th floor':'green'}
    congestion_menu={'Phillips':(1140,373),'Duffield':(932,467),'Upson':(1012,629),'Rhodes':(1200,872)}

    for spaces in space_list:
        filter = df['Location Name'] == spaces
        filtered_df = df.loc[filter]
        # print(filtered_df)
        congestion_data[spaces] = float(filtered_df['In'].sum()) + float(filtered_df['Out'].sum())

    for halls in congestion_menu:
        filter = df['Hall Name'] == halls.lower()
        filtered_df = df.loc[filter]
        congestion_data[halls] = float(filtered_df['In'].sum()) + float(filtered_df['Out'].sum())

    return congestion_data

# convert df to list of mrtg graphs
def convert_df_to_graph_lst(df, hall_name):
    filter = df['Hall Name'] == hall_name.lower()
    filtered_df = df.loc[filter]
    graph_lst = list(filtered_df['Graph'])
    return graph_lst
    
    
def convert_url_to_df(urls):

    name_lst = []
    hall_lst = []
    port_lst = []
    in_lst = []
    out_lst = []
    mrtg_lst = []

    for url, location in urls: 
        # hall_name = url.split('/')[-1].split('-')[0]
        result = daily_in_out(url)

        hall_name = result[3].split('-')[0]
        hall_lst.append(hall_name)
        name_lst.append(location) 
        port_lst.append(result[3])
        in_lst.append(result[0])
        out_lst.append(result[1])
        mrtg_lst.append(result[2])

    df = pd.DataFrame(
        {'Port Name': port_lst,
         'Hall Name': hall_lst,
         'Location Name': name_lst,
         'In': in_lst,
         'Out': out_lst,
         'Graph': mrtg_lst
        })
    return df
def main():
    urls = [('http://mrtg.cit.cornell.edu/switch/WorkDir/phillips1-5400.252.html', 'ECE lounge'),
            ('http://mrtg.cit.cornell.edu/switch/WorkDir/duffield2-5400.120.html', 'Duffield atrium'), # near phillips
            ('http://mrtg.cit.cornell.edu/switch/WorkDir/phillips2-5400.132.html', 'Duffield atrium'), # near upsonv
            ('http://mrtg.cit.cornell.edu/switch/WorkDir/duffield2-5400.119.html', 'Duffield atrium'), # near duffield
            ('http://mrtg.cit.cornell.edu/switch/WorkDir/phillips2-5400.131.html', 'Duffield atrium'), # Mattins
            ('http://mrtg.cit.cornell.edu/switch/WorkDir/upson3-5400r.33.html', 'Upson 2nd floor'), # middle
            ('http://mrtg.cit.cornell.edu/switch/WorkDir/upson3-5400r.3.html', 'Upson 2nd floor'), #stairs
            ('http://mrtg.cit.cornell.edu/switch/WorkDir/upson5-5400r.71.html', 'Upson 3rd floor'),
            ('http://mrtg.cit.cornell.edu/switch/WorkDir/rhodes2-2-5400.194.html', 'CIS lounge'),
            ('http://mrtg.cit.cornell.edu/switch/WorkDir/rhodes2-2-5400.202.html', 'CIS lounge'),
            ('http://mrtg.cit.cornell.edu/switch/WorkDir/rhodes2-2-5400.203.html', 'CIS lounge'),
            ('http://mrtg.cit.cornell.edu/switch/WorkDir/rhodes2-2-5400.204.html', 'CIS lounge'),
            ('http://mrtg.cit.cornell.edu/switch/WorkDir/rhodes3-1-5400.37.html', 'Rhodes 3rd floor'),
            ('http://mrtg.cit.cornell.edu/switch/WorkDir/rhodes3-1-5400.38.html', 'Rhodes 3rd floor'),
            ('http://mrtg.cit.cornell.edu/switch/WorkDir/rhodes4-1-5400.25.html', 'Rhodes 4th floor'),
            ('http://mrtg.cit.cornell.edu/switch/WorkDir/rhodes4-1-5400.26.html', 'Rhodes 4th floor'),
            ('http://mrtg.cit.cornell.edu/switch/WorkDir/rhodes5-1-5400.25.html', 'Rhodes 5th floor'),
            ]

    df = convert_url_to_df(urls)
    # print(df)
    # print(convert_df_to_graph_lst(df, 'Upson'))
    save_df_as_image(df)
    return df
    
    # data = convert_df_to_dict(df)
    # print(data)
    

if __name__ == "__main__":
    main()