"""
Researcher Agent Module

This module implements the ResearcherAgent class responsible for gathering
information about companies and their competitors using web search and AI
analysis powered by Google's Gemini model.

The agent performs two primary functions:
1. Company Research - Detailed information gathering about a target company
2. Competitor Research - Identification and analysis of market competitors

Author: Ishan
Course: Google-Kaggle 5-Day AI Agents Intensive Course (Capstone Project)
Date: November 2025
"""

import os
from api_config import GOOGLE_API_KEY
from google import genai
from google.genai import types
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.tools import search_company_info, search_competitors, fetch_webpage_content

load_dotenv()


class ResearcherAgent:
    """
    Agent responsible for researching companies and their competitive landscape.
    
    This agent uses web search APIs and Google's Gemini AI model to gather and
    synthesize information about target companies and their competitors. It performs
    multi-step research including web searches, content extraction, and AI-powered
    analysis.
    
    Attributes:
        client (genai.Client): Google Generative AI client instance
        model_id (str): Gemini model identifier for AI analysis
        
    Example:
        >>> researcher = ResearcherAgent()
        >>> company_data = researcher.research_company("Netflix")
        >>> print(company_data['summary'])
    """
    
    def __init__(self):
        """
        Initialize the ResearcherAgent with Gemini AI client.
        
        Sets up the Google Generative AI client using the API key from
        environment variables and configures the Gemini model.
        
        Raises:
            Exception: If GOOGLE_API_KEY is not found in environment
        """
        self.client = genai.Client(api_key=GOOGLE_API_KEY)
        self.model_id = "gemini-2.5-flash"
        
    def research_company(self, company_name: str) -> dict:
        """
        Conduct comprehensive research on a target company.
        
        This method performs a multi-step research process:
        1. Searches for company information using SerpAPI
        2. Fetches full webpage content from top search results
        3. Uses Gemini AI to extract and structure key information
        
        The AI analysis produces a structured summary including:
        - Company overview and mission
        - Main products/services
        - Target market
        - Key features and differentiators
        
        Args:
            company_name (str): Name of the company to research
            
        Returns:
            dict: Comprehensive research data with the following structure:
                {
                    'company_name': str,
                    'search_results': list[dict],  # Raw search results
                    'web_content': list[dict],     # Extracted webpage content
                    'summary': str                 # AI-generated structured summary
                }
                
        Raises:
            Exception: If web search fails or AI analysis encounters an error
            
        Example:
            >>> researcher = ResearcherAgent()
            >>> data = researcher.research_company("Notion")
            >>> print(data['summary'])
            
            Company Overview: Notion is a productivity platform...
            Main Products/Services: All-in-one workspace...
            
        Note:
            - Fetches top 3 search results
            - Extracts full content from top 2 results
            - Uses Gemini 2.5 Flash for fast analysis
        """
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
        """
        Identify and research the main competitors of a target company.
        
        This method searches for competitor information and uses AI to identify
        the top 3-5 main competitors with detailed analysis of why they compete
        in the same market space.
        
        Args:
            company_name (str): Name of the company whose competitors to find
            
        Returns:
            dict: Competitor research data with the following structure:
                {
                    'search_results': list[dict],      # Raw search results
                    'identified_competitors': str      # AI-generated competitor list
                }
                
                The 'identified_competitors' field contains formatted text with:
                - Competitor name
                - Brief description
                - Reason for being a competitor
                
        Raises:
            Exception: If competitor search fails or AI analysis encounters an error
            
        Example:
            >>> researcher = ResearcherAgent()
            >>> competitors = researcher.research_competitors("Slack")
            >>> print(competitors['identified_competitors'])
            
            1. Microsoft Teams
               Description: Enterprise communication platform...
               Why they're a competitor: Direct competitor in team chat...
               
            2. Discord
               Description: Community-focused chat platform...
               
        Note:
            - Searches for top 5 competitor-related results
            - AI identifies 3-5 main competitors from results
            - Provides context for competitive relationships
        """
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
        """
        Format search results into a readable string for AI prompts.
        
        Converts a list of search result dictionaries into a formatted text
        string that can be included in prompts for AI analysis.
        
        Args:
            results (list): List of search result dictionaries from SerpAPI.
                Each dict should contain 'title', 'snippet', and 'link' keys.
                
        Returns:
            str: Formatted multi-line string with numbered results
            
        Example:
            >>> results = [
            ...     {'title': 'Company X', 'snippet': 'Leading provider...', 'link': 'https://...'},
            ...     {'title': 'About Company X', 'snippet': 'Founded in...', 'link': 'https://...'}
            ... ]
            >>> formatted = researcher._format_search_results(results)
            >>> print(formatted)
            
            1. Company X
               Leading provider...
               URL: https://...
               
            2. About Company X
               Founded in...
               URL: https://...
        """
        formatted = ""
        for i, result in enumerate(results, 1):
            formatted += f"\n{i}. {result.get('title', 'N/A')}\n"
            formatted += f"   {result.get('snippet', 'N/A')}\n"
            formatted += f"   URL: {result.get('link', 'N/A')}\n"
        return formatted
    
    def _format_web_content(self, content_list: list) -> str:
        """
        Format webpage content into a readable string for AI prompts.
        
        Converts a list of webpage content dictionaries into a formatted text
        string, truncating long content to 1000 characters per source.
        
        Args:
            content_list (list): List of content dictionaries.
                Each dict should contain 'url' and 'content' keys.
                
        Returns:
            str: Formatted multi-line string with numbered sources
            
        Example:
            >>> content = [
            ...     {'url': 'https://example.com', 'content': 'Long webpage text...'},
            ...     {'url': 'https://example2.com', 'content': 'More content...'}
            ... ]
            >>> formatted = researcher._format_web_content(content)
            >>> print(formatted)
            
            Source 1 (https://example.com):
            Long webpage text...(truncated to 1000 chars)
            
            Source 2 (https://example2.com):
            More content...(truncated to 1000 chars)
            
        Note:
            Content is automatically truncated to 1000 characters to prevent
            token limit issues in AI prompts.
        """
        formatted = ""
        for i, item in enumerate(content_list, 1):
            formatted += f"\nSource {i} ({item.get('url', 'N/A')}):\n"
            formatted += f"{item.get('content', 'N/A')[:1000]}...\n"
        return formatted