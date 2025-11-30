"""
Competitive Analysis Agent - CLI Interface

This module provides a command-line interface for performing competitive analysis
on companies using AI-powered agents. Supports both single company analysis and
multi-company comparisons with visual charts.

Author: Ishan
Course: Google-Kaggle 5-Day AI Agents Intensive Course (Capstone Project)
Date: November 2025
"""

import os
from dotenv import load_dotenv
from agents.researcher import ResearcherAgent
from agents.analyst import AnalystAgent
from agents.report_generator import ReportGeneratorAgent
from agents.comparison_agent import ComparisonAgent
from agents.visual_generator import VisualGeneratorAgent

load_dotenv()


def single_company_analysis():
    """
    Run comprehensive competitive analysis for a single company.
    
    This function orchestrates a 6-step analysis process:
    1. Company research (background, products, market position)
    2. Competitor identification and research
    3. Competitive landscape analysis
    4. SWOT analysis generation
    5. Pricing strategy analysis
    6. Final report compilation and export
    
    The analysis results are saved as a markdown file in the current directory.
    
    Returns:
        None
        
    Raises:
        Exception: If any step in the analysis pipeline fails
        
    Example:
        >>> single_company_analysis()
        Enter the company name to analyze: Netflix
        🎯 Starting competitive analysis for: Netflix
        ...
        ✅ ANALYSIS COMPLETE!
        📄 Report saved as: Netflix_competitive_analysis_20251130_190229.md
    """
    print('=' * 60)
    print('🚀 COMPETITIVE ANALYSIS AGENT')
    print('=' * 60)
    
    # Get company name from user
    company_name = input('\nEnter the company name to analyze: ').strip()
    
    if not company_name:
        print('❌ Company name cannot be empty!')
        return
    
    print(f'\n🎯 Starting competitive analysis for: {company_name}')
    print('=' * 60)
    
    # Initialize agents
    researcher = ResearcherAgent()
    analyst = AnalystAgent()
    report_generator = ReportGeneratorAgent()
    
    # Store all data
    all_data = {}
    
    try:
        # Step 1: Research the company
        print('\n' + '=' * 60)
        print('STEP 1: COMPANY RESEARCH')
        print('=' * 60)
        company_research = researcher.research_company(company_name)
        all_data['company_research'] = company_research
        
        # Step 2: Research competitors
        print('\n' + '=' * 60)
        print('STEP 2: COMPETITOR RESEARCH')
        print('=' * 60)
        competitors_research = researcher.research_competitors(company_name)
        all_data['competitors_research'] = competitors_research
        
        # Step 3: Competitive analysis
        print('\n' + '=' * 60)
        print('STEP 3: COMPETITIVE ANALYSIS')
        print('=' * 60)
        competitive_analysis = analyst.analyze_competition(company_research, competitors_research)
        all_data['competitive_analysis'] = competitive_analysis
        
        # Step 4: SWOT analysis
        print('\n' + '=' * 60)
        print('STEP 4: SWOT ANALYSIS')
        print('=' * 60)
        swot_analysis = analyst.generate_swot(company_research, competitive_analysis)
        all_data['swot_analysis'] = swot_analysis
        
        # Step 5: Pricing analysis
        print('\n' + '=' * 60)
        print('STEP 5: PRICING ANALYSIS')
        print('=' * 60)
        competitors_list = [company_name]
        pricing_analysis = analyst.analyze_pricing(company_name, competitors_list)
        all_data['pricing_analysis'] = pricing_analysis
        
        # Step 6: Generate final report
        print('\n' + '=' * 60)
        print('STEP 6: GENERATING FINAL REPORT')
        print('=' * 60)
        final_report = report_generator.generate_final_report(company_name, all_data)
        
        # Save report
        filename = report_generator.save_report(final_report, company_name)
        
        print('\n' + '=' * 60)
        print('✅ ANALYSIS COMPLETE!')
        print('=' * 60)
        print(f'\n📄 Report saved as: {filename}')
        print('\nYou can now open the report file to view the complete analysis.')
        
    except Exception as e:
        print(f'\n❌ Error occurred: {e}')
        import traceback
        traceback.print_exc()


