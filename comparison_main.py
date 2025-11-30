import os
from dotenv import load_dotenv
from agents.researcher import ResearcherAgent
from agents.analyst import AnalystAgent
from agents.comparison_agent import ComparisonAgent
from agents.visual_generator import VisualGeneratorAgent

load_dotenv()

def analyze_single_company(company_name: str) -> dict:
    '''Analyze a single company and return all data'''
    print(f'\n{'=' * 60}')
    print(f'Analyzing: {company_name}')
    print('=' * 60)
    
    researcher = ResearcherAgent()
    analyst = AnalystAgent()
    
    company_data = {'company_name': company_name}
    
    try:
        # Research company
        print('\n?? Researching company...')
        company_data['company_research'] = researcher.research_company(company_name)
        
        # Research competitors
        print('?? Identifying competitors...')
        company_data['competitors_research'] = researcher.research_competitors(company_name)
        
        # Competitive analysis
        print('?? Analyzing competition...')
        company_data['competitive_analysis'] = analyst.analyze_competition(
            company_data['company_research'],
            company_data['competitors_research']
        )
        
        # SWOT analysis
        print('?? Generating SWOT...')
        company_data['swot_analysis'] = analyst.generate_swot(
            company_data['company_research'],
            company_data['competitive_analysis']
        )
        
        # Pricing analysis
        print('?? Analyzing pricing...')
        company_data['pricing_analysis'] = analyst.analyze_pricing(company_name, [company_name])
        
        print(f'? Analysis complete for {company_name}')
        return company_data
        
    except Exception as e:
        print(f'? Error analyzing {company_name}: {e}')
        return None

def main():
    print('=' * 60)
    print('?? MULTI-COMPANY COMPARISON TOOL')
    print('=' * 60)
    
    # Get number of companies
    while True:
        try:
            num_companies = int(input('\nHow many companies do you want to compare? (2-5): ').strip())
            if 2 <= num_companies <= 5:
                break
            else:
                print('??  Please enter a number between 2 and 5')
        except ValueError:
            print('??  Please enter a valid number')
    
    # Get company names
    companies = []
    for i in range(num_companies):
        company = input(f'Enter company #{i+1} name: ').strip()
        if company:
            companies.append(company)
        else:
            print('? Company name cannot be empty!')
            return
    
    print(f'\n?? Comparing: {', '.join(companies)}')
    print('=' * 60)
    
    # Analyze each company
    companies_data = []
    for company in companies:
        data = analyze_single_company(company)
        if data:
            companies_data.append(data)
        else:
            print(f'\n??  Skipping {company} due to errors')
    
    if len(companies_data) < 2:
        print('\n? Need at least 2 companies to compare!')
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
        report += f'- **{chart_type.title()} Chart**: {chart_path}\n'
    
    filename = comparison_agent.save_comparison_report(report, [d['company_name'] for d in companies_data])
    
    print('\n' + '=' * 60)
    print('? COMPARISON COMPLETE!')
    print('=' * 60)
    print(f'\n?? Report saved as: {filename}')
    print(f'\n?? Charts generated:')
    for chart_type, chart_path in visual_data['charts'].items():
        print(f'   - {chart_type.title()}: {chart_path}')
    print('\nYou can now open the report and chart files!')

if __name__ == '__main__':
    main()
