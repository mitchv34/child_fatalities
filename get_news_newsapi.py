# %%
from newsapi import NewsApiClient
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
# Test case is last month incidents where the description is one of:
# Death / Alleged maltreatment
incidents = incidents[
#                         (incidents[incidents.columns[1]].dt.year == 2022) & # filter by year
                        (incidents[incidents.columns[1]] >= pd.to_datetime("2023-04-01")) & # filter by year
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
incident = incidents.iloc[2]
# Construct query
state = "Wisconsin"
county = incident.county
child_q = "child OR baby OR kid OR youth OR minor OR youngster OR toddler OR infant"
death_q = "death OR kill OR demise OR decease OR fatality"
query = f"+{county} +{state} +({death_q}) +({child_q}) OR (Child AND Protective AND Services)"
from_date = incident.date.isoformat()
to_date = (incident.date + pd.DateOffset(days=30)).isoformat()
language = "en"

print(query)

# %%
# Initialize the News API client
newsapi = NewsApiClient(api_key='fbba16f97f5c47868038e725a0334a58')
# %%
# Make the request
articles = newsapi.get_everything(  q=query,
                                    sources=",".join(sources),
                                    from_param=from_date,
                                    to=to_date,
                                    language=language,
                                    sort_by='relevancy',
                                    page=1)
# %%
