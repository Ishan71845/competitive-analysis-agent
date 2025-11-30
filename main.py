import os
from dotenv import load_dotenv
from agents.researcher import ResearcherAgent
from agents.analyst import AnalystAgent
from agents.report_generator import ReportGeneratorAgent

load_dotenv()

def main():
    print("=" * 60)
    print("🚀 COMPETITIVE ANALYSIS AGENT")
    print("=" * 60)
    
    # Get company name from user
    company_name = input("\nEnter the company name to analyze: ").strip()
    
    if not company_name:
        print("❌ Company name cannot be empty!")
        return
    
    print(f"\n🎯 Starting competitive analysis for: {company_name}")
    print("=" * 60)
    
    # Initialize agents
    researcher = ResearcherAgent()
    analyst = AnalystAgent()
    report_generator = ReportGeneratorAgent()
    
    # Store all data
    all_data = {}
    
    try:
        # Step 1: Research the company
        print("\n" + "=" * 60)
        print("STEP 1: COMPANY RESEARCH")
        print("=" * 60)
        company_research = researcher.research_company(company_name)
        all_data['company_research'] = company_research
        
        # Step 2: Research competitors
        print("\n" + "=" * 60)
        print("STEP 2: COMPETITOR RESEARCH")
        print("=" * 60)
        competitors_research = researcher.research_competitors(company_name)
        all_data['competitors_research'] = competitors_research
        
        # Step 3: Competitive analysis
        print("\n" + "=" * 60)
        print("STEP 3: COMPETITIVE ANALYSIS")
        print("=" * 60)
        competitive_analysis = analyst.analyze_competition(company_research, competitors_research)
        all_data['competitive_analysis'] = competitive_analysis
        
        # Step 4: SWOT analysis
        print("\n" + "=" * 60)
        print("STEP 4: SWOT ANALYSIS")
        print("=" * 60)
        swot_analysis = analyst.generate_swot(company_research, competitive_analysis)
        all_data['swot_analysis'] = swot_analysis
        
        # Step 5: Pricing analysis
        print("\n" + "=" * 60)
        print("STEP 5: PRICING ANALYSIS")
        print("=" * 60)
        competitors_list = [company_name]
        pricing_analysis = analyst.analyze_pricing(company_name, competitors_list)
        all_data['pricing_analysis'] = pricing_analysis
        
        # Step 6: Generate final report
        print("\n" + "=" * 60)
        print("STEP 6: GENERATING FINAL REPORT")
        print("=" * 60)
        final_report = report_generator.generate_final_report(company_name, all_data)
        
        # Save report
        filename = report_generator.save_report(final_report, company_name)
        
        print("\n" + "=" * 60)
        print("✅ ANALYSIS COMPLETE!")
        print("=" * 60)
        print(f"\n📄 Report saved as: {filename}")
        print("\nYou can now open the report file to view the complete analysis.")
        
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()