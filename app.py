import streamlit as st
import sys
import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import re
import html

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.researcher import ResearcherAgent
from agents.analyst import AnalystAgent
from agents.report_generator import ReportGeneratorAgent

# Page config
st.set_page_config(
    page_title="Competitive Analysis Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Professional & Minimal
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #6b7280;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    .stProgress > div > div > div > div {
        background-color: #3b82f6;
    }
    .step-complete {
        padding: 0.75rem 1rem;
        border-radius: 0.375rem;
        background-color: #f0fdf4;
        border-left: 4px solid #10b981;
        color: #065f46;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    .step-header {
        color: #1f2937;
        font-size: 1.1rem;
        font-weight: 500;
        margin: 1rem 0;
    }
    .history-item {
        padding: 0.75rem;
        border-radius: 0.375rem;
        background-color: #f9fafb;
        border: 1px solid #e5e7eb;
        margin-bottom: 0.5rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    .history-item:hover {
        background-color: #f3f4f6;
        border-color: #d1d5db;
    }
    .sidebar-section {
        margin-bottom: 1.5rem;
    }
    .sidebar-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)

# History functions
HISTORY_FILE = "session_history.json"

def load_history():
    """Load research history from JSON file"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_to_history(company_name, timestamp):
    """Save research to history"""
    history = load_history()
    history.insert(0, {
        "company": company_name,
        "timestamp": timestamp,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    # Keep only last 10 items
    history = history[:10]
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def markdown_to_pdf(markdown_text, company_name):
    """Convert markdown report to PDF with better error handling"""
    from io import BytesIO
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for PDF elements
    elements = []
    
    # Define styles
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
        """Clean and escape text for PDF"""
        # Remove any existing HTML tags except the ones we want
        text = re.sub(r'<(?!/?[bi]>)[^>]+>', '', text)
        # Escape special characters
        text = html.escape(text, quote=False)
        # Convert markdown bold to HTML
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        # Convert markdown italic to HTML
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        return text
    
    # Parse markdown
    lines = markdown_text.split('\n')
    
    for line in lines:
        line = line.strip()
        
        if not line:
            elements.append(Spacer(1, 0.15*inch))
            continue
        
        try:
            # Title (# )
            if line.startswith('# '):
                text = clean_text(line[2:].strip())
                elements.append(Paragraph(text, title_style))
                elements.append(Spacer(1, 0.3*inch))
            
            # Heading (## )
            elif line.startswith('## '):
                text = clean_text(line[3:].strip())
                elements.append(Spacer(1, 0.2*inch))
                elements.append(Paragraph(text, heading_style))
            
            # Subheading (### )
            elif line.startswith('### '):
                text = clean_text(line[4:].strip())
                elements.append(Paragraph(text, subheading_style))
            
            # Horizontal line
            elif line.startswith('---'):
                elements.append(Spacer(1, 0.2*inch))
            
            # List items (- or *)
            elif line.startswith('- ') or line.startswith('* '):
                text = clean_text(line[2:].strip())
                elements.append(Paragraph(f"• {text}", normal_style))
            
            # Regular text
            else:
                text = clean_text(line)
                if text:  # Only add non-empty text
                    elements.append(Paragraph(text, normal_style))
        
        except Exception as e:
            # If a line fails, skip it and continue
            print(f"Skipping line due to error: {e}")
            continue
    
    # Build PDF
    try:
        doc.build(elements)
        buffer.seek(0)
        return buffer
    except Exception as e:
        # If PDF generation fails completely, create a simple error PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        error_elements = [
            Paragraph("Error Generating PDF", title_style),
            Spacer(1, 0.5*inch),
            Paragraph("The report was generated successfully but could not be converted to PDF format.", normal_style),
            Paragraph("Please download the Markdown version instead.", normal_style)
        ]
        doc.build(error_elements)
        buffer.seek(0)
        return buffer

# Sidebar - Research History
with st.sidebar:
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">Recent Research</div>', unsafe_allow_html=True)
    
    history = load_history()
    
    if history:
        for item in history:
            with st.container():
                st.markdown(f"""
                <div class="history-item">
                    <div style="font-weight: 500; color: #1f2937;">{item['company']}</div>
                    <div style="font-size: 0.8rem; color: #6b7280; margin-top: 0.25rem;">{item['date']}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown('<p style="color: #9ca3af; font-size: 0.9rem;">No recent research yet</p>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Clear history button
    if history and st.button("Clear History", use_container_width=True):
        with open(HISTORY_FILE, 'w') as f:
            json.dump([], f)
        st.rerun()

# Header
st.markdown('<h1 class="main-header">Competitive Analysis Agent</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-powered market intelligence and competitor research</p>', unsafe_allow_html=True)

# Input section
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    company_name = st.text_input(
        "",
        placeholder="Enter company name (e.g., Notion, Slack, Figma)",
        label_visibility="collapsed"
    )
    
    analyze_button = st.button("Start Analysis", type="primary", use_container_width=True)

# Analysis section
if analyze_button and company_name:
    st.markdown("---")
    
    # Initialize progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Initialize agents
        researcher = ResearcherAgent()
        analyst = AnalystAgent()
        report_generator = ReportGeneratorAgent()
        
        all_data = {}
        
        # Step 1: Company Research
        status_text.markdown('<div class="step-header">Step 1/6: Researching Company</div>', unsafe_allow_html=True)
        progress_bar.progress(10)
        
        with st.spinner(f"Researching {company_name}..."):
            company_research = researcher.research_company(company_name)
            all_data['company_research'] = company_research
        
        progress_bar.progress(20)
        st.markdown('<div class="step-complete">✓ Company research complete</div>', unsafe_allow_html=True)
        
        with st.expander("View Company Research Summary"):
            st.markdown(company_research.get('summary', 'No summary available'))
        
        # Step 2: Competitor Research
        status_text.markdown('<div class="step-header">Step 2/6: Identifying Competitors</div>', unsafe_allow_html=True)
        progress_bar.progress(30)
        
        with st.spinner("Finding competitors..."):
            competitors_research = researcher.research_competitors(company_name)
            all_data['competitors_research'] = competitors_research
        
        progress_bar.progress(40)
        st.markdown('<div class="step-complete">✓ Competitors identified</div>', unsafe_allow_html=True)
        
        with st.expander("View Identified Competitors"):
            st.markdown(competitors_research.get('identified_competitors', 'No competitors found'))
        
        # Step 3: Competitive Analysis
        status_text.markdown('<div class="step-header">Step 3/6: Analyzing Competition</div>', unsafe_allow_html=True)
        progress_bar.progress(50)
        
        with st.spinner("Performing competitive analysis..."):
            competitive_analysis = analyst.analyze_competition(company_research, competitors_research)
            all_data['competitive_analysis'] = competitive_analysis
        
        progress_bar.progress(60)
        st.markdown('<div class="step-complete">✓ Competitive analysis complete</div>', unsafe_allow_html=True)
        
        with st.expander("View Competitive Analysis"):
            st.markdown(competitive_analysis.get('competitive_analysis', 'No analysis available'))
        
        # Step 4: SWOT Analysis
        status_text.markdown('<div class="step-header">Step 4/6: Generating SWOT Analysis</div>', unsafe_allow_html=True)
        progress_bar.progress(70)
        
        with st.spinner("Creating SWOT analysis..."):
            swot_analysis = analyst.generate_swot(company_research, competitive_analysis)
            all_data['swot_analysis'] = swot_analysis
        
        progress_bar.progress(80)
        st.markdown('<div class="step-complete">✓ SWOT analysis complete</div>', unsafe_allow_html=True)
        
        with st.expander("View SWOT Analysis"):
            st.markdown(swot_analysis.get('swot_analysis', 'No SWOT available'))
        
        # Step 5: Pricing Analysis
        status_text.markdown('<div class="step-header">Step 5/6: Analyzing Pricing Strategy</div>', unsafe_allow_html=True)
        progress_bar.progress(85)
        
        with st.spinner("Analyzing pricing..."):
            pricing_analysis = analyst.analyze_pricing(company_name, [company_name])
            all_data['pricing_analysis'] = pricing_analysis
        
        progress_bar.progress(90)
        st.markdown('<div class="step-complete">✓ Pricing analysis complete</div>', unsafe_allow_html=True)
        
        with st.expander("View Pricing Analysis"):
            st.markdown(pricing_analysis.get('analysis', 'No pricing analysis available'))
        
        # Step 6: Generate Report
        status_text.markdown('<div class="step-header">Step 6/6: Generating Final Report</div>', unsafe_allow_html=True)
        progress_bar.progress(95)
        
        with st.spinner("Creating comprehensive report..."):
            final_report = report_generator.generate_final_report(company_name, all_data)
        
        progress_bar.progress(100)
        status_text.markdown('<div class="step-complete">✓ Analysis complete</div>', unsafe_allow_html=True)
        
        # Save to history
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        save_to_history(company_name, timestamp)
        
        # Display final report
        st.markdown("---")
        st.markdown("## Final Report")
        
        st.markdown(final_report)
        
        # Download buttons
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            # Markdown download
            filename_md = f"{company_name.replace(' ', '_')}_analysis_{timestamp}.md"
            st.download_button(
                label="Download as Markdown",
                data=final_report,
                file_name=filename_md,
                mime="text/markdown",
                use_container_width=True
            )
        
        with col2:
            # PDF download
            pdf_buffer = markdown_to_pdf(final_report, company_name)
            filename_pdf = f"{company_name.replace(' ', '_')}_analysis_{timestamp}.pdf"
            st.download_button(
                label="Download as PDF",
                data=pdf_buffer,
                file_name=filename_pdf,
                mime="application/pdf",
                use_container_width=True
            )
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        with st.expander("View Error Details"):
            st.exception(e)

elif analyze_button and not company_name:
    st.warning("Please enter a company name to analyze.")

# Footer
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #9ca3af; font-size: 0.85rem;">Built for Google-Kaggle 5-Day AI Agents Intensive Course</p>',
    unsafe_allow_html=True
)