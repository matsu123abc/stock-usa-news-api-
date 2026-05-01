from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import requests
import os
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# -----------------------------
# 英語ニュース検索 API
# -----------------------------
@app.get("/tools/news")
def get_news(keyword: str):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": keyword + " stock news",
        "api_key": SERPER_API_KEY,
        "num": 5
    }

    response = requests.get(url, params=params)
    data = response.json()

    articles = []

    def safe(v):
        return v if v is not None else ""

    for item in data.get("top_stories", []):
        articles.append({
            "title": safe(item.get("title")),
            "snippet": safe(item.get("snippet")),
            "link": safe(item.get("link")),
            "source": safe(item.get("source")),
            "date": safe(item.get("date"))
        })

    for item in data.get("organic_results", []):
        articles.append({
            "title": safe(item.get("title")),
            "snippet": safe(item.get("snippet")),
            "link": safe(item.get("link")),
            "source": safe(item.get("source"))
        })

    for item in data.get("news_results", []):
        articles.append({
            "title": safe(item.get("title")),
            "snippet": safe(item.get("snippet")),
            "link": safe(item.get("link")),
            "source": safe(item.get("source"))
        })

    return {"keyword": keyword, "count": len(articles), "articles": articles}


# -----------------------------
# ストック価格 API
# -----------------------------
@app.get("/tools/stock_price")
def stock_price(symbol: str):
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1d")
    price = float(data["Close"].iloc[-1])
    return {"symbol": symbol, "price": price, "currency": "USD"}


# -----------------------------
# UI（ティッカー入力 → 英語ニュース一覧）
# -----------------------------
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
    <body>
        <h2>USA Stock News</h2>
        <input id="ticker" placeholder="例: QCOM, AAPL, MSFT">
        <button onclick="search()">ニュース検索</button>

        <div id="result"></div>

        <script>
        async function search() {
            const t = document.getElementById("ticker").value;
            const url = `/tools/news?keyword=${t}`;
            const res = await fetch(url);
            const data = await res.json();

            let html = "<h3>検索結果</h3>";
            for (const n of data.articles) {
                html += `
                    <div>
                        <a href="${n.link}" target="_blank">${n.title}</a><br>
                        <small>${n.source}</small><br>
                        <p>${n.snippet}</p>
                    </div>
                `;
            }
            document.getElementById("result").innerHTML = html;
        }
        </script>
    </body>
    </html>
    """