'''
webscraper that gets data & images from the multiple mrtg websites
'''

import pandas as pd
from bs4 import BeautifulSoup
import requests

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
    for item in soup.findAll("tr", {"class":"out"}):
        for i in item.findAll("td"):
            if 'Traffic' not in i.text:
                out_lst.append(i.text)

    for item in soup.findAll("img", {"alt":"day"}):
        # print(item["src"])
        mrtg = item["src"]

    day_cur_in = float(in_lst[2].split()[0])
    day_cur_out = float(out_lst[2].split()[0])

    return (day_cur_in, day_cur_out, mrtg, port)

# convert df to dictionary of congestion_data
def convert_df_to_dict(df):
    congestion_data = {}
    space_list={'Duffield atrium':'green','ECE lounge':'green','Upson 2nd floor':'green','Upson 3rd floor':'green','CIS lounge':'green','Rhodes 3rd floor':'green','Rhodes 4th floor':'green','Rhodes 5th floor':'green'}
    
    for spaces in space_list:
        filter = df['Location Name'] == spaces
        filtered_df = df.loc[filter]
        # print(filtered_df)
        congestion_data[spaces] = float(filtered_df['In'].sum()) + float(filtered_df['Out'].sum())

    return congestion_data
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
    
    name_lst = []
    port_lst = []
    in_lst = []
    out_lst = []
    mrtg_lst = []

    for url, location in urls: 
        result = daily_in_out(url)
        name_lst.append(location) 
        port_lst.append(result[3])
        in_lst.append(result[0])
        out_lst.append(result[1])
        mrtg_lst.append(result[2])

    df = pd.DataFrame(
        {'Port Name': port_lst,
         'Location Name': name_lst,
         'In': in_lst,
         'Out': out_lst,
         'Graph': mrtg_lst
        })

    print(df)
    print(convert_df_to_dict(df))
if __name__ == "__main__":
    main()