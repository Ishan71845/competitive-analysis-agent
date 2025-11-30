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
    def __init__(self):
        self.client = genai.Client(api_key=GOOGLE_API_KEY)
        self.model_id = "gemini-2.5-flash"
        
    def analyze_competition(self, company_data: dict, competitors_data: dict) -> dict:
        """Perform competitive analysis"""
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
        """Generate SWOT analysis"""
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
        """Analyze pricing strategies"""
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
        """Format pricing results"""
        formatted = ""
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result.get('title', 'N/A')}\n"
            formatted += f"   {result.get('snippet', 'N/A')}\n"
        return formatted
    
    def _format_competitor_pricing(self, comp_pricing: list) -> str:
        """Format competitor pricing"""
        formatted = ""
        for item in comp_pricing:
            formatted += f"\n{item.get('competitor', 'Unknown')}:\n"
            formatted += self._format_pricing_results(item.get('results', []))
        return formatted
