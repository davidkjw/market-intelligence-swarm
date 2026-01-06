"""
Market Intelligence Engine - Analyzes and aggregates data
"""
from typing import List, Dict
from collections import Counter
from datetime import datetime, timedelta
import re

class IntelligenceEngine:
    def __init__(self):
        self.stock_pattern = re.compile(r'\$?[A-Z]{1,5}\b')
    
    def analyze_sentiment(self, text: str) -> Dict[str, int]:
        """Simple sentiment analysis using keyword matching"""
        positive_words = ['bull', 'bullish', 'up', 'rise', 'gain', 'profit', 'buy', 'moon', 'rocket', 'surge']
        negative_words = ['bear', 'bearish', 'down', 'fall', 'loss', 'crash', 'sell', 'dump', 'plunge', 'drop']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        return {
            'positive': positive_count,
            'negative': negative_count,
            'neutral': 1 if positive_count == 0 and negative_count == 0 else 0
        }
    
    def extract_stock_mentions(self, articles: List[Dict]) -> Dict[str, int]:
        """Extract and count stock symbol mentions"""
        mentions = []
        for article in articles:
            text = f"{article.get('title', '')} {article.get('summary', '')}"
            found = self.stock_pattern.findall(text)
            mentions.extend([m.replace('$', '').upper() for m in found if len(m.replace('$', '')) <= 5])
        
        return dict(Counter(mentions).most_common(20))

    def compute_per_ticker_sentiment(self, news: List[Dict], reddit: List[Dict]) -> Dict[str, Dict[str, int]]:
        """Compute sentiment counts per ticker symbol extracted from news + reddit"""
        per_ticker = {}

        # Helper to update counts
        def _update_for_text(symbols, text):
            sentiment = self.analyze_sentiment(text)
            for s in symbols:
                if s not in per_ticker:
                    per_ticker[s] = {'positive': 0, 'negative': 0, 'neutral': 0}
                per_ticker[s]['positive'] += sentiment.get('positive', 0)
                per_ticker[s]['negative'] += sentiment.get('negative', 0)
                per_ticker[s]['neutral'] += sentiment.get('neutral', 0)

        # Process news
        for article in news:
            text = f"{article.get('title', '')} {article.get('summary', '')}"
            found = [m.replace('$', '').upper() for m in self.stock_pattern.findall(text) if len(m.replace('$', '')) <= 5]
            if found:
                _update_for_text(found, text)

        # Process reddit
        for post in reddit:
            text = f"{post.get('title', '')} {post.get('selftext', '')}"
            found = [m.replace('$', '').upper() for m in self.stock_pattern.findall(text) if len(m.replace('$', '')) <= 5]
            if found:
                _update_for_text(found, text)

        # Convert counts to a simple summary (optionally add percent positive)
        summary = {}
        for s, counts in per_ticker.items():
            pos = counts.get('positive', 0)
            neg = counts.get('negative', 0)
            total = pos + neg
            pct_pos = (pos / total) * 100.0 if total > 0 else 50.0
            summary[s] = {
                'positive': pos,
                'negative': neg,
                'neutral': counts.get('neutral', 0),
                'pct_positive': round(pct_pos, 2)
            }

        return summary
    
    def aggregate_intelligence(self, news: List[Dict], reddit: List[Dict], financial: List[Dict]) -> Dict:
        """Aggregate all intelligence sources"""
        # Analyze news sentiment
        news_sentiment = {'positive': 0, 'negative': 0, 'neutral': 0}
        for article in news:
            sentiment = self.analyze_sentiment(article.get('summary', ''))
            news_sentiment['positive'] += sentiment['positive']
            news_sentiment['negative'] += sentiment['negative']
            news_sentiment['neutral'] += sentiment['neutral']
        
        # Analyze Reddit sentiment
        reddit_sentiment = {'positive': 0, 'negative': 0, 'neutral': 0}
        for post in reddit:
            text = f"{post.get('title', '')} {post.get('selftext', '')}"
            sentiment = self.analyze_sentiment(text)
            reddit_sentiment['positive'] += sentiment['positive']
            reddit_sentiment['negative'] += sentiment['negative']
            reddit_sentiment['neutral'] += sentiment['neutral']
        
        # Extract trending stocks
        all_content = news + reddit
        trending_stocks = self.extract_stock_mentions(all_content)
        
        # Get top stories
        top_news = sorted(news, key=lambda x: x.get('published', ''), reverse=True)[:10]
        top_reddit = sorted(reddit, key=lambda x: x.get('score', 0), reverse=True)[:10]
        
        return {
            'timestamp': datetime.now().isoformat(),
            'news_sentiment': news_sentiment,
            'reddit_sentiment': reddit_sentiment,
            'per_ticker_sentiment': self.compute_per_ticker_sentiment(news, reddit),
            'trending_stocks': trending_stocks,
            'top_news': top_news,
            'top_reddit': top_reddit,
            'market_indices': financial,
            'summary': self._generate_summary(news_sentiment, reddit_sentiment, trending_stocks)
        }
    
    def _generate_summary(self, news_sentiment: Dict, reddit_sentiment: Dict, trending_stocks: Dict) -> str:
        """Generate a text summary"""
        total_positive = news_sentiment['positive'] + reddit_sentiment['positive']
        total_negative = news_sentiment['negative'] + reddit_sentiment['negative']
        
        sentiment = "bullish" if total_positive > total_negative else "bearish" if total_negative > total_positive else "neutral"
        
        top_stocks = list(trending_stocks.keys())[:5]
        stocks_str = ", ".join(top_stocks) if top_stocks else "None"
        
        return f"Market sentiment is {sentiment}. Top trending stocks: {stocks_str}"


