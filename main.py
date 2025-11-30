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
from utils.memory import MemoryManager

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
    Session state and conversation history are tracked using MemoryManager.
    
    Returns:
        None
        
    Raises:
        Exception: If any step in the analysis pipeline fails
        
    Example:
        >>> single_company_analysis()
        Enter the company name to analyze: Netflix
        🎯 Starting competitive analysis for: Netflix
        📊 Session ID: session_20251201_120000
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
    
    # Initialize memory manager for this session
    memory = MemoryManager()
    memory.add_message('user', f'Analyze {company_name}')
    memory.store_analysis_result('company_name', company_name)
    
    print(f'\n🎯 Starting competitive analysis for: {company_name}')
    print(f'📊 Session ID: {memory.session_id}')
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
        memory.add_message('system', 'Starting company research', 
                          metadata={'step': 1, 'agent': 'ResearcherAgent'})
        
        company_research = researcher.research_company(company_name)
        all_data['company_research'] = company_research
        
        memory.add_message('agent', f'Completed research for {company_name}', 
                          metadata={'step': 1, 'agent': 'ResearcherAgent'})
        memory.increment_analysis_count()
        
        # Step 2: Research competitors
        print('\n' + '=' * 60)
        print('STEP 2: COMPETITOR RESEARCH')
        print('=' * 60)
        memory.add_message('system', 'Starting competitor research', 
                          metadata={'step': 2, 'agent': 'ResearcherAgent'})
        
        competitors_research = researcher.research_competitors(company_name)
        all_data['competitors_research'] = competitors_research
        
        memory.add_message('agent', 'Competitors identified', 
                          metadata={'step': 2, 'agent': 'ResearcherAgent'})
        
        # Step 3: Competitive analysis
        print('\n' + '=' * 60)
        print('STEP 3: COMPETITIVE ANALYSIS')
        print('=' * 60)
        memory.add_message('system', 'Starting competitive analysis', 
                          metadata={'step': 3, 'agent': 'AnalystAgent'})
        
        competitive_analysis = analyst.analyze_competition(company_research, competitors_research)
        all_data['competitive_analysis'] = competitive_analysis
        
        memory.add_message('agent', 'Competitive analysis complete', 
                          metadata={'step': 3, 'agent': 'AnalystAgent'})
        
        # Step 4: SWOT analysis
        print('\n' + '=' * 60)
        print('STEP 4: SWOT ANALYSIS')
        print('=' * 60)
        memory.add_message('system', 'Starting SWOT analysis', 
                          metadata={'step': 4, 'agent': 'AnalystAgent'})
        
        swot_analysis = analyst.generate_swot(company_research, competitive_analysis)
        all_data['swot_analysis'] = swot_analysis
        
        memory.add_message('agent', 'SWOT analysis complete', 
                          metadata={'step': 4, 'agent': 'AnalystAgent'})
        
        # Step 5: Pricing analysis
        print('\n' + '=' * 60)
        print('STEP 5: PRICING ANALYSIS')
        print('=' * 60)
        memory.add_message('system', 'Starting pricing analysis', 
                          metadata={'step': 5, 'agent': 'AnalystAgent'})
        
        competitors_list = [company_name]
        pricing_analysis = analyst.analyze_pricing(company_name, competitors_list)
        all_data['pricing_analysis'] = pricing_analysis
        
        memory.add_message('agent', 'Pricing analysis complete', 
                          metadata={'step': 5, 'agent': 'AnalystAgent'})
        
        # Step 6: Generate final report
        print('\n' + '=' * 60)
        print('STEP 6: GENERATING FINAL REPORT')
        print('=' * 60)
        memory.add_message('system', 'Generating final report', 
                          metadata={'step': 6, 'agent': 'ReportGeneratorAgent'})
        
        final_report = report_generator.generate_final_report(company_name, all_data)
        
        # Save report
        filename = report_generator.save_report(final_report, company_name)
        
        memory.add_message('agent', f'Report saved: {filename}', 
                          metadata={'step': 6, 'agent': 'ReportGeneratorAgent'})
        memory.store_analysis_result('report_filename', filename)
        
        print('\n' + '=' * 60)
        print('✅ ANALYSIS COMPLETE!')
        print('=' * 60)
        print(f'\n📄 Report saved as: {filename}')
        
        # Display session statistics
        stats = memory.get_session_stats()
        print(f'\n📊 Session Statistics:')
        print(f'   - Session ID: {stats["session_id"]}')
        print(f'   - Messages exchanged: {stats["message_count"]}')
        print(f'   - Analyses completed: {stats["analysis_count"]}')
        
        # Save session to file
        try:
            os.makedirs('sessions', exist_ok=True)
            session_file = f'sessions/{memory.session_id}.json'
            memory.save_to_file(session_file)
            print(f'   - Session saved: {session_file}')
        except Exception:
            pass  # Silent fail if session save fails
        
        print('\nYou can now open the report file to view the complete analysis.')
        
    except Exception as e:
        memory.add_message('system', f'Error occurred: {str(e)}', metadata={'error': True})
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
    Session state is tracked using MemoryManager.
    
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
    
    # Initialize memory manager for comparison session
    memory = MemoryManager()
    memory.add_message('user', f'Compare: {", ".join(companies)}')
    memory.store_analysis_result('companies', companies)
    memory.store_analysis_result('comparison_mode', True)
    
    print(f'\n🎯 Comparing: {", ".join(companies)}')
    print(f'📊 Session ID: {memory.session_id}')
    print('=' * 60)
    
    # Analyze each company
    companies_data = []
    researcher = ResearcherAgent()
    analyst = AnalystAgent()
    
    for idx, company_name in enumerate(companies, 1):
        print(f'\n[{idx}/{len(companies)}] ' + '=' * 50)
        print(f'Analyzing: {company_name}')
        print('=' * 50)
        
        memory.add_message('system', f'Starting analysis for {company_name}', 
                          metadata={'company_index': idx, 'total_companies': len(companies)})
        
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
            
            memory.add_message('agent', f'Completed analysis for {company_name}', 
                              metadata={'company_index': idx, 'success': True})
            memory.increment_analysis_count()
            
        except Exception as e:
            print(f'❌ Error analyzing {company_name}: {e}')
            print(f'⚠️  Skipping {company_name}')
            memory.add_message('system', f'Error analyzing {company_name}: {str(e)}', 
                              metadata={'company_index': idx, 'error': True})
    
    if len(companies_data) < 2:
        print('\n❌ Need at least 2 companies to compare!')
        memory.add_message('system', 'Comparison failed: insufficient data')
        return
    
    # Generate comparison
    print('\n' + '=' * 60)
    print('GENERATING COMPARISON REPORT')
    print('=' * 60)
    memory.add_message('system', 'Starting comparison report generation', 
                      metadata={'agent': 'ComparisonAgent'})
    
    comparison_agent = ComparisonAgent()
    comparison_data = comparison_agent.compare_companies(companies_data)
    
    memory.add_message('agent', 'Comparison report generated', 
                      metadata={'agent': 'ComparisonAgent'})
    
    # Generate visualizations
    print('\n' + '=' * 60)
    print('GENERATING VISUAL CHARTS')
    print('=' * 60)
    memory.add_message('system', 'Starting visualization generation', 
                      metadata={'agent': 'VisualGeneratorAgent'})
    
    visual_generator = VisualGeneratorAgent()
    visual_data = visual_generator.generate_all_charts(companies_data)
    
    memory.add_message('agent', f'Generated {len(visual_data["charts"])} charts', 
                      metadata={'agent': 'VisualGeneratorAgent', 'charts': list(visual_data['charts'].keys())})
    
    # Create and save report
    report = comparison_agent.generate_comparison_report(comparison_data)
    
    # Add chart references to report
    report += f'\n\n## Visual Comparisons\n\n'
    report += f'Charts have been generated:\n'
    for chart_type, chart_path in visual_data['charts'].items():
        report += f'- **{chart_type.title()} Chart**: `{chart_path}`\n'
    
    filename = comparison_agent.save_comparison_report(report, [d['company_name'] for d in companies_data])
    
    memory.store_analysis_result('comparison_report_filename', filename)
    memory.store_analysis_result('charts_generated', visual_data['charts'])
    
    print('\n' + '=' * 60)
    print('✅ COMPARISON COMPLETE!')
    print('=' * 60)
    print(f'\n📄 Report saved as: {filename}')
    print(f'\n📊 Charts generated:')
    for chart_type, chart_path in visual_data['charts'].items():
        print(f'   - {chart_type.title()}: {chart_path}')
    
    # Display session statistics
    stats = memory.get_session_stats()
    print(f'\n📊 Session Statistics:')
    print(f'   - Session ID: {stats["session_id"]}')
    print(f'   - Messages exchanged: {stats["message_count"]}')
    print(f'   - Companies analyzed: {stats["analysis_count"]}')
    
    # Save session to file
    try:
        os.makedirs('sessions', exist_ok=True)
        session_file = f'sessions/{memory.session_id}.json'
        memory.save_to_file(session_file)
        print(f'   - Session saved: {session_file}')
    except Exception:
        pass  # Silent fail if session save fails
    
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