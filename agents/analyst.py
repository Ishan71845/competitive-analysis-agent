"""
Analyst Agent Module

This module implements the AnalystAgent class responsible for performing
competitive analysis, SWOT analysis, and pricing strategy analysis using
Google's Gemini AI model.

The agent provides three core analytical functions:
1. Competitive Analysis - Market positioning and competitor comparison
2. SWOT Analysis - Strengths, Weaknesses, Opportunities, Threats
3. Pricing Analysis - Pricing strategy evaluation and recommendations

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
from utils.tools import search_pricing_info

load_dotenv()


class AnalystAgent:
    """
    Agent responsible for competitive analysis and strategic insights.
    
    This agent uses Google's Gemini AI to perform comprehensive business
    analysis including competitive positioning, SWOT analysis, and pricing
    strategy evaluation. It synthesizes research data into actionable insights.
    
    Attributes:
        client (genai.Client): Google Generative AI client instance
        model_id (str): Gemini model identifier for AI analysis
        
    Example:
        >>> analyst = AnalystAgent()
        >>> analysis = analyst.analyze_competition(company_data, competitors_data)
        >>> swot = analyst.generate_swot(company_data, analysis)
    """
    
    def __init__(self):
        """
        Initialize the AnalystAgent with Gemini AI client.
        
        Sets up the Google Generative AI client using the API key from
        environment variables and configures the Gemini model.
        """
        self.client = genai.Client(api_key=GOOGLE_API_KEY)
        self.model_id = "gemini-2.5-flash"

    def analyze_competition(self, company_data: dict, competitors_data: dict) -> dict:
        """
        Perform comprehensive competitive landscape analysis.
        
        Analyzes the target company's position relative to competitors across
        multiple dimensions including market position, competitive advantages,
        disadvantages, feature comparison, and target audience overlap.
        
        Args:
            company_data (dict): Research data for the target company.
                Expected keys: 'company_name', 'summary'
            competitors_data (dict): Research data about competitors.
                Expected keys: 'identified_competitors'
                
        Returns:
            dict: Competitive analysis results with the following structure:
                {
                    'competitive_analysis': str  # Detailed analysis covering:
                                                 # - Market Position
                                                 # - Competitive Advantages
                                                 # - Competitive Disadvantages
                                                 # - Feature Comparison
                                                 # - Target Audience Overlap
                }
                
        Raises:
            Exception: If AI analysis fails or data is insufficient
            
        Example:
            >>> company_data = {
            ...     'company_name': 'Slack',
            ...     'summary': 'Team collaboration platform...'
            ... }
            >>> competitors_data = {
            ...     'identified_competitors': '1. Microsoft Teams...'
            ... }
            >>> result = analyst.analyze_competition(company_data, competitors_data)
            >>> print(result['competitive_analysis'])
            
        Note:
            Analysis is data-driven and specific based on provided research
        """
        print(f"\n📊 Analyzing competitive landscape...")

        company_name = company_data.get("company_name", "Unknown")

        # Create analysis prompt
        prompt = f"""
You are a business analyst. Perform a competitive analysis based on this data:

TARGET COMPANY: {company_name}
{company_data.get('summary', 'No data available')}

COMPETITORS:
{competitors_data.get('identified_competitors', 'No competitors identified')}

Provide a competitive analysis covering:

1. **Market Position**: Where does {company_name} stand relative to competitors?

2. **Competitive Advantages**: What are {company_name}'s unique strengths?

3. **Competitive Disadvantages**: Where do competitors have an edge?

4. **Feature Comparison**: Compare key features/offerings across competitors

5. **Target Audience Overlap**: How similar are the target markets?

Be specific and data-driven. Use the information provided.
"""

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )

        analysis = {
            "competitive_analysis": response.text
        }

        print(f"✅ Competitive analysis complete")

        return analysis

    def generate_swot(self, company_data: dict, competitive_analysis: dict) -> dict:
        """
        Generate comprehensive SWOT analysis for the target company.
        
        Creates a structured SWOT (Strengths, Weaknesses, Opportunities, Threats)
        analysis based on company research and competitive analysis data.
        
        Args:
            company_data (dict): Research data for the target company.
                Expected keys: 'company_name', 'summary'
            competitive_analysis (dict): Results from competitive analysis.
                Expected keys: 'competitive_analysis'
                
        Returns:
            dict: SWOT analysis with the following structure:
                {
                    'swot_analysis': str  # Structured SWOT with:
                                          # - 4-5 Strengths
                                          # - 4-5 Weaknesses
                                          # - 4-5 Opportunities
                                          # - 4-5 Threats
                }
                
        Raises:
            Exception: If AI analysis fails or data is insufficient
            
        Example:
            >>> company_data = {'company_name': 'Netflix', 'summary': '...'}
            >>> competitive_analysis = {'competitive_analysis': '...'}
            >>> swot = analyst.generate_swot(company_data, competitive_analysis)
            >>> print(swot['swot_analysis'])
            
            **STRENGTHS:**
            - Market leader in streaming...
            - Strong original content library...
            
        Note:
            Analysis is specific and actionable, not generic platitudes
        """
        print(f"\n📋 Generating SWOT analysis...")

        company_name = company_data.get("company_name", "Unknown")

        prompt = f"""
