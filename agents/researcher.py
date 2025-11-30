import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.tools import search_company_info, search_competitors, fetch_webpage_content

load_dotenv()

class ResearcherAgent:
    def __init__(self):
        self.client = genai.Client(api_key="AIzaSyDQkcA8-kSv44w5F_fxOJ8KFXGSpvkRQ-0")
        self.model_id = "gemini-2.5-flash"
        
    def research_company(self, company_name: str) -> dict:
        """Research the target company"""
        print(f"\n🔍 Researching {company_name}...")
        
        # Search for company information
        search_results = search_company_info(company_name, num_results=3)
        
        # Compile research data
        research_data = {
            "company_name": company_name,
            "search_results": search_results,
            "web_content": []
        }
        
        # Fetch content from top results
        for result in search_results[:2]:
            url = result.get("link", "")
            if url:
                content = fetch_webpage_content(url)
                if content:
                    research_data["web_content"].append({
                        "url": url,
                        "content": content
                    })
        
        # Use Gemini to extract key information
        prompt = f"""
Based on the following search results and web content about {company_name}, extract key information:

Search Results:
{self._format_search_results(search_results)}

Web Content:
{self._format_web_content(research_data["web_content"])}

Provide a structured summary with:
1. Company Overview (what they do, their mission)
2. Main Products/Services
3. Target Market
4. Key Features/Differentiators

Keep it concise and factual.
"""
        
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )
        
        research_data["summary"] = response.text
        print(f"✅ Research complete for {company_name}")
        
        return research_data
    
    def research_competitors(self, company_name: str) -> dict:
        """Research competitors"""
        print(f"\n🔍 Finding competitors of {company_name}...")
        
        # Search for competitors
        competitor_results = search_competitors(company_name, num_results=5)
        
        # Use Gemini to identify top competitors
        prompt = f"""
Based on these search results about {company_name}'s competitors:

{self._format_search_results(competitor_results)}

Identify the top 3-5 main competitors. For each competitor, provide:
- Company name
- Brief description
- Why they're a competitor

Format as a clear list.
"""
        
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )
        
        competitors_data = {
            "search_results": competitor_results,
            "identified_competitors": response.text
        }
        
        print(f"✅ Found competitors for {company_name}")
        
        return competitors_data
    
    def _format_search_results(self, results: list) -> str:
        """Format search results for prompt"""
        formatted = ""
        for i, result in enumerate(results, 1):
            formatted += f"\n{i}. {result.get('title', 'N/A')}\n"
            formatted += f"   {result.get('snippet', 'N/A')}\n"
            formatted += f"   URL: {result.get('link', 'N/A')}\n"
        return formatted
    
    def _format_web_content(self, content_list: list) -> str:
        """Format web content for prompt"""
        formatted = ""
        for i, item in enumerate(content_list, 1):
            formatted += f"\nSource {i} ({item.get('url', 'N/A')}):\n"
            formatted += f"{item.get('content', 'N/A')[:1000]}...\n"
        return formatted