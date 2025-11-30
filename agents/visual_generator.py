"""
Visual Generator Agent Module

This module implements the VisualGeneratorAgent class responsible for creating
professional data visualizations for multi-company comparisons.

The agent generates three types of charts:
1. Radar Chart - Multi-dimensional comparison across 8 key metrics
2. Bar Chart - Grouped comparison showing side-by-side metrics
3. Heatmap - Color-coded matrix showing relative performance

All charts are exported as high-resolution PNG files suitable for reports
and presentations.

Author: Ishan
Course: Google-Kaggle 5-Day AI Agents Intensive Course (Capstone Project)
Date: November 2025
"""

import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime
from api_config import GOOGLE_API_KEY
from google import genai
import re
import json


class VisualGeneratorAgent:
    """
    Agent responsible for generating professional comparison visualizations.
    
    This agent extracts quantitative metrics from qualitative analysis data
    using AI, then creates three types of professional charts for visual
    comparison of companies. All charts are publication-quality at 300 DPI.
    
    Attributes:
        client (genai.Client): Google Generative AI client instance
        model_id (str): Gemini model identifier for metric extraction
        
    Example:
        >>> visual_gen = VisualGeneratorAgent()
        >>> charts = visual_gen.generate_all_charts(companies_data)
        >>> print(charts['charts']['radar'])  # Path to radar chart
    """
    
    def __init__(self):
        """
        Initialize the VisualGeneratorAgent with Gemini AI and chart styling.
        
        Sets up the AI client for metric extraction and configures matplotlib
        and seaborn for professional-quality chart generation.
        """
        self.client = genai.Client(api_key=GOOGLE_API_KEY)
        self.model_id = 'gemini-2.5-flash'
        # Set style for professional charts
        sns.set_style('whitegrid')
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10

    def extract_comparison_metrics(self, companies_data: list) -> dict:
        """
        Extract quantitative metrics from qualitative analysis data using AI.
        
        Uses Gemini AI to analyze SWOT and competitive analysis text and
        extract numerical scores (1-10 scale) across 8 standardized metrics
        for objective comparison visualization.
        
        Metrics extracted:
        - Market Position
        - Product Quality
        - Innovation
        - Pricing Value
        - Customer Satisfaction
        - Growth Potential
        - Brand Strength
        - Technology Stack
        
        Args:
            companies_data (list): List of company analysis dictionaries.
                Each should contain 'company_name', 'swot_analysis',
                'competitive_analysis'
                
        Returns:
            dict: Metrics dictionary with structure:
                {
                    'Company1': {
                        'Market Position': 8,
                        'Product Quality': 9,
                        ...
                    },
                    'Company2': {...}
                }
                
        Raises:
            json.JSONDecodeError: Falls back to dummy data if parsing fails
            
        Example:
            >>> metrics = agent.extract_comparison_metrics(companies_data)
            >>> print(metrics['Netflix']['Innovation'])
            8
            
        Note:
            - Uses AI to ensure consistent scoring across companies
            - Falls back to random dummy data if extraction fails
            - Scores are on 1-10 scale for standardization
        """
        print('\n📊 Extracting metrics for visualization...')

        company_names = [data['company_name'] for data in companies_data]

        # Use Gemini to extract structured data for charts
        prompt = f'''
Based on the following company analysis data, extract numerical scores (1-10 scale) for comparison.

Companies: {', '.join(company_names)}

Data for each company:
'''

        for i, data in enumerate(companies_data, 1):
            prompt += f'''
Company {i}: {data['company_name']}
SWOT: {data.get('swot_analysis', {}).get('swot_analysis', 'N/A')[:500]}
Competitive Analysis: {data.get('competitive_analysis', {}).get('competitive_analysis', 'N/A')[:500]}
'''

        prompt += '''
Extract comparison scores (1-10) for these categories:
1. Market Position
2. Product Quality
3. Innovation
4. Pricing Value
5. Customer Satisfaction
6. Growth Potential
7. Brand Strength
8. Technology Stack

Respond ONLY with valid JSON in this exact format:
{
  "Company1Name": {
    "Market Position": 8,
    "Product Quality": 9,
    "Innovation": 7,
    "Pricing Value": 6,
    "Customer Satisfaction": 8,
    "Growth Potential": 9,
    "Brand Strength": 7,
    "Technology Stack": 8
  },
  "Company2Name": {
    ...
  }
}

DO NOT include any text outside the JSON. Only output valid JSON.
'''

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )

        # Parse JSON response
        try:
            # Clean response - remove markdown code blocks if present
            response_text = response.text.strip()
            response_text = re.sub(r'```json\n?', '', response_text)
            response_text = re.sub(r'```\n?', '', response_text)

            metrics = json.loads(response_text)
            print('✅ Metrics extracted successfully')
            return metrics
        except json.JSONDecodeError as e:
            print(f'⚠️  Failed to parse metrics: {e}')
            # Return dummy data as fallback
            return self._create_dummy_metrics(company_names)

    def _create_dummy_metrics(self, company_names: list) -> dict:
        """
        Create fallback dummy metrics if AI extraction fails.
        
        Generates random but reasonable scores (5-9 range) for all metrics
        when AI-based extraction encounters errors.
        
        Args:
            company_names (list): List of company names to generate metrics for
            
        Returns:
            dict: Dummy metrics with random scores for all categories
            
        Note:
            This is a fallback mechanism to ensure charts can still be generated
        """
        categories = ['Market Position', 'Product Quality', 'Innovation', 'Pricing Value',
                     'Customer Satisfaction', 'Growth Potential', 'Brand Strength', 'Technology Stack']

        import random
        metrics = {}
        for company in company_names:
            metrics[company] = {cat: random.randint(5, 9) for cat in categories}

        return metrics

    def generate_radar_chart(self, metrics: dict, output_path: str):
        """
        Generate professional radar (spider) chart for multi-dimensional comparison.
        
        Creates a polar radar chart showing companies across 8 metrics,
        with color-coded lines and semi-transparent fills for easy comparison.
        
        Args:
            metrics (dict): Company metrics dictionary from extract_comparison_metrics()
            output_path (str): File path to save the PNG chart
            
        Returns:
            None (saves chart to file)
            
        Raises:
            IOError: If file write fails
            
        Example:
            >>> metrics = {'Netflix': {...}, 'Hulu': {...}}
            >>> agent.generate_radar_chart(metrics, 'comparison_radar.png')
            
        Note:
            - Saved at 300 DPI for publication quality
            - Uses professional color scheme (#3b82f6, #ef4444, etc.)
            - Includes legend and gridlines
        """
        print('  📊 Creating radar chart...')

        categories = list(list(metrics.values())[0].keys())
        num_vars = len(categories)

        # Compute angle for each axis
        angles = [n / float(num_vars) * 2 * 3.14159 for n in range(num_vars)]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

        colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6']

        for idx, (company, scores) in enumerate(metrics.items()):
            values = list(scores.values())
            values += values[:1]

            ax.plot(angles, values, 'o-', linewidth=2, label=company, color=colors[idx % len(colors)])
            ax.fill(angles, values, alpha=0.15, color=colors[idx % len(colors)])

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, size=10)
        ax.set_ylim(0, 10)
        ax.set_yticks([2, 4, 6, 8, 10])
        ax.set_yticklabels(['2', '4', '6', '8', '10'], size=8)
        ax.grid(True, linestyle='--', alpha=0.7)

        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)
        plt.title('Multi-Company Comparison - Radar Chart', size=16, weight='bold', pad=20)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f'  ✅ Radar chart saved: {output_path}')

    def generate_bar_comparison(self, metrics: dict, output_path: str):
        """
        Generate grouped bar chart for side-by-side metric comparison.
        
        Creates a professional bar chart with grouped bars showing each
        company's scores across all metrics for easy visual comparison.
        
        Args:
            metrics (dict): Company metrics dictionary from extract_comparison_metrics()
            output_path (str): File path to save the PNG chart
            
        Returns:
            None (saves chart to file)
            
        Raises:
            IOError: If file write fails
            
        Example:
            >>> agent.generate_bar_comparison(metrics, 'comparison_bars.png')
            
        Note:
            - Bars grouped by metric for easy comparison
            - Y-axis fixed at 0-10 scale
            - Includes gridlines and legend
            - Saved at 300 DPI
        """
        print('  📊 Creating bar chart...')

        # Prepare data
        df_data = []
        for company, scores in metrics.items():
            for category, score in scores.items():
                df_data.append({'Company': company, 'Category': category, 'Score': score})

        df = pd.DataFrame(df_data)

        # Create plot
        fig, ax = plt.subplots(figsize=(14, 8))

        categories = df['Category'].unique()
        x = range(len(categories))
        width = 0.8 / len(metrics)

        colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6']

        for idx, company in enumerate(metrics.keys()):
            company_data = df[df['Company'] == company]
            scores = [company_data[company_data['Category'] == cat]['Score'].values[0] for cat in categories]
            offset = (idx - len(metrics)/2 + 0.5) * width
            ax.bar([i + offset for i in x], scores, width, label=company, color=colors[idx % len(colors)])

        ax.set_xlabel('Metrics', fontsize=12, weight='bold')
        ax.set_ylabel('Score (1-10)', fontsize=12, weight='bold')
        ax.set_title('Company Comparison - Bar Chart', fontsize=16, weight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.legend(fontsize=10)
        ax.grid(axis='y', alpha=0.3)
        ax.set_ylim(0, 10)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f'  ✅ Bar chart saved: {output_path}')

    def generate_heatmap(self, metrics: dict, output_path: str):
        """
        Generate color-coded heatmap for metric comparison matrix.
        
        Creates a professional heatmap with color gradients showing relative
        performance across companies and metrics. Red-Yellow-Green color scheme
        with values annotated in each cell.
        
        Args:
            metrics (dict): Company metrics dictionary from extract_comparison_metrics()
            output_path (str): File path to save the PNG chart
            
        Returns:
            None (saves chart to file)
            
        Raises:
            IOError: If file write fails
            
        Example:
            >>> agent.generate_heatmap(metrics, 'comparison_heatmap.png')
            
        Note:
            - Uses RdYlGn (Red-Yellow-Green) colormap centered at 5
            - Shows actual scores in each cell
            - Saved at 300 DPI for clarity
        """
        print('  📊 Creating heatmap...')

        # Convert metrics to DataFrame
        df = pd.DataFrame(metrics).T

        fig, ax = plt.subplots(figsize=(12, 6))

        sns.heatmap(df, annot=True, fmt='.1f', cmap='RdYlGn', center=5,
                   vmin=0, vmax=10, cbar_kws={'label': 'Score'},
                   linewidths=0.5, linecolor='white', ax=ax)

        ax.set_title('Company Metrics Heatmap', fontsize=16, weight='bold', pad=20)
        ax.set_xlabel('Metrics', fontsize=12, weight='bold')
        ax.set_ylabel('Companies', fontsize=12, weight='bold')

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f'  ✅ Heatmap saved: {output_path}')

    def generate_all_charts(self, companies_data: list) -> dict:
        """
        Generate all three chart types for comprehensive visual comparison.
        
        Orchestrates the complete chart generation pipeline:
        1. Extract metrics from analysis data
        2. Generate radar chart
        3. Generate bar chart
        4. Generate heatmap
        
        All charts are timestamped and include company names in filenames.
        
        Args:
            companies_data (list): List of company analysis dictionaries
            
        Returns:
            dict: Chart paths and metrics with structure:
                {
                    'charts': {
                        'radar': str (file path),
                        'bar': str (file path),
                        'heatmap': str (file path)
                    },
                    'metrics': dict (extracted metric scores)
                }
                
        Raises:
            Exception: If chart generation fails
            
        Example:
            >>> companies_data = [netflix_data, hulu_data]
            >>> result = agent.generate_all_charts(companies_data)
            >>> print(result['charts']['radar'])
            chart_radar_Netflix_vs_Hulu_20251130_191252.png
            
        Note:
            - Filename format: chart_{type}_{Co1}_vs_{Co2}_{timestamp}.png
            - All charts saved in current directory
            - Returns both chart paths and raw metrics for reference
        """
        print('\n📊 Generating visual comparisons...')

        # Extract metrics
        metrics = self.extract_comparison_metrics(companies_data)

        # Create output directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        company_names = [data['company_name'] for data in companies_data]
        base_name = '_vs_'.join([name.replace(' ', '_') for name in company_names])

        # Generate charts
        charts = {}

        radar_path = f'chart_radar_{base_name}_{timestamp}.png'
        self.generate_radar_chart(metrics, radar_path)
        charts['radar'] = radar_path

        bar_path = f'chart_bars_{base_name}_{timestamp}.png'
        self.generate_bar_comparison(metrics, bar_path)
        charts['bar'] = bar_path

        heatmap_path = f'chart_heatmap_{base_name}_{timestamp}.png'
        self.generate_heatmap(metrics, heatmap_path)
        charts['heatmap'] = heatmap_path

        print(f'\n✅ Generated {len(charts)} charts')

        return {
            'charts': charts,
            'metrics': metrics
        }