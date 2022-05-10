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

def main():
    urls = ['http://mrtg.cit.cornell.edu/switch/WorkDir/phillips1-5400.252.html', # ECE loung
            'http://mrtg.cit.cornell.edu/switch/WorkDir/duffield2-5400.120.html', # Duff atrium near phillips
            'http://mrtg.cit.cornell.edu/switch/WorkDir/phillips2-5400.132.html', # Duff atrium near upson
            'http://mrtg.cit.cornell.edu/switch/WorkDir/duffield2-5400.119.html', # Duff atrium near duffield
            'http://mrtg.cit.cornell.edu/switch/WorkDir/phillips2-5400.131.html', # Mattin's
            'http://mrtg.cit.cornell.edu/switch/WorkDir/upson3-5400r.33.html',# upson 2nd flr middle lounge
            'http://mrtg.cit.cornell.edu/switch/WorkDir/upson3-5400r.3.html', # upson 2nd flr stairs lounge
            'http://mrtg.cit.cornell.edu/switch/WorkDir/upson5-5400r.71.html', # upson 3rd flr stairs lounge
            'http://mrtg.cit.cornell.edu/switch/WorkDir/rhodes2-2-5400.194.html', # rhodes CIS entrance
            'http://mrtg.cit.cornell.edu/switch/WorkDir/rhodes2-2-5400.202.html', # CIS 1
            'http://mrtg.cit.cornell.edu/switch/WorkDir/rhodes2-2-5400.203.html', # CIS 2
            'http://mrtg.cit.cornell.edu/switch/WorkDir/rhodes2-2-5400.204.html', # CIS 3
            'http://mrtg.cit.cornell.edu/switch/WorkDir/rhodes3-1-5400.37.html', # rhodes 3rd flr
            'http://mrtg.cit.cornell.edu/switch/WorkDir/rhodes3-1-5400.38.html', # rhodes 3rd flr 2
            'http://mrtg.cit.cornell.edu/switch/WorkDir/rhodes4-1-5400.25.html', # rhodes 4th flr 
            'http://mrtg.cit.cornell.edu/switch/WorkDir/rhodes4-1-5400.26.html', # rhodes 4th flr 2
            'http://mrtg.cit.cornell.edu/switch/WorkDir/rhodes5-1-5400.25.html' # rhodes 5th flr
            ]
    
    port_lst = []
    in_lst = []
    out_lst = []
    mrtg_lst = []

    for url in urls: 
        result = daily_in_out(url)
        port_lst.append(result[3])
        in_lst.append(result[0])
        out_lst.append(result[1])
        mrtg_lst.append(result[2])

    df = pd.DataFrame(
        {'Port Name': port_lst,
         'In': in_lst,
         'Out': out_lst,
         'Graph': mrtg_lst
        })

    print(df)
if __name__ == "__main__":
    main()