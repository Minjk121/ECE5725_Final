'''
webscraper that gets data from the multiple mrtg websites
'''

import pandas as pd
from bs4 import BeautifulSoup
import requests
from zmq import device

# returns tuple of daily average (in, out)
def daily_in_out(url):
    # page to scrape
    # url = 'http://mrtg.cit.cornell.edu/switch/WorkDir/duffield1-5400.21.html'
    request = requests.get(url, timeout=5)
    soup = BeautifulSoup(request.text, features="html.parser")

    in_lst = []
    out_lst = []

    for item in soup.findAll("tr", {"class":"in"}):
        for i in item.findAll("td"):
            if 'Traffic' not in i.text:
                in_lst.append(i.text)
    for item in soup.findAll("tr", {"class":"out"}):
        for i in item.findAll("td"):
            if 'Traffic' not in i.text:
                out_lst.append(i.text)

    day_avg_in = float(in_lst[1].split()[0])
    day_avg_out = float(out_lst[1].split()[0])

    return (day_avg_in, day_avg_out)

def main():
    urls = ['http://mrtg.cit.cornell.edu/switch/WorkDir/duffield1-5400.21.html',
    'http://mrtg.cit.cornell.edu/switch/WorkDir/duffield1-5400.49.html']
    
    device_lst = []
    in_lst = []
    out_lst = []

    for url in urls: 
        device_lst.append(url.split('/')[-1].replace(".html",""))
        result = daily_in_out(url)
        in_lst.append(result[0])
        out_lst.append(result[1])

    df = pd.DataFrame(
        {'Device Name': device_lst,
         'In': in_lst,
         'Out': out_lst
        })
    print(df)
if __name__ == "__main__":
    main()