Based on this information about {company_name}:

COMPANY OVERVIEW:
{company_data.get('summary', 'No data available')}

COMPETITIVE ANALYSIS:
{competitive_analysis.get('competitive_analysis', 'No analysis available')}

Generate a comprehensive SWOT analysis:

**STRENGTHS:**
- List 4-5 key strengths

**WEAKNESSES:**
- List 4-5 key weaknesses

**OPPORTUNITIES:**
- List 4-5 market opportunities

**THREATS:**
- List 4-5 threats from competition/market

Be specific and actionable.
"""

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )

        swot = {
            "swot_analysis": response.text
        }

        print(f"✅ SWOT analysis complete")

        return swot

    def analyze_pricing(self, company_name: str, competitors: list) -> dict:
        """
        Analyze pricing strategies and positioning.
        
        Evaluates the target company's pricing strategy in comparison to
        competitors, providing insights on pricing positioning and strategic
        recommendations.
        
        Args:
            company_name (str): Name of the target company
            competitors (list): List of competitor company names (max 2 analyzed)
                
        Returns:
            dict: Pricing analysis with the following structure:
                {
                    'company_pricing': list,      # Search results for company pricing
                    'competitor_pricing': list,   # Competitor pricing data
                    'analysis': str               # AI-generated analysis covering:
                                                  # - Pricing positioning
                                                  # - Competitor comparison
                                                  # - Strategy recommendations
                }
                
        Raises:
            Exception: If pricing search fails or AI analysis encounters error
            
        Example:
            >>> result = analyst.analyze_pricing("Notion", ["Coda", "Airtable"])
            >>> print(result['analysis'])
            
            Pricing Positioning: Mid-tier/Premium...
            Comparison: More affordable than Coda but pricier than...
            
        Note:
            - Limits competitor analysis to 2 companies to save API calls
            - Uses web search to gather current pricing information
        """
        print(f"\n💰 Analyzing pricing strategies...")

        # Search pricing for main company
        company_pricing = search_pricing_info(company_name)

        pricing_data = {
            "company_pricing": company_pricing,
            "competitor_pricing": []
        }

        # Search pricing for competitors (limit to 2 to save API calls)
        for competitor in competitors[:2]:
            comp_pricing = search_pricing_info(competitor)
            pricing_data["competitor_pricing"].append({
                "competitor": competitor,
                "results": comp_pricing
            })
        
        # Analyze with Gemini
        prompt = f"""
Analyze the pricing strategy based on this data:

{company_name} Pricing:
{self._format_pricing_results(company_pricing)}

Competitor Pricing:
{self._format_competitor_pricing(pricing_data["competitor_pricing"])}

Provide:
1. Pricing positioning (premium/mid-tier/budget)
2. Comparison with competitors
3. Pricing strategy recommendations

Keep it concise.
"""

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )

        pricing_data["analysis"] = response.text

        print(f"✅ Pricing analysis complete")

        return pricing_data

    def _format_pricing_results(self, results: list) -> str:
        """
        Format pricing search results for AI prompt.
        
        Args:
            results (list): List of search result dictionaries
            
        Returns:
            str: Formatted text with numbered results
        """
        formatted = ""
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result.get('title', 'N/A')}\n"
            formatted += f"   {result.get('snippet', 'N/A')}\n"
        return formatted

    def _format_competitor_pricing(self, comp_pricing: list) -> str:
        """
        Format competitor pricing data for AI prompt.
        
        Args:
            comp_pricing (list): List of competitor pricing dictionaries
            
        Returns:
            str: Formatted text with competitor names and pricing results
        """
        formatted = ""
        for item in comp_pricing:
            formatted += f"\n{item.get('competitor', 'Unknown')}:\n"
            formatted += self._format_pricing_results(item.get('results', []))
        return formatted