'''
webscraper that gets data from the mrtg website
'''

import pandas as pd
from bs4 import BeautifulSoup
import requests

# page to scrape
url = 'http://mrtg.cit.cornell.edu/switch/WorkDir/duffield1-5400.21.html'
request = requests.get(url, timeout=5)
soup = BeautifulSoup(request.text, features="html.parser")

# print(content.get_text())

# list to store data 
in_lst = []
out_lst = []
# graph = ['Daily Max', 'Daily Avg', 'Daily Cur', 'Weekly Max', 'Weekly Avg', 'Weekly Cur', 'Montly Max', 'Montly Avg', 'Montly Cur', 'Yearly Cur']
# for i in soup.findAll("div", {"class":"graph"}):
# for i in soup.findAll("h2", string=lambda text: "daily" in text.lower()):
    # print((j.find("th", {"scope":"row"})).text)

for item in soup.findAll("tr", {"class":"in"}):
    for i in item.findAll("td"):
        if 'Traffic' not in i.text:
            in_lst.append(i.text)
for item in soup.findAll("tr", {"class":"out"}):
    for i in item.findAll("td"):
        if 'Traffic' not in i.text:
            out_lst.append(i.text)

df = pd.DataFrame(
    {'In': in_lst,
     'Out': out_lst
    })

day_avg_in = float(df['In'][1].split()[0])
day_avg_out = float(df['Out'][1].split()[0])

print(df)
print("Daily Avg In: ", day_avg_in, df['In'][1].split()[1])
print("Daily Avg Out: ", day_avg_out, df['In'][1].split()[1])

