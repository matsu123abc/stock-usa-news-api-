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
        "num": 10
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
async def home(request: Request):
    ticker = request.query_params.get("ticker", "")

    html_head = """
    <html><head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; padding: 20px; }
        input { width: 100%; padding: 12px; font-size: 18px; }
        button { width: 100%; padding: 12px; margin-top: 10px; font-size: 18px;
                 background: #0078D4; color: white; border: none; border-radius: 6px; }
        .card { padding: 15px; margin-top: 15px; border-radius: 8px;
                background: #f2f2f2; }
        a { text-decoration: none; color: #0078D4; font-weight: bold; }
    </style>
    </head><body>
    <h2>USA Stock News</h2>
    """

    html_form = f"""
    <form method="get">
        <input name="ticker" placeholder="例: QCOM, AAPL, MSFT" value="{ticker}">
        <button type="submit">ニュース検索</button>
    </form>
    """

    if ticker == "":
        return html_head + html_form + "</body></html>"

    # ★ Azure / ローカルの両方で動く「自分自身の API URL」
    base_url = str(request.base_url).rstrip("/")
    api_url = f"{base_url}/tools/news"
    news = requests.get(api_url, params={"keyword": ticker}).json()

    html_news = "<h3>検索結果</h3>"

    for n in news["articles"]:
        html_news += f"""
        <div class="card">
            <a href="{n['link']}" target="_blank">{n['title']}</a><br>
            <small>{n.get('source','')}</small><br>
            <p>{n.get('snippet','')}</p>
        </div>
        """

    return html_head + html_form + html_news + "</body></html>"