def multi_company_comparison():
    """
    Run multi-company comparison analysis with visual charts.
    
    This function performs comparative analysis across 2-5 companies, including:
    - Individual analysis of each company
    - Side-by-side comparison of key metrics
    - Visual comparisons (radar chart, bar chart, heatmap)
    - Comprehensive comparison report
    
    All results are saved as markdown reports and PNG chart files.
    
    Returns:
        None
        
    Raises:
        Exception: If analysis fails for any company or chart generation fails
        
    Example:
        >>> multi_company_comparison()
        How many companies do you want to compare? (2-5): 2
        Enter company #1 name: Amazon
        Enter company #2 name: Flipkart
        🎯 Comparing: Amazon, Flipkart
        ...
        ✅ COMPARISON COMPLETE!
        📄 Report saved as: comparison_Amazon_vs_Flipkart_20251130_200505.md
    """
    print('=' * 60)
    print('🔄 MULTI-COMPANY COMPARISON')
    print('=' * 60)
    
    # Get number of companies
    while True:
        try:
            num_companies = int(input('\nHow many companies do you want to compare? (2-5): ').strip())
            if 2 <= num_companies <= 5:
                break
            else:
                print('⚠️  Please enter a number between 2 and 5')
        except ValueError:
            print('⚠️  Please enter a valid number')
    
    # Get company names
    companies = []
    for i in range(num_companies):
        company = input(f'Enter company #{i+1} name: ').strip()
        if company:
            companies.append(company)
        else:
            print('❌ Company name cannot be empty!')
            return
    
    print(f'\n🎯 Comparing: {", ".join(companies)}')
    print('=' * 60)
    
    # Analyze each company
    companies_data = []
    researcher = ResearcherAgent()
    analyst = AnalystAgent()
    
    for idx, company_name in enumerate(companies, 1):
        print(f'\n[{idx}/{len(companies)}] ' + '=' * 50)
        print(f'Analyzing: {company_name}')
        print('=' * 50)
        
        company_data = {'company_name': company_name}
        
        try:
            print('🔍 Researching company...')
            company_data['company_research'] = researcher.research_company(company_name)
            
            print('🏢 Identifying competitors...')
            company_data['competitors_research'] = researcher.research_competitors(company_name)
            
            print('📊 Analyzing competition...')
            company_data['competitive_analysis'] = analyst.analyze_competition(
                company_data['company_research'],
                company_data['competitors_research']
            )
            
            print('💡 Generating SWOT...')
            company_data['swot_analysis'] = analyst.generate_swot(
                company_data['company_research'],
                company_data['competitive_analysis']
            )
            
            print('💰 Analyzing pricing...')
            company_data['pricing_analysis'] = analyst.analyze_pricing(company_name, [company_name])
            
            companies_data.append(company_data)
            print(f'✅ {company_name} analysis complete')
            
        except Exception as e:
            print(f'❌ Error analyzing {company_name}: {e}')
            print(f'⚠️  Skipping {company_name}')
    
    if len(companies_data) < 2:
        print('\n❌ Need at least 2 companies to compare!')
        return
    
    # Generate comparison
    print('\n' + '=' * 60)
    print('GENERATING COMPARISON REPORT')
    print('=' * 60)
    
    comparison_agent = ComparisonAgent()
    comparison_data = comparison_agent.compare_companies(companies_data)
    
    # Generate visualizations
    print('\n' + '=' * 60)
    print('GENERATING VISUAL CHARTS')
    print('=' * 60)
    
    visual_generator = VisualGeneratorAgent()
    visual_data = visual_generator.generate_all_charts(companies_data)
    
    # Create and save report
    report = comparison_agent.generate_comparison_report(comparison_data)
    
    # Add chart references to report
    report += f'\n\n## Visual Comparisons\n\n'
    report += f'Charts have been generated:\n'
    for chart_type, chart_path in visual_data['charts'].items():
        report += f'- **{chart_type.title()} Chart**: `{chart_path}`\n'
    
    filename = comparison_agent.save_comparison_report(report, [d['company_name'] for d in companies_data])
    
    print('\n' + '=' * 60)
    print('✅ COMPARISON COMPLETE!')
    print('=' * 60)
    print(f'\n📄 Report saved as: {filename}')
    print(f'\n📊 Charts generated:')
    for chart_type, chart_path in visual_data['charts'].items():
        print(f'   - {chart_type.title()}: {chart_path}')
    print('\nYou can now open the report and chart files!')


def main():
    """
    Main entry point for the CLI interface.
    
    Presents a menu allowing users to choose between:
    1. Single Company Analysis - Detailed analysis of one company
    2. Multi-Company Comparison - Comparative analysis with visualizations
    3. Exit - Quit the application
    
    The function runs in a loop until the user chooses to exit.
    
    Returns:
        None
        
    Example:
        >>> main()
        🚀 COMPETITIVE ANALYSIS AGENT
        Select analysis mode:
        1. Single Company Analysis
        2. Multi-Company Comparison (with visual charts)
        3. Exit
        Enter your choice (1-3):
    """
    print('=' * 60)
    print('🚀 COMPETITIVE ANALYSIS AGENT')
    print('=' * 60)
    print('\nSelect analysis mode:')
    print('1. Single Company Analysis')
    print('2. Multi-Company Comparison (with visual charts)')
    print('3. Exit')
    
    while True:
        choice = input('\nEnter your choice (1-3): ').strip()
        
        if choice == '1':
            print()
            single_company_analysis()
            break
        elif choice == '2':
            print()
            multi_company_comparison()
            break
        elif choice == '3':
            print('👋 Goodbye!')
            break
        else:
            print('⚠️  Invalid choice. Please enter 1, 2, or 3.')


if __name__ == '__main__':
    main()