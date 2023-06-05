# %%
import http.client, urllib.parse
from rich import print
import pandas as pd
# %%
# Sources
sources = [
    'abc-news',
    'associated-press',
    'cbs-news',
    'cnn',
    'fox-news',
    'msnbc',
    'nbc-news',
    'reuters',
    'the-washington-post',
    'usa-today'
]

# Load dataset of incidents
incidents = pd.read_csv("./data/WI/dataset.csv")
# Convert date column to datetime
incidents[incidents.columns[1]] = pd.to_datetime(incidents[incidents.columns[1]])
# Test case is 2022 incidents where the description is one of:
# Death / Alleged maltreatment
incidents = incidents[
                        (incidents[incidents.columns[1]].dt.year == 2022) & # filter by year
                        (incidents[incidents.columns[11]])   # filter by description being Serious Injury
]
# Reanme columns
incidents.rename(columns={
    "Date of  Incident" : "date", 
    "Practice  Review?" : "practice_review", 
    "90 Day" : "day_90", "6 Month" : "month_6", 
    }, inplace=True)
# Lowercase all columns
incidents.columns = [col.lower() for col in incidents.columns]
# %%
# Example first incident
incident = incidents.iloc[0]
# Construct query
api_key = "1a2a5e1d84c61d65e8772511fe821558"
country = "us"
state = "Wisconsin"
county = incident.county
# child_q = "child OR baby OR kid OR youth OR minor OR youngster OR toddler OR infant"
child_q = "child"
# death_q = "death OR passing OR demise OR decease OR fatality"
death_q = "death"
# query = f"+{county} +{state} +({death_q}) +({child_q}) OR (Child AND Protective AND Services)"
query = f"{county} {state} {death_q} {child_q}"
from_date = incident.date.isoformat()[:10]
to_date = (incident.date + pd.DateOffset(days=30)).isoformat()[:10]
language = "en"
params = urllib.parse.urlencode({
    'access_key': api_key,
    "sources" : ",".join(sources),
    "languages": language,
    "countries": country,
    # "date": f"{from_date},{to_date}",
    "limit": 100,
    "offset": 0,
    "keywords": query
    })
# %%
# Initialize the News API client
conn = http.client.HTTPConnection('api.mediastack.com')
# %%

# Make the request
conn.request('GET', '/v1/news?{}'.format(params))
res = conn.getresponse()
data = res.read()
# %%
# %%
