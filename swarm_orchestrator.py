"""
Swarm Orchestrator - Coordinates multiple data collectors
"""
import asyncio
import aiohttp
from typing import Dict, List
from datetime import datetime
from data_collectors.rss_collector import RSSCollector
from data_collectors.financial_collector import FinancialCollector
from data_collectors.reddit_collector import RedditCollector
from intelligence_engine import IntelligenceEngine
import config

class SwarmOrchestrator:
    def __init__(self):
        self.rss_collector = RSSCollector()
        self.financial_collector = FinancialCollector()
        self.reddit_collector = RedditCollector()
        self.intelligence_engine = IntelligenceEngine()
        self.cache = {}
        self.last_update = None
    
    async def collect_news_async(self, feed_urls: List[str]) -> List[Dict]:
        """Asynchronously collect news from RSS feeds"""
        loop = asyncio.get_event_loop()
        # Run in executor to avoid blocking
        return await loop.run_in_executor(None, self.rss_collector.collect_all, feed_urls)
    
    async def collect_reddit_async(self, subreddits: List[str]) -> List[Dict]:
        """Asynchronously collect Reddit data"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.reddit_collector.collect_all, subreddits)
    
    async def collect_financial_async(self) -> List[Dict]:
        """Asynchronously collect financial data"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.financial_collector.get_market_indices)
    
    async def gather_intelligence(self) -> Dict:
        """Gather intelligence from all sources in parallel"""
        print(f"[{datetime.now()}] Starting intelligence gathering...")
        
        # Collect from all sources in parallel
        news_task = self.collect_news_async(config.NEWS_SOURCES['rss_feeds'])
        reddit_task = self.collect_reddit_async(config.NEWS_SOURCES['reddit']['subreddits'])
        financial_task = self.collect_financial_async()
        
        news, reddit, financial = await asyncio.gather(
            news_task,
            reddit_task,
            financial_task
        )
        
        print(f"[{datetime.now()}] Collected {len(news)} news articles, {len(reddit)} Reddit posts, {len(financial)} market indices")
        
        # Aggregate intelligence
        intelligence = self.intelligence_engine.aggregate_intelligence(news, reddit, financial)
        
        # Cache the results
        self.cache = intelligence
        self.last_update = datetime.now()
        
        return intelligence
    
    def get_cached_intelligence(self) -> Dict:
        """Get cached intelligence if available and fresh"""
        if self.cache and self.last_update:
            age = (datetime.now() - self.last_update).total_seconds()
            if age < config.SWARM_CONFIG['cache_duration']:
                return self.cache
        
        return None
    
    def get_intelligence(self, force_refresh: bool = False) -> Dict:
        """Get intelligence (from cache or fresh)"""
        if not force_refresh:
            cached = self.get_cached_intelligence()
            if cached:
                return cached
        
        # Run async gather
        return asyncio.run(self.gather_intelligence())


