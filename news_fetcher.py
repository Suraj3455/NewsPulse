import requests
import pandas as pd

def fetch_top_headlines(api_key, category=None, country=None):
    base_url = "https://newsapi.org/v2/top-headlines"
    params = {
        'apiKey': api_key,
        'pageSize': 30  # or more if needed
    }

    if category:
        params['category'] = category
    if country:
        params['country'] = country

    response = requests.get(base_url, params=params)
    data = response.json()

    if data.get("status") != "ok" or not data.get("articles"):
        return pd.DataFrame()  # return empty if no articles

    articles = data['articles']

    df = pd.DataFrame([{
        'title': article['title'],
        'description': article['description'],
        'url': article['url'],
        'source': article['source']['name']
    } for article in articles])

    return df
