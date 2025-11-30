import streamlit as st
import sys
import os
from datetime import datetime
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.enums import TA_CENTER
import re
import html
from io import BytesIO

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.researcher import ResearcherAgent
from agents.analyst import AnalystAgent
from agents.report_generator import ReportGeneratorAgent
from agents.comparison_agent import ComparisonAgent
from agents.visual_generator import VisualGeneratorAgent

# Page config
st.set_page_config(
    page_title='Competitive Analysis Agent',
    page_icon='📊',
    layout='wide',
    initial_sidebar_state='expanded'
)

# Custom CSS
st.markdown('''
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        color: #1f2937;
        text-align: center;
    }
    .step-complete {
        padding: 0.75rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
    }
</style>
''', unsafe_allow_html=True)

def markdown_to_pdf(markdown_text, company_name, chart_paths=None):
    """Convert markdown report to PDF with optional charts"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#1f2937',
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor='#374151',
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=13,
        textColor='#4b5563',
        spaceAfter=10,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor='#1f2937',
        spaceAfter=12,
        leading=16
    )
    
    def clean_text(text):
        text = re.sub(r'<(?!/?[bi]>)[^>]+>', '', text)
        text = html.escape(text, quote=False)
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        return text
    
    lines = markdown_text.split('\n')
    
    for line in lines:
        line = line.strip()
        
        if not line:
            elements.append(Spacer(1, 0.15*inch))
            continue
        
        try:
            if line.startswith('# '):
                text = clean_text(line[2:].strip())
                elements.append(Paragraph(text, title_style))
                elements.append(Spacer(1, 0.3*inch))
            elif line.startswith('## '):
                text = clean_text(line[3:].strip())
                elements.append(Spacer(1, 0.2*inch))
                elements.append(Paragraph(text, heading_style))
            elif line.startswith('### '):
                text = clean_text(line[4:].strip())
                elements.append(Paragraph(text, subheading_style))
            elif line.startswith('---'):
                elements.append(Spacer(1, 0.2*inch))
            elif line.startswith('- ') or line.startswith('* '):
                text = clean_text(line[2:].strip())
                elements.append(Paragraph(f'• {text}', normal_style))
            else:
                text = clean_text(line)
                if text:
                    elements.append(Paragraph(text, normal_style))
        except Exception as e:
            continue
    
    # Add charts if provided
    if chart_paths:
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph('Visual Comparisons', heading_style))
        elements.append(Spacer(1, 0.3*inch))
        
        for chart_type, chart_path in chart_paths.items():
            try:
                elements.append(Paragraph(f'{chart_type.title()} Chart', subheading_style))
                img = RLImage(chart_path, width=6*inch, height=4*inch)
                elements.append(img)
                elements.append(Spacer(1, 0.3*inch))
            except Exception as e:
                elements.append(Paragraph(f'Chart could not be embedded: {chart_type}', normal_style))
    
    try:
        doc.build(elements)
        buffer.seek(0)
        return buffer
    except Exception as e:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        error_elements = [
            Paragraph('Error Generating PDF', title_style),
            Spacer(1, 0.5*inch),
            Paragraph('Please download the Markdown version instead.', normal_style)
        ]
        doc.build(error_elements)
        buffer.seek(0)
        return buffer

def analyze_single_company_streamlit(company_name):
    """Analyze a single company for Streamlit"""
    researcher = ResearcherAgent()
    analyst = AnalystAgent()
    
    company_data = {'company_name': company_name}
    
    with st.spinner('🔍 Researching company...'):
        company_data['company_research'] = researcher.research_company(company_name)
    
    with st.spinner('🏢 Identifying competitors...'):
        company_data['competitors_research'] = researcher.research_competitors(company_name)
    
    with st.spinner('📊 Analyzing competition...'):
        company_data['competitive_analysis'] = analyst.analyze_competition(
            company_data['company_research'],
            company_data['competitors_research']
        )
    
    with st.spinner('💡 Generating SWOT...'):
        company_data['swot_analysis'] = analyst.generate_swot(
            company_data['company_research'],
            company_data['competitive_analysis']
        )
    
    with st.spinner('💰 Analyzing pricing...'):
        company_data['pricing_analysis'] = analyst.analyze_pricing(company_name, [company_name])
    
    return company_data

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'final_report' not in st.session_state:
    st.session_state.final_report = None
if 'company_name' not in st.session_state:
    st.session_state.company_name = None
if 'comparison_complete' not in st.session_state:
    st.session_state.comparison_complete = False
if 'comparison_data' not in st.session_state:
    st.session_state.comparison_data = None
if 'visual_data' not in st.session_state:
    st.session_state.visual_data = None
if 'comparison_names' not in st.session_state:
    st.session_state.comparison_names = None

# Sidebar
with st.sidebar:
    st.markdown('### Analysis Mode')
    analysis_mode = st.radio(
        'Select Mode',
        ['Single Company', 'Multi-Company Comparison'],
        label_visibility='collapsed'
    )
    
    # Reset button
    if st.button('🔄 Reset Analysis', use_container_width=True):
        st.session_state.analysis_complete = False
        st.session_state.final_report = None
        st.session_state.company_name = None
        st.session_state.comparison_complete = False
        st.session_state.comparison_data = None
        st.session_state.visual_data = None
        st.session_state.comparison_names = None
        st.rerun()

# Header
st.markdown('<h1 class="main-header">🎯 Competitive Analysis Agent</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #6b7280;">AI-powered market intelligence and competitor research</p>', unsafe_allow_html=True)
st.markdown('---')

# Main content based on mode
if analysis_mode == 'Single Company':
    
    # Show input only if analysis not complete
    if not st.session_state.analysis_complete:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            company_name = st.text_input(
                'Company Name',
                placeholder='Enter company name (e.g., Notion, Slack, Figma)',
                label_visibility='collapsed'
            )
            
            analyze_button = st.button('🚀 Start Analysis', type='primary', use_container_width=True)
        
        if analyze_button and company_name:
            st.markdown('---')
            
            progress_bar = st.progress(0)
            
            try:
                report_generator = ReportGeneratorAgent()
                all_data = {}
                
                # Step 1-5 (same as before)
                st.info('📊 Step 1/6: Researching Company')
                progress_bar.progress(15)
                with st.spinner('Researching...'):
                    researcher = ResearcherAgent()
                    all_data['company_research'] = researcher.research_company(company_name)
                st.success('✅ Company research complete')
                
                st.info('🏢 Step 2/6: Identifying Competitors')
                progress_bar.progress(30)
                with st.spinner('Finding competitors...'):
                    all_data['competitors_research'] = researcher.research_competitors(company_name)
                st.success('✅ Competitors identified')
                
                st.info('📈 Step 3/6: Analyzing Competition')
                progress_bar.progress(50)
                with st.spinner('Analyzing...'):
                    analyst = AnalystAgent()
                    all_data['competitive_analysis'] = analyst.analyze_competition(
                        all_data['company_research'],
                        all_data['competitors_research']
                    )
                st.success('✅ Competitive analysis complete')
                
                st.info('💡 Step 4/6: Generating SWOT')
                progress_bar.progress(65)
                with st.spinner('Creating SWOT...'):
                    all_data['swot_analysis'] = analyst.generate_swot(
                        all_data['company_research'],
                        all_data['competitive_analysis']
                    )
                st.success('✅ SWOT analysis complete')
                
                st.info('💰 Step 5/6: Analyzing Pricing')
                progress_bar.progress(80)
                with st.spinner('Analyzing pricing...'):
                    all_data['pricing_analysis'] = analyst.analyze_pricing(company_name, [company_name])
                st.success('✅ Pricing analysis complete')
                
                st.info('📝 Step 6/6: Generating Report')
                progress_bar.progress(95)
                with st.spinner('Creating report...'):
                    final_report = report_generator.generate_final_report(company_name, all_data)
                
                progress_bar.progress(100)
                st.success('✅ Analysis Complete!')
                
                # Save to session state
                st.session_state.analysis_complete = True
                st.session_state.final_report = final_report
                st.session_state.company_name = company_name
                st.rerun()
                
            except Exception as e:
                st.error(f'❌ Error: {str(e)}')
                with st.expander('Error Details'):
                    st.exception(e)
        
        elif analyze_button and not company_name:
            st.warning('⚠️ Please enter a company name')
    
    # Display results if analysis is complete
    if st.session_state.analysis_complete and st.session_state.final_report:
        st.markdown('---')
        st.markdown('## 📄 Final Report')
        st.markdown(st.session_state.final_report)
        
        # Download Buttons (with key to prevent rerun)
        st.markdown('---')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_md = f'{st.session_state.company_name.replace(" ", "_")}_analysis_{timestamp}.md'
        filename_pdf = f'{st.session_state.company_name.replace(" ", "_")}_analysis_{timestamp}.pdf'
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                '📄 Download as Markdown',
                st.session_state.final_report,
                file_name=filename_md,
                mime='text/markdown',
                use_container_width=True,
                key='download_md_single'
            )
        
        with col2:
            pdf_buffer = markdown_to_pdf(st.session_state.final_report, st.session_state.company_name)
            st.download_button(
                '📕 Download as PDF',
                pdf_buffer,
                file_name=filename_pdf,
                mime='application/pdf',
                use_container_width=True,
                key='download_pdf_single'
            )

else:  # Multi-Company Comparison
    
    # Show input only if comparison not complete
    if not st.session_state.comparison_complete:
        st.markdown('### 🔄 Multi-Company Comparison')
        
        num_companies = st.number_input('Number of companies', min_value=2, max_value=5, value=2)
        
        company_names = []
        cols = st.columns(num_companies)
        
        for i in range(num_companies):
            with cols[i]:
                company = st.text_input(f'Company {i+1}', key=f'comp_{i}')
                if company:
                    company_names.append(company)
        
        compare_button = st.button('🔄 Compare Companies', type='primary', use_container_width=True)
        
        if compare_button and len(company_names) >= 2:
            st.markdown('---')
            
            progress_bar = st.progress(0)
            
            try:
                companies_data = []
                
                # Analyze each company
                for idx, company in enumerate(company_names):
                    st.info(f'Analyzing {company} ({idx+1}/{len(company_names)})')
                    progress_bar.progress(int((idx / len(company_names)) * 60))
                    
                    data = analyze_single_company_streamlit(company)
                    companies_data.append(data)
                    
                    st.success(f'✅ {company} complete')
                
                # Generate comparison
                st.info('📊 Generating comparison report...')
                progress_bar.progress(70)
                
                comparison_agent = ComparisonAgent()
                comparison_data = comparison_agent.compare_companies(companies_data)
                
                st.success('✅ Comparison complete')
                
                # Generate charts
                st.info('📈 Creating visual charts...')
                progress_bar.progress(85)
                
                visual_generator = VisualGeneratorAgent()
                visual_data = visual_generator.generate_all_charts(companies_data)
                
                progress_bar.progress(100)
                st.success('✅ All visualizations complete!')
                
                # Save to session state
                st.session_state.comparison_complete = True
                st.session_state.comparison_data = comparison_data
                st.session_state.visual_data = visual_data
                st.session_state.comparison_names = company_names
                st.rerun()
                
            except Exception as e:
                st.error(f'❌ Error: {str(e)}')
                with st.expander('Error Details'):
                    st.exception(e)
        
        elif compare_button:
            st.warning('⚠️ Please enter at least 2 companies')
    
    # Display results if comparison is complete
    if st.session_state.comparison_complete and st.session_state.comparison_data:
        st.markdown('---')
        st.markdown('## 📊 Comparison Report')
        st.markdown(st.session_state.comparison_data['comparison_analysis'])
        
        # Display Charts
        st.markdown('---')
        st.markdown('## 📈 Visual Comparisons')
        
        tab1, tab2, tab3 = st.tabs(['🎯 Radar Chart', '📊 Bar Chart', '🔥 Heatmap'])
        
        with tab1:
            radar_img = Image.open(st.session_state.visual_data['charts']['radar'])
            st.image(radar_img, use_container_width=True)
            
            with open(st.session_state.visual_data['charts']['radar'], 'rb') as f:
                st.download_button(
                    '📥 Download Radar Chart',
                    f,
                    file_name=st.session_state.visual_data['charts']['radar'],
                    mime='image/png',
                    use_container_width=True,
                    key='download_radar'
                )
        
        with tab2:
            bar_img = Image.open(st.session_state.visual_data['charts']['bar'])
            st.image(bar_img, use_container_width=True)
            
            with open(st.session_state.visual_data['charts']['bar'], 'rb') as f:
                st.download_button(
                    '📥 Download Bar Chart',
                    f,
                    file_name=st.session_state.visual_data['charts']['bar'],
                    mime='image/png',
                    use_container_width=True,
                    key='download_bar'
                )
        
        with tab3:
            heatmap_img = Image.open(st.session_state.visual_data['charts']['heatmap'])
            st.image(heatmap_img, use_container_width=True)
            
            with open(st.session_state.visual_data['charts']['heatmap'], 'rb') as f:
                st.download_button(
                    '📥 Download Heatmap',
                    f,
                    file_name=st.session_state.visual_data['charts']['heatmap'],
                    mime='image/png',
                    use_container_width=True,
                    key='download_heatmap'
                )
        
        # Download full report
        st.markdown('---')
        st.markdown('### 📥 Download Reports')
        
        report = ComparisonAgent().generate_comparison_report(st.session_state.comparison_data)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_md = f'comparison_{"_vs_".join([c.replace(" ", "_") for c in st.session_state.comparison_names])}_{timestamp}.md'
        filename_pdf = f'comparison_{"_vs_".join([c.replace(" ", "_") for c in st.session_state.comparison_names])}_{timestamp}.pdf'
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                '📄 Download as Markdown',
                report,
                file_name=filename_md,
                mime='text/markdown',
                use_container_width=True,
                key='download_md_comparison'
            )
        
        with col2:
            pdf_buffer = markdown_to_pdf(report, '_vs_'.join(st.session_state.comparison_names), st.session_state.visual_data['charts'])
            st.download_button(
                '📕 Download as PDF (with Charts)',
                pdf_buffer,
                file_name=filename_pdf,
                mime='application/pdf',
                use_container_width=True,
                key='download_pdf_comparison'
            )

# Footer
st.markdown('---')
st.markdown(
    '<p style="text-align: center; color: #9ca3af;">Built for Google-Kaggle 5-Day AI Agents Intensive Course</p>',
    unsafe_allow_html=True
)