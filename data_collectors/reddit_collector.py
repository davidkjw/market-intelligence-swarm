"""
Reddit Collector - Free social sentiment data
Uses web scraping (no API key required)
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import time
import re

class RedditCollector:
    def __init__(self):
        self.base_url = "https://www.reddit.com/r"
        self.headers = {
            'User-Agent': 'MarketIntelligenceSwarm/1.0 (Educational)'
        }
    
    def fetch_subreddit(self, subreddit: str, limit: int = 25) -> List[Dict]:
        """Fetch posts from a subreddit"""
        try:
            url = f"{self.base_url}/{subreddit}/hot.json?limit={limit}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            posts = []
            
            for child in data.get('data', {}).get('children', [])[:limit]:
                post_data = child.get('data', {})
                post = {
                    'title': post_data.get('title', ''),
                    'url': post_data.get('url', ''),
                    'selftext': post_data.get('selftext', ''),
                    'score': post_data.get('score', 0),
                    'num_comments': post_data.get('num_comments', 0),
                    'created_utc': post_data.get('created_utc', 0),
                    'subreddit': subreddit,
                    'source_type': 'reddit',
                    'permalink': f"https://reddit.com{post_data.get('permalink', '')}"
                }
                posts.append(post)
            
            return posts
        except Exception as e:
            print(f"Error fetching Reddit data from r/{subreddit}: {e}")
            return []
    
    def collect_all(self, subreddits: List[str]) -> List[Dict]:
        """Collect from all subreddits"""
        all_posts = []
        for subreddit in subreddits:
            posts = self.fetch_subreddit(subreddit)
            all_posts.extend(posts)
            time.sleep(2)  # Rate limiting to be respectful
        
        # Sort by score (highest first)
        all_posts.sort(key=lambda x: x['score'], reverse=True)
        return all_posts
    
    def extract_stock_mentions(self, text: str) -> List[str]:
        """Extract potential stock symbols from text"""
        # Simple pattern matching for stock symbols
        pattern = r'\$[A-Z]{1,5}\b'
        mentions = re.findall(pattern, text)
        return [m.replace('$', '') for m in mentions]


