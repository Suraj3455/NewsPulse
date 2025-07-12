import streamlit as st
import requests
from textblob import TextBlob
from transformers import pipeline
from datetime import datetime
from collections import Counter
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from gtts import gTTS
from io import BytesIO
import nltk
nltk.download('vader_lexicon')

# Page Config
st.set_page_config(page_title="NewsPulse: AI Trending & Sentiment", layout="wide")

# Session State for bookmarks
if 'bookmarks' not in st.session_state:
    st.session_state.bookmarks = []

# Summarizer model
@st.cache_resource
def load_summarizer():
    return pipeline("summarization", model="facebook/bart-large-cnn")

summarizer = load_summarizer()
vader_analyzer = SentimentIntensityAnalyzer()

<<<<<<< HEAD
# ✅ NewsAPI Key
=======
# API Key
>>>>>>> fd2ebf5 (Updated app.py with WordCloud and Publisher Chart)
api_key = "88adf97bc6924ef7a83334bf4b08af0e"

# News Fetcher
def fetch_news(category=None, keyword=None):
    base_url = "https://newsapi.org/v2/"
    if keyword:
        url = f"{base_url}everything?apiKey={api_key}&q={keyword}&language=en&sortBy=publishedAt"
    else:
        url = f"{base_url}top-headlines?apiKey={api_key}&language=en"
        if category:
            url += f"&category={category}"
    response = requests.get(url)
    data = response.json()
    return data.get("articles", [])

# Sentiment Analyzer
def analyze_sentiment_all(text):
    blob_polarity = TextBlob(text).sentiment.polarity
    vader_scores = vader_analyzer.polarity_scores(text)
    pos = round(vader_scores['pos'] * 100, 1)
    neu = round(vader_scores['neu'] * 100, 1)
    neg = round(vader_scores['neg'] * 100, 1)
    return blob_polarity, pos, neu, neg

# AI Summarizer
def generate_summary(text):
    if text and len(text) > 50:
        try:
            summary = summarizer(text, max_length=120, min_length=50, do_sample=False)
            return summary[0]['summary_text']
        except:
            return text
    else:
        return "No summary available."

# Text-to-Speech
def text_to_speech(text):
    tts = gTTS(text)
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return mp3_fp

# Sidebar Filters
st.sidebar.title("🔍 Filter & Search News")
category = st.sidebar.selectbox("Select News Category", ("general", "business", "sports", "technology", "entertainment"))
keyword = st.sidebar.text_input("Or enter a Search Keyword:")

# Title
st.markdown("# 📰 NewsPulse: Real-Time News Trends & Sentiment AI")
st.markdown("###### Powered by NewsAPI, TextBlob, VADER, and BART AI Summarizer")

# Fetch News
articles = fetch_news(category=category, keyword=keyword)

# Sentiment Distribution
sentiments_total = {'Positive': 0, 'Neutral': 0, 'Negative': 0}

for article in articles:
    text = (article.get("title") or "") + " " + (article.get("description") or "")
    _, pos, neu, neg = analyze_sentiment_all(text)
    if pos > neu and pos > neg:
        sentiments_total['Positive'] += 1
    elif neg > pos and neg > neu:
        sentiments_total['Negative'] += 1
    else:
        sentiments_total['Neutral'] += 1

total_articles = sum(sentiments_total.values())

# Show Sentiment Stats
if total_articles > 0:
    st.markdown("## 📊 Overall Sentiment Distribution")
    for sentiment, count in sentiments_total.items():
        percent = round((count / total_articles) * 100, 1)
        emoji = "🟢" if sentiment == "Positive" else "⚪" if sentiment == "Neutral" else "🔴"
        st.write(f"{emoji} {sentiment}: {percent}%")
else:
    st.warning("No news articles found for the current filter.")

# News Articles Section
st.markdown("## 🗞️ Latest News")

publishers = []

for idx, article in enumerate(articles):
    with st.expander(f"📰 {article.get('title')}"):
        if article.get("urlToImage"):
            st.image(article["urlToImage"], use_container_width=True)

        text = (article.get("title") or "") + " " + (article.get("description") or "")
        blob_polarity, pos, neu, neg = analyze_sentiment_all(text)

        st.write("**Sentiment Analysis:**")
        st.write(f"🟢 Positive: {pos}% | ⚪ Neutral: {neu}% | 🔴 Negative: {neg}%")
        st.write(f"TextBlob Polarity: {round(blob_polarity*100, 1)}%")

        content_text = (article.get("content") or article.get("description") or "")

        if st.button("📖 Show Summary", key=f"summary_{idx}"):
            summary = generate_summary(content_text)
            st.success(summary)

            # TTS player after summary
            st.markdown("**🎧 Listen Summary:**")
            audio_fp = text_to_speech(summary)
            st.audio(audio_fp, format="audio/mp3")

        st.markdown(f"[🔗 Read Full Article]({article.get('url')})")
        st.caption(f"Published by: {article.get('source', {}).get('name', 'Unknown')} | Date: {article.get('publishedAt', 'N/A')}")

        if st.button("⭐ Bookmark Article", key=f"bookmark_{idx}"):
            if article not in st.session_state.bookmarks:
                st.session_state.bookmarks.append(article)
                st.success("Added to bookmarks!")
            else:
                st.info("Already in bookmarks.")

        publishers.append(article.get('source', {}).get('name', 'Unknown'))

# ✅ WordCloud & Publisher Count (if articles exist)
if total_articles > 0:
    st.markdown("## 📊 Article Count by Publisher")

    # Count publisher occurrences
    publishers = [article.get('source', {}).get('name', 'Unknown') for article in articles]
    publisher_counts = dict(Counter(publishers))

    # Convert to DataFrame
    publisher_df = pd.DataFrame(list(publisher_counts.items()), columns=['Publisher', 'Article Count'])
    publisher_df = publisher_df.sort_values(by="Article Count", ascending=False)

    # Display bar chart
    st.bar_chart(publisher_df.set_index('Publisher'))

    # ✅ WordCloud of Headlines
    st.markdown("## ☁️ WordCloud of Headlines")
    wordcloud_text = " ".join([article.get("title", "") for article in articles])

    wordcloud = WordCloud(width=1200, height=600, background_color='white').generate(wordcloud_text)

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)

# Bookmarks Section
if st.session_state.bookmarks:
    st.markdown("## ⭐ Bookmarked Articles")
    for bm in st.session_state.bookmarks:
        st.markdown(f"📰 [{bm.get('title')}]({bm.get('url')}) — *{bm.get('source', {}).get('name', 'Unknown')}*")

# Footer
st.markdown("---")
st.write("Made with ❤️ by Suraj Thorat | Powered by NewsAPI, TextBlob, VADER, and BART AI Summarizer")

