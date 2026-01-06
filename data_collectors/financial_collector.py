"""
Financial Data Collector - Free market data
"""
import yfinance as yf
from typing import Dict, List
import pandas as pd
from datetime import datetime, timedelta

class FinancialCollector:
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
    
    def get_stock_data(self, symbol: str) -> Dict:
        """Get stock data for a symbol"""
        cache_key = f"stock_{symbol}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if (datetime.now() - cached_time).seconds < self.cache_duration:
                return cached_data
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get recent price data
            hist = ticker.history(period="5d")
            
            if hist.empty:
                return {}
            
            latest = hist.iloc[-1]
            previous = hist.iloc[-2] if len(hist) > 1 else latest
            
            change = latest['Close'] - previous['Close']
            change_percent = (change / previous['Close'] * 100) if previous['Close'] > 0 else 0
            
            data = {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'price': float(latest['Close']),
                'change': float(change),
                'change_percent': round(change_percent, 2),
                'volume': int(latest['Volume']),
                'market_cap': info.get('marketCap', 0),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'timestamp': datetime.now().isoformat()
            }
            
            self.cache[cache_key] = (data, datetime.now())
            return data
        except Exception as e:
            print(f"Error fetching stock data for {symbol}: {e}")
            return {}
    
    def get_market_indices(self) -> List[Dict]:
        """Get major market indices"""
        indices = ['^GSPC', '^DJI', '^IXIC', '^RUT']  # S&P 500, Dow, Nasdaq, Russell 2000
        results = []
        
        for symbol in indices:
            data = self.get_stock_data(symbol)
            if data:
                results.append(data)
        
        return results
    
    def get_trending_stocks(self, symbols: List[str]) -> List[Dict]:
        """Get data for multiple stocks"""
        results = []
        for symbol in symbols[:20]:  # Limit to 20 stocks
            data = self.get_stock_data(symbol)
            if data:
                results.append(data)
        return results


