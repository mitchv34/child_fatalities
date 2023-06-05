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
