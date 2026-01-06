"""
RSS Feed Collector - Free news aggregation
"""
import feedparser
import requests
from datetime import datetime
from typing import List, Dict
import time

class RSSCollector:
    def __init__(self):
        self.user_agent = 'MarketIntelligenceSwarm/1.0'
    
    def fetch_feed(self, url: str) -> List[Dict]:
        """Fetch and parse RSS feed"""
        try:
            headers = {'User-Agent': self.user_agent}
            feed = feedparser.parse(url)
            
            articles = []
            for entry in feed.entries[:20]:  # Limit to 20 per feed
                article = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', entry.get('description', '')),
                    'published': self._parse_date(entry.get('published', '')),
                    'source': feed.feed.get('title', url),
                    'source_type': 'rss'
                }
                articles.append(article)
            
            return articles
        except Exception as e:
            print(f"Error fetching RSS feed {url}: {e}")
            return []
    
    def _parse_date(self, date_str: str) -> str:
        """Parse date string to ISO format"""
        try:
            if date_str:
                # Try to parse with feedparser
                parsed = feedparser._parse_date(date_str)
                if parsed:
                    return datetime(*parsed[:6]).isoformat()
        except:
            pass
        return datetime.now().isoformat()
    
    def collect_all(self, feed_urls: List[str]) -> List[Dict]:
        """Collect from all RSS feeds"""
        all_articles = []
        for url in feed_urls:
            articles = self.fetch_feed(url)
            all_articles.extend(articles)
            time.sleep(1)  # Rate limiting
        
        # Sort by date (newest first)
        all_articles.sort(key=lambda x: x['published'], reverse=True)
        return all_articles


