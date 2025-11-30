import os
import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()

def search_company_info(company_name: str, num_results: int = 5) -> list:
    """Search for company information using SerpAPI"""
    try:
        params = {
            "engine": "google",
            "q": f"{company_name} company overview products services",
            "api_key": os.getenv("SERPAPI_KEY"),
            "num": num_results
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        organic_results = results.get("organic_results", [])
        
        search_results = []
        for result in organic_results[:num_results]:
            search_results.append({
                "title": result.get("title", ""),
                "link": result.get("link", ""),
                "snippet": result.get("snippet", "")
            })
        
        return search_results
    except Exception as e:
        print(f"Error in search_company_info: {e}")
        return []


def search_competitors(company_name: str, num_results: int = 5) -> list:
    """Search for competitors using SerpAPI"""
    try:
        params = {
            "engine": "google",
            "q": f"{company_name} competitors alternatives similar companies",
            "api_key": os.getenv("SERPAPI_KEY"),
            "num": num_results
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        organic_results = results.get("organic_results", [])
        
        competitor_results = []
        for result in organic_results[:num_results]:
            competitor_results.append({
                "title": result.get("title", ""),
                "link": result.get("link", ""),
                "snippet": result.get("snippet", "")
            })
        
        return competitor_results
    except Exception as e:
        print(f"Error in search_competitors: {e}")
        return []


def search_pricing_info(company_name: str) -> list:
    """Search for pricing information"""
    try:
        params = {
            "engine": "google",
            "q": f"{company_name} pricing plans cost",
            "api_key": os.getenv("SERPAPI_KEY"),
            "num": 3
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        organic_results = results.get("organic_results", [])
        
        pricing_results = []
        for result in organic_results[:3]:
            pricing_results.append({
                "title": result.get("title", ""),
                "link": result.get("link", ""),
                "snippet": result.get("snippet", "")
            })
        
        return pricing_results
    except Exception as e:
        print(f"Error in search_pricing_info: {e}")
        return []


def fetch_webpage_content(url: str) -> str:
    """Fetch and parse webpage content"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text[:5000]  # Limit to 5000 chars
    except Exception as e:
        print(f"Error fetching webpage {url}: {e}")
        return ""