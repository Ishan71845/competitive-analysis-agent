import os
from api_config import GOOGLE_API_KEY
from google import genai
from google.genai import types
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class ReportGeneratorAgent:
    def __init__(self):
        self.client = genai.Client(api_key=GOOGLE_API_KEY)
        self.model_id = "gemini-2.5-flash"
        
    def generate_final_report(self, company_name: str, all_data: dict) -> str:
        """Generate comprehensive final report"""
        print(f"\n📝 Generating final report for {company_name}...")
        
        prompt = f"""
You are a business intelligence analyst. Generate a comprehensive competitive analysis report.

Use ALL the following data to create a professional report:

COMPANY RESEARCH:
{all_data.get('company_research', {}).get('summary', 'N/A')}

IDENTIFIED COMPETITORS:
{all_data.get('competitors_research', {}).get('identified_competitors', 'N/A')}

COMPETITIVE ANALYSIS:
{all_data.get('competitive_analysis', {}).get('competitive_analysis', 'N/A')}

SWOT ANALYSIS:
{all_data.get('swot_analysis', {}).get('swot_analysis', 'N/A')}

PRICING ANALYSIS:
{all_data.get('pricing_analysis', {}).get('analysis', 'N/A')}

Create a professional report with these sections:

# Competitive Analysis Report: {company_name}
*Generated on {datetime.now().strftime('%B %d, %Y')}*

---

## Executive Summary
[2-3 paragraph overview of key findings]

---

## 1. Company Overview
[Details about {company_name}]

---

## 2. Competitive Landscape
[Overview of main competitors and market dynamics]

---

## 3. Competitive Analysis
[Detailed comparison with competitors]

---

## 4. SWOT Analysis
[Present the SWOT in clear format]

---

## 5. Pricing Strategy Analysis
[Pricing positioning and recommendations]

---

## 6. Strategic Recommendations
[3-5 actionable strategic recommendations based on the analysis]

---

## Conclusion
[Final thoughts and key takeaways]

Make it professional, data-driven, and actionable. Use markdown formatting.
"""
        
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )
        
        report = response.text
        
        print(f"✅ Final report generated!")
        
        return report
    
    def save_report(self, report: str, company_name: str) -> str:
        """Save report to file"""
        filename = f"{company_name.replace(' ', '_')}_competitive_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n💾 Report saved to: {filename}")
        
        return filename
