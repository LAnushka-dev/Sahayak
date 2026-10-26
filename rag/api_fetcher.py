import os
import requests
from typing import List, Dict, Optional

class LiveLegalAPIFetcher:
    """
    Dynamically fetches and extracts statutory laws, judicial precedents, and government 
    schemes using external APIs (Jina Reader, Serper Search, and official gazettes)
    without needing manual hardcoded files.
    """
    def __init__(self, jina_api_key: Optional[str] = None, serper_api_key: Optional[str] = None):
        self.jina_api_key = jina_api_key or os.getenv("JINA_API_KEY", "")
        self.serper_api_key = serper_api_key or os.getenv("SERPER_API_KEY", "")
        self.jina_reader_url = "https://r.jina.ai/"
        self.serper_url = "https://google.serper.dev/search"

    def fetch_via_jina_reader(self, target_url: str) -> str:
        """
        Uses Jina Reader API to convert any live law portal, act PDF, or government 
        page into clean, LLM-ready markdown.
        """
        headers = {
            "Accept": "text/event-stream" if not self.jina_api_key else "application/json",
            "X-Return-Format": "markdown"
        }
        if self.jina_api_key:
            headers["Authorization"] = f"Bearer {self.jina_api_key}"

        try:
            full_url = f"{self.jina_reader_url}{target_url}"
            resp = requests.get(full_url, headers=headers, timeout=15)
            if resp.status_code == 200:
                return resp.text[:12000]  # Return top relevant chunk
        except Exception as e:
            print(f"[LiveFetcher] Jina Reader error: {e}")
        return ""

    def search_live_legal_updates(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Queries live legal databases, recent circulars, and court orders via Serper API.
        """
        if not self.serper_api_key:
            # Fallback mock search for local testing without active API key
            return [{
                "title": f"Live Search Result for: {query}",
                "snippet": f"Statutory provisions and current regulatory guidelines concerning '{query}'. Under Indian Law, citizens can approach appellate tribunals and online portals.",
                "link": "https://indiacode.nic.in"
            }]

        headers = {
            "X-API-KEY": self.serper_api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "q": f"India law statutory provision {query}",
            "num": num_results
        }
        try:
            resp = requests.post(self.serper_url, json=payload, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                results = []
                for item in data.get("organic", []):
                    results.append({
                        "title": item.get("title", ""),
                        "snippet": item.get("snippet", ""),
                        "link": item.get("link", "")
                    })
                return results
        except Exception as e:
            print(f"[LiveFetcher] Serper search error: {e}")
        return []

    def fetch_law_by_topic(self, topic: str) -> List[Dict]:
        """
        Aggregates live search results and scrapes the top source via Jina Reader.
        """
        search_results = self.search_live_legal_updates(topic, num_results=3)
        enriched_docs = []
        for res in search_results:
            content = res.get("snippet", "")
            # If a reputable legal URL is found, read it live through Jina Reader
            link = res.get("link", "")
            if link and ("nic.in" in link or "indiankanoon.org" in link or "gov.in" in link):
                scraped = self.fetch_via_jina_reader(link)
                if scraped:
                    content = scraped[:2500]

            enriched_docs.append({
                "title": res.get("title", "Legal Provision"),
                "content": content,
                "source": link or "National Legal Portal"
            })
        return enriched_docs
