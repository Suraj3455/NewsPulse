import streamlit as st
import requests
from textblob import TextBlob
from transformers import pipeline
from datetime import datetime
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
nltk.download('vader_lexicon')

# ✅ Page config (must be first)
st.set_page_config(page_title="NewsPulse", layout="wide")

# ✅ Session bookmarks
if 'bookmarks' not in st.session_state:
    st.session_state.bookmarks = []

# ✅ Load summarizer + sentiment analyzer
@st.cache_resource
def load_summarizer():
    return pipeline("summarization", model="facebook/bart-large-cnn")

summarizer = load_summarizer()
vader_analyzer = SentimentIntensityAnalyzer()

# ✅ NewsAPI Key
api_key = "380a2141d0b34d91931aa5a856a37d6f"

# ✅ News fetch function
def fetch_news(category=None, keyword=None, use_everything=False):
    if use_everything and keyword:
        url = f"https://newsapi.org/v2/everything?apiKey={api_key}&language=en&q={keyword}&sortBy=publishedAt"
    else:
        url = f"https://newsapi.org/v2/top-headlines?apiKey={api_key}&language=en"
        if category:
            url += f"&category={category}"
        if keyword:
            url += f"&q={keyword}"

    response = requests.get(url)
    return response.json().get("articles", [])

# ✅ Sentiment analyzer
def analyze_sentiment_all(article):
    text = (article.get("title", "") or "") + " " + (article.get("description", "") or "")
    blob_polarity = TextBlob(text).sentiment.polarity
    vader_scores = vader_analyzer.polarity_scores(text)
    pos = round(vader_scores['pos'] * 100, 1)
    neu = round(vader_scores['neu'] * 100, 1)
    neg = round(vader_scores['neg'] * 100, 1)
    return blob_polarity, pos, neu, neg

# ✅ Summarizer
def generate_summary(article):
    text = (article.get("content") or article.get("description") or "")
    if text and len(text) > 50:
        try:
            summary = summarizer(text, max_length=130, min_length=50, do_sample=False)
            return summary[0]['summary_text']
        except:
            return text
    else:
        return "No summary available."

# ✅ Sidebar controls
st.sidebar.title("🔍 Filter News")

search_mode = st.sidebar.radio("Search Mode", ["By Category", "By Keyword"])

use_everything = False
category = None
keyword = None

if search_mode == "By Category":
    category = st.sidebar.selectbox("Select News Category", ("general", "business", "sports", "technology", "entertainment"))

else:
    keyword = st.sidebar.text_input("Enter Keyword", value="India")
    use_everything = st.sidebar.checkbox("Use Full Archive (Everything API)", value=False)

# ✅ Page title
st.markdown("## 📰 NewsPulse: Real-Time Trending Topics & Sentiment Analyzer")

# ✅ Fetch News
articles = fetch_news(category=category, keyword=keyword, use_everything=use_everything)

# ✅ Sentiment Distribution
sentiments_total = {'Positive': 0, 'Neutral': 0, 'Negative': 0}

for article in articles:
    _, pos, neu, neg = analyze_sentiment_all(article)
    if pos > neu and pos > neg:
        sentiments_total['Positive'] += 1
    elif neg > pos and neg > neu:
        sentiments_total['Negative'] += 1
    else:
        sentiments_total['Neutral'] += 1

total_articles = sum(sentiments_total.values())

if total_articles > 0:
    st.write("### 📊 Overall Sentiment Distribution:")
    for sentiment, count in sentiments_total.items():
        percent = round((count / total_articles) * 100, 1)
        emoji = "🟢" if sentiment == "Positive" else "⚪" if sentiment == "Neutral" else "🔴"
        st.write(f"{emoji} {sentiment}: {percent}%")
else:
    st.write("No news articles found.")

# ✅ Display Articles
for i, article in enumerate(articles):
    with st.expander(f"📰 {article.get('title')}"):
        if article.get('urlToImage'):
            st.image(article.get('urlToImage'), use_container_width=True)

        blob_polarity, pos, neu, neg = analyze_sentiment_all(article)

        st.write("**Sentiment Distribution:**")
        st.write(f"🟢 Positive: {pos}%")
        st.write(f"⚪ Neutral: {neu}%")
        st.write(f"🔴 Negative: {neg}%")
        st.write(f"**TextBlob Polarity:** {round(blob_polarity*100, 1)}%")

        if st.button(f"📑 Show Summary", key=f"summary_{i}"):
            st.write("**Summary:**", generate_summary(article))

        st.markdown(f"[🔗 Read Full Article]({article.get('url')})")
        st.write(f"Published by: {article.get('source', {}).get('name', 'Unknown')}")

        if st.button("⭐ Bookmark Article", key=f"bookmark_{i}"):
            if article not in st.session_state.bookmarks:
                st.session_state.bookmarks.append(article)
                st.success("Added to bookmarks!")
            else:
                st.warning("Already bookmarked.")

# ✅ Bookmarks Section
if st.session_state.bookmarks:
    st.markdown("## ⭐ Bookmarked Articles")
    for saved in st.session_state.bookmarks:
        st.markdown(f"📰 [{saved.get('title')}]({saved.get('url')}) — *{saved.get('source', {}).get('name', 'Unknown')}*")

# ✅ Footer
st.markdown("---")
st.write("Made with ❤️ by Suraj Thorat | Powered by NewsAPI, TextBlob, VADER & BART AI Summarizer")
