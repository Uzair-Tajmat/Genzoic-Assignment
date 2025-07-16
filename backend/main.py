# main.py
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import httpx
import asyncio
from datetime import datetime, timedelta
import json
import logging
import os
from functools import lru_cache
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
import json
import re




ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE", "K5SEK3JRJ9KXMAFC")
NEWS_API_KEY = "28b6be8fca4c4bd380b727e9afcbbbe6"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyA5lqAnDM_pZ4fpq2_7hmwJnUB08C8vI3I")
genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI(title="Market-Pulse", version="1")

@app.get("/api/greet")
def greet():
    return {"message": "Hello from FastAPI!"}




# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)





# Response models
class MomentumData(BaseModel):
    returns: List[float]
    score: float

class NewsItem(BaseModel):
    title: str
    description: str
    url: str

class MarketPulseResponse(BaseModel):
    ticker: str
    as_of: str
    momentum: MomentumData
    news: List[NewsItem]
    pulse: str
    llm_explanation: str

cache = {}
CACHE_TTL = 600  

def is_cache_valid(timestamp):
    return datetime.now() - timestamp < timedelta(seconds=CACHE_TTL)

def get_from_cache(key):
    if key in cache:
        data, timestamp = cache[key]
        if is_cache_valid(timestamp):
            return data
    return None

def set_cache(key, data):
    cache[key] = (data, datetime.now())

# API Configuration


async def fetch_price_data(ticker: str) -> Dict[str, Any]:
    """Fetch last 5 trading days price data from Alpha Vantage"""
    cache_key = f"price_{ticker}"
    cached_data = get_from_cache(cache_key)
    if cached_data:
        return cached_data
    
    try:
        async with httpx.AsyncClient() as client:
            url = f"https://www.alphavantage.co/query"
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": ticker,
                "apikey": ALPHA_VANTAGE_API_KEY,
                "outputsize": "compact"
            }
            
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            if "Time Series (Daily)" in data:
                time_series = data["Time Series (Daily)"]
                # Get last 5 trading days
                dates = sorted(time_series.keys(), reverse=True)[:6]  # Get 6 to calculate 5 returns
                
                prices = []
                for date in dates:
                    close_price = float(time_series[date]["4. close"])
                    prices.append(close_price)
                
                # Calculate daily returns
                returns = []
                for i in range(1, len(prices)):
                    daily_return = (prices[i-1] - prices[i]) / prices[i] * 100
                    returns.append(round(daily_return, 2))
                
                result = {
                    "returns": returns[:5],  # Last 5 returns
                    "prices": prices[:5]
                }
                
                set_cache(cache_key, result)
                return result
                
    except Exception as e:
        logger.error(f"Error fetching price data for {ticker}: {str(e)}")
        
    
def calculate_momentum_score(returns: List[float]) -> float:
    """Calculate simple momentum score from returns"""
    if not returns:
        return 0.0
    
    weights = [0.1, 0.15, 0.2, 0.25, 0.3] 
    
    weighted_sum = sum(ret * weight for ret, weight in zip(returns, weights))
    
    momentum_score = max(-1.0, min(1.0, weighted_sum / 10))
    
    return round(momentum_score, 2)

async def fetch_news_data(ticker: str) -> List[Dict[str, str]]:
    """Fetch latest news for the ticker"""
    cache_key = f"news_{ticker}"
    cached_data = get_from_cache(cache_key)
    if cached_data:
        return cached_data
    
    try:
        async with httpx.AsyncClient() as client:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": ticker,
                "sortBy": "publishedAt",
                "pageSize": 5,
                "apiKey": NEWS_API_KEY,
                "language": "en"
            }
            
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            if "articles" in data:
                news_items = []
                for article in data["articles"][:5]:
                    news_items.append({
                        "title": article.get("title", ""),
                        "description": article.get("description", ""),
                        "url": article.get("url", "")
                    })
                
                set_cache(cache_key, news_items)
                return news_items
                
    except Exception as e:
        logger.error(f"Error fetching news for {ticker}: {str(e)}")
    
  


async def get_llm_analysis(ticker: str, momentum_data: Dict, news_data: List[Dict]) -> Dict[str, str]:
    """Get LLM analysis using Gemini API"""
    try:
        
        prompt = f"""
Analyze the market sentiment for {ticker} based on the following data:

MOMENTUM DATA:
- Last 5 trading day returns: {momentum_data['returns']}
- Momentum score: {momentum_data['score']} (range: -1 to 1)

NEWS HEADLINES:
"""
        
        for i, news in enumerate(news_data[:5], 1):
            prompt += f"{i}. {news['title']}\n   {news['description']}\n"
        
        prompt += """
Based on this information, provide:
1. Overall market pulse: "bullish", "bearish", or "neutral"
2. Brief explanation (2-3 sentences) referencing both momentum and news context

Respond in JSON format:
{
  "pulse": "bullish|bearish|neutral",
  "explanation": "your explanation here"
}
"""

        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = await model.generate_content_async(prompt)

        
        llm_text = response.text.strip()
        try:
            cleaned_text = re.sub(r"^```json|^```|```$", "", llm_text.strip(), flags=re.MULTILINE).strip()

            llm_json = json.loads(cleaned_text)
        except Exception as parse_error:
            # If Gemini response is not perfect JSON, fallback logic
            logger.error(f"Error parsing Gemini JSON: {parse_error}, raw response: {llm_text}")
            return {
                "pulse": "neutral",
                "explanation": f"Could not parse Gemini output correctly. Raw output: {llm_text}"
            }

        return {
            "pulse": llm_json.get("pulse", "neutral"),
            "explanation": llm_json.get("explanation", "No explanation provided by Gemini.")
        }

    except Exception as e:
        logger.error(f"Error getting LLM analysis from Gemini: {str(e)}")
        return {
            "pulse": "neutral",
            "explanation": f"Unable to analyze market sentiment for {ticker} due to technical issues."
        }

@app.get("/api/v1/market-pulse", response_model=MarketPulseResponse)
async def get_market_pulse(ticker: str):
    """Get market pulse for a given ticker"""
    
    if not ticker or len(ticker) > 10:
        raise HTTPException(status_code=400, detail="Invalid ticker symbol")
    
    ticker = ticker.upper()
    
    try:
        # Fetch data concurrently
        price_task = fetch_price_data(ticker)
        news_task = fetch_news_data(ticker)
        
        price_data, news_data = await asyncio.gather(price_task, news_task)
        
        # Calculate momentum score
        momentum_score = calculate_momentum_score(price_data['returns'])
        
        momentum_data = {
            "returns": price_data['returns'],
            "score": momentum_score
        }
        
        # Get LLM analysis
        llm_result = await get_llm_analysis(ticker, momentum_data, news_data)
        
        response = MarketPulseResponse(
            ticker=ticker,
            as_of=datetime.now().strftime("%Y-%m-%d"),
            momentum=MomentumData(**momentum_data),
            news=[NewsItem(**item) for item in news_data],
            pulse=llm_result["pulse"],
            llm_explanation=llm_result["explanation"]
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing request for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)