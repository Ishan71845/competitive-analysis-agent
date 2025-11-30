"""
Comparison Agent Module

This module implements the ComparisonAgent class responsible for performing
multi-company comparative analysis. It synthesizes data from multiple companies
to create side-by-side comparisons and strategic insights.

The agent provides comprehensive comparative analysis including market positioning,
product comparison, competitive advantages/weaknesses, pricing strategies, and
strategic recommendations across 2-5 companies simultaneously.

Author: Ishan
Course: Google-Kaggle 5-Day AI Agents Intensive Course (Capstone Project)
Date: November 2025
"""

import os
from api_config import GOOGLE_API_KEY
from google import genai
from datetime import datetime


class ComparisonAgent:
    """
    Agent responsible for multi-company comparative analysis.
    
    This agent takes analysis data from multiple companies and creates
    comprehensive side-by-side comparisons, identifying leaders in various
    categories and providing strategic insights on competitive positioning.
    
    Attributes:
        client (genai.Client): Google Generative AI client instance
        model_id (str): Gemini model identifier for comparative analysis
        
    Example:
        >>> comparison_agent = ComparisonAgent()
        >>> comparison = comparison_agent.compare_companies([data1, data2, data3])
        >>> report = comparison_agent.generate_comparison_report(comparison)
        >>> filename = comparison_agent.save_comparison_report(report, ["Co1", "Co2"])
    """
    
    def __init__(self):
        """
        Initialize the ComparisonAgent with Gemini AI client.
        
        Sets up the Google Generative AI client for generating multi-company
        comparative analysis and strategic insights.
        """
        self.client = genai.Client(api_key=GOOGLE_API_KEY)
        self.model_id = 'gemini-2.5-flash'
    
    def compare_companies(self, companies_data: list) -> dict:
        """
        Compare multiple companies and generate comprehensive comparative analysis.
        
        Performs deep comparative analysis across 2-5 companies, covering:
        - Market position comparison
        - Product & service comparison
        - Competitive advantages and weaknesses
        - Pricing strategy comparison
        - SWOT comparison matrix
        - Head-to-head analysis
        - Strategic positioning
        - Winner analysis (by category)
        - Final verdict
        
        Args:
            companies_data (list): List of company data dictionaries (2-5 companies).
                Each dict should contain:
                    - 'company_name': str
                    - 'company_research': dict with 'summary'
                    - 'competitors_research': dict with 'identified_competitors'
                    - 'competitive_analysis': dict with 'competitive_analysis'
                    - 'swot_analysis': dict with 'swot_analysis'
                    - 'pricing_analysis': dict with 'analysis'
                    
        Returns:
            dict: Comprehensive comparison analysis with structure:
                {
                    'comparison_analysis': str,     # Full comparative analysis
                    'companies_compared': list,     # List of company names
                    'comparison_date': str          # Timestamp of analysis
                }
                
        Raises:
            Exception: If AI analysis fails or insufficient data provided
            
        Example:
            >>> companies_data = [
            ...     {'company_name': 'Slack', 'company_research': {...}, ...},
            ...     {'company_name': 'Microsoft Teams', 'company_research': {...}, ...}
            ... ]
            >>> result = agent.compare_companies(companies_data)
            >>> print(result['comparison_analysis'][:200])
            
            ## Comparative Analysis: Slack vs Microsoft Teams
            
            ### 1. Market Position Comparison
            Slack maintains strong position in SMB segment...
            
        Note:
            - Supports 2-5 companies for optimal comparison depth
            - Analysis is data-driven using provided company research
            - Provides objective, balanced comparisons
        """
        print(f'\n🔄 Comparing {len(companies_data)} companies...')
        
        company_names = [data['company_name'] for data in companies_data]
        
        # Prepare comparison data
        comparison_prompt = f'''
You are a business analyst comparing multiple companies. Based on the comprehensive data provided for each company, create a detailed comparative analysis.

COMPANIES BEING COMPARED: {', '.join(company_names)}

'''
        
        # Add each company's data
        for i, company_data in enumerate(companies_data, 1):
            company_name = company_data['company_name']
            comparison_prompt += f'''
{'=' * 80}
COMPANY {i}: {company_name}
{'=' * 80}

Company Overview:
{company_data.get('company_research', {}).get('summary', 'N/A')}

Competitors:
{company_data.get('competitors_research', {}).get('identified_competitors', 'N/A')}

Competitive Analysis:
{company_data.get('competitive_analysis', {}).get('competitive_analysis', 'N/A')}

SWOT Analysis:
{company_data.get('swot_analysis', {}).get('swot_analysis', 'N/A')}

Pricing:
{company_data.get('pricing_analysis', {}).get('analysis', 'N/A')}

'''
        
        comparison_prompt += f'''
Based on ALL the above data, create a comprehensive multi-company comparison with these sections:

## Comparative Analysis: {' vs '.join(company_names)}

### 1. Market Position Comparison
Compare how each company is positioned in the market:
- Market share and dominance
- Target audience and segments
- Geographic presence
- Brand strength

### 2. Product & Service Comparison
Compare offerings:
- Core products/services
- Feature differentiation
- Innovation and unique value propositions
- Product maturity

### 3. Competitive Advantages
For each company, identify:
- Unique strengths
- What makes them stand out
- Areas where they lead

### 4. Competitive Weaknesses
For each company, identify:
- Vulnerabilities
- Areas where competitors have advantage
- Market gaps they haven't filled

### 5. Pricing Strategy Comparison
Compare pricing approaches:
- Pricing models
- Value positioning (premium vs budget)
- Pricing flexibility

### 6. SWOT Comparison Matrix
Create a side-by-side comparison of:
- Key strengths of each
- Main weaknesses of each
- Biggest opportunities
- Common threats

### 7. Head-to-Head Analysis
Direct comparison addressing:
- Who is winning in different segments?
- Feature parity analysis
- Customer preference indicators

### 8. Strategic Positioning
- Where each company fits in the competitive landscape
- Future trajectory predictions
- Strategic moves to watch

### 9. Winner Analysis
For different criteria, identify the leader:
- Best for enterprise customers
- Best for startups/SMBs
- Best pricing value
- Best innovation
- Best market position

### 10. Final Verdict
Overall comparison summary and insights.

Be specific, data-driven, and objective. Use the actual information provided for each company.
'''
        
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=comparison_prompt
        )
        
        comparison = {
            'comparison_analysis': response.text,
            'companies_compared': company_names,
            'comparison_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print(f'✅ Multi-company comparison complete')
        
        return comparison
    
    def generate_comparison_report(self, comparison_data: dict) -> str:
        """
        Generate formatted markdown report for multi-company comparison.
        
        Creates a professional markdown document with comparison analysis,
        metadata, and proper formatting suitable for export and presentation.
        
        Args:
            comparison_data (dict): Comparison analysis results from compare_companies().
                Expected keys:
                    - 'comparison_analysis': str (main analysis content)
                    - 'companies_compared': list (company names)
                    - 'comparison_date': str (timestamp)
                    
        Returns:
            str: Complete markdown-formatted comparison report
            
        Example:
            >>> comparison = agent.compare_companies(companies_data)
            >>> report = agent.generate_comparison_report(comparison)
            >>> print(report[:150])
            
            # Multi-Company Competitive Comparison
            *Comparing: Amazon, Flipkart, Walmart*
            *Generated on November 30, 2025 at 19:36*
            
        Note:
            - Includes report metadata and timestamps
            - Professional formatting with headers and sections
            - Ready for markdown or PDF export
        """
        company_names = comparison_data['companies_compared']
        
        report = f'''# Multi-Company Competitive Comparison
*Comparing: {', '.join(company_names)}*
*Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}*

---

{comparison_data['comparison_analysis']}

---

## Report Metadata
- **Companies Analyzed**: {len(company_names)}
- **Companies**: {', '.join(company_names)}
- **Analysis Date**: {comparison_data['comparison_date']}
- **Report Type**: Multi-Company Comparative Analysis

---

*Generated by Competitive Analysis Agent*
'''
        
        return report
    
    def save_comparison_report(self, report: str, company_names: list) -> str:
        """
        Save comparison report to markdown file with timestamp.
        
        Creates a timestamped markdown file in the current directory with
        company names in the filename for easy identification.
        
        Args:
            report (str): Complete markdown-formatted report content
            company_names (list): List of company names being compared
            
        Returns:
            str: Filename of the saved comparison report
            
        Raises:
            IOError: If file write fails
            
        Example:
            >>> filename = agent.save_comparison_report(report, ["Slack", "Teams"])
            >>> print(filename)
            comparison_Slack_vs_Teams_20251130_193633.md
            
        Note:
            - Filename format: comparison_{Co1}_vs_{Co2}_vs_{Co3}_{timestamp}.md
            - Spaces in company names replaced with underscores
            - Timestamp format: YYYYMMDD_HHMMSS
        """
        companies_str = '_vs_'.join([name.replace(' ', '_') for name in company_names])
        filename = f'comparison_{companies_str}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f'\n📄 Comparison report saved to: {filename}')
        
        return filename