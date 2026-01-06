"""
Configuration for Market Intelligence Swarm
All services are free tier or open source
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Free News APIs (no key required or free tier)
NEWS_SOURCES = {
    'rss_feeds': [
        'https://feeds.finance.yahoo.com/rss/2.0/headline',
        'https://www.cnbc.com/id/100003114/device/rss/rss.html',
        'https://feeds.reuters.com/reuters/businessNews',
        'https://rss.cnn.com/rss/money_latest.rss',
    ],
    'reddit': {
        'subreddits': ['stocks', 'investing', 'StockMarket', 'wallstreetbets'],
        'use_api': False  # Use web scraping instead of API
    }
}

# Free Financial Data APIs
FINANCIAL_APIS = {
    'yfinance': {
        'enabled': True,
        'rate_limit': 2  # requests per second
    },
    'alpha_vantage': {
        'enabled': False,  # Requires free API key
        'api_key': os.getenv('ALPHA_VANTAGE_KEY', '')
    }
}

# Swarm Configuration
SWARM_CONFIG = {
    'workers': 5,  # Number of parallel workers
    'update_interval': 300,  # Update every 5 minutes
    'max_articles': 100,  # Max articles per update
    'cache_duration': 600  # Cache for 10 minutes
}

# Server Configuration
SERVER_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': True
}


