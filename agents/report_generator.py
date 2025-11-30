"""
Report Generator Agent Module

This module implements the ReportGeneratorAgent class responsible for compiling
comprehensive competitive analysis reports in professional markdown format.

The agent synthesizes data from all analysis stages into a cohesive,
professionally formatted final report with executive summary, detailed
sections, and strategic recommendations.

Author: Ishan
Course: Google-Kaggle 5-Day AI Agents Intensive Course (Capstone Project)
Date: November 2025
"""

import os
from api_config import GOOGLE_API_KEY
from google import genai
from google.genai import types
from datetime import datetime


class ReportGeneratorAgent:
    """
    Agent responsible for generating professional analysis reports.
    
    This agent takes raw analysis data from multiple sources (research,
    competitive analysis, SWOT, pricing) and compiles it into a comprehensive,
    professionally formatted markdown report suitable for business use.
    
    Attributes:
        client (genai.Client): Google Generative AI client instance
        model_id (str): Gemini model identifier for report generation
        
    Example:
        >>> generator = ReportGeneratorAgent()
        >>> report = generator.generate_final_report("Notion", all_analysis_data)
        >>> filename = generator.save_report(report, "Notion")
    """
    
    def __init__(self):
        """
        Initialize the ReportGeneratorAgent with Gemini AI client.
        
        Sets up the Google Generative AI client for generating professional
        business intelligence reports.
        """
        self.client = genai.Client(api_key=GOOGLE_API_KEY)
        self.model_id = 'gemini-2.5-flash'
    
    def generate_final_report(self, company_name: str, all_data: dict) -> str:
        """
        Generate comprehensive competitive analysis report.
        
        Compiles all analysis data into a professional markdown report with
        the following sections:
        - Executive Summary
        - Company Overview
        - Competitive Landscape
        - Competitive Analysis
        - SWOT Analysis
        - Pricing Strategy Analysis
        - Strategic Recommendations
        - Conclusion
        
        Args:
            company_name (str): Name of the company being analyzed
            all_data (dict): Complete analysis data with the following keys:
                - 'company_research': Company background and overview
                - 'competitors_research': Competitor identification
                - 'competitive_analysis': Market position analysis
                - 'swot_analysis': SWOT analysis results
                - 'pricing_analysis': Pricing strategy analysis
                
        Returns:
            str: Complete markdown-formatted report ready for export
            
        Raises:
            Exception: If AI report generation fails
            
        Example:
            >>> all_data = {
            ...     'company_research': {...},
            ...     'competitors_research': {...},
            ...     'competitive_analysis': {...},
            ...     'swot_analysis': {...},
            ...     'pricing_analysis': {...}
            ... }
            >>> report = generator.generate_final_report("Slack", all_data)
            >>> print(report[:100])
            # Competitive Analysis Report: Slack
            *Generated on November 30, 2025*
            
        Note:
            - Report is formatted in markdown with proper headings
            - Includes metadata and timestamps
            - Professional tone suitable for business stakeholders
        """
        print(f'\n📝 Generating final report for {company_name}...')
        
        prompt = f'''
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
'''
        
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )
        
        report = response.text
        
        print(f'✅ Final report generated!')
        
        return report
    
    def save_report(self, report: str, company_name: str) -> str:
        """
        Save report to markdown file with timestamp.
        
        Creates a timestamped markdown file in the current directory with
        the complete analysis report.
        
        Args:
            report (str): Complete markdown-formatted report content
            company_name (str): Name of the company (used in filename)
            
        Returns:
            str: Filename of the saved report
            
        Raises:
            IOError: If file write fails
            
        Example:
            >>> filename = generator.save_report(report_text, "Notion")
            >>> print(filename)
            Notion_competitive_analysis_20251130_190229.md
            
        Note:
            - Filename format: {company}_competitive_analysis_{timestamp}.md
            - Spaces in company names are replaced with underscores
            - Timestamp format: YYYYMMDD_HHMMSS
        """
        filename = f'{company_name.replace(" ", "_")}_competitive_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f'\n📄 Report saved to: {filename}')
        
        return filename