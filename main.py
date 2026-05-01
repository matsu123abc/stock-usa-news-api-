from fastapi import FastAPI
import requests
import os
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")

@app.get("/tools/news")
def get_news(keyword: str):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": keyword + " stock news",   # ★英語ニュース検索
        "api_key": SERPER_API_KEY,
        "num": 10
    }

    response = requests.get(url, params=params)
    data = response.json()

    articles = []

    def safe(v):
        return v if v is not None else ""

    # ① top_stories
    for item in data.get("top_stories", []):
        articles.append({
            "title": safe(item.get("title")),
            "snippet": safe(item.get("snippet")),
            "link": safe(item.get("link")),
            "source": safe(item.get("source")),
            "date": safe(item.get("date"))
        })

    # ② organic_results
    for item in data.get("organic_results", []):
        articles.append({
            "title": safe(item.get("title")),
            "snippet": safe(item.get("snippet")),
            "link": safe(item.get("link")),
            "source": safe(item.get("source"))
        })

    # ③ news_results
    for item in data.get("news_results", []):
        articles.append({
            "title": safe(item.get("title")),
            "snippet": safe(item.get("snippet")),
            "link": safe(item.get("link")),
            "source": safe(item.get("source"))
        })

    return {
        "keyword": keyword,
        "count": len(articles),
        "articles": articles
    }


@app.get("/tools/stock_price")
def stock_price(symbol: str):
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1d")
    price = float(data["Close"].iloc[-1])
    return {
        "symbol": symbol,
        "price": price,
        "currency": "USD"
    }
