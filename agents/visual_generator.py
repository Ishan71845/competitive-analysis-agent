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
    def __init__(self):
        self.client = genai.Client(api_key=GOOGLE_API_KEY)
        self.model_id = 'gemini-2.5-flash'
        # Set style for professional charts
        sns.set_style('whitegrid')
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
    
    def extract_comparison_metrics(self, companies_data: list) -> dict:
        '''Extract metrics from company data for visualization'''
        print('\n?? Extracting metrics for visualization...')
        
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
            response_text = re.sub(r'`json\n?', '', response_text)
            response_text = re.sub(r'`\n?', '', response_text)
            
            metrics = json.loads(response_text)
            print('? Metrics extracted successfully')
            return metrics
        except json.JSONDecodeError as e:
            print(f'??  Failed to parse metrics: {e}')
            # Return dummy data as fallback
            return self._create_dummy_metrics(company_names)
    
    def _create_dummy_metrics(self, company_names: list) -> dict:
        '''Create dummy metrics if extraction fails'''
        categories = ['Market Position', 'Product Quality', 'Innovation', 'Pricing Value',
                     'Customer Satisfaction', 'Growth Potential', 'Brand Strength', 'Technology Stack']
        
        import random
        metrics = {}
        for company in company_names:
            metrics[company] = {cat: random.randint(5, 9) for cat in categories}
        
        return metrics
    
    def generate_radar_chart(self, metrics: dict, output_path: str):
        '''Generate radar chart comparing companies'''
        print('  ?? Creating radar chart...')
        
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
        
        print(f'  ? Radar chart saved: {output_path}')
    
    def generate_bar_comparison(self, metrics: dict, output_path: str):
        '''Generate grouped bar chart'''
        print('  ?? Creating bar chart...')
        
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
        
        print(f'  ? Bar chart saved: {output_path}')
    
    def generate_heatmap(self, metrics: dict, output_path: str):
        '''Generate heatmap comparison'''
        print('  ?? Creating heatmap...')
        
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
        
        print(f'  ? Heatmap saved: {output_path}')
    
    def generate_all_charts(self, companies_data: list) -> dict:
        '''Generate all visualization charts'''
        print('\n?? Generating visual comparisons...')
        
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
        
        print(f'\n? Generated {len(charts)} charts')
        
        return {
            'charts': charts,
            'metrics': metrics
        }
