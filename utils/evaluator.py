"""
Agent Evaluation Module

Provides evaluation metrics and quality assessment for AI agent outputs.
Implements scoring systems to measure report completeness, analysis quality,
and overall agent performance.

Author: Ishan
Course: Google-Kaggle 5-Day AI Agents Intensive Course (Capstone Project)
Date: November 2025
"""

from typing import Dict, Any, List
import re
from datetime import datetime
import json


class AgentEvaluator:
    """
    Evaluates the quality and completeness of agent outputs.
    
    Provides metrics for:
    - Report completeness
    - Content quality
    - Section presence
    - Word count analysis
    - Overall quality score
    
    Example:
        >>> evaluator = AgentEvaluator()
        >>> score = evaluator.evaluate_report(report_text)
        >>> print(f"Quality Score: {score['overall_score']}/100")
    """
    
    def __init__(self):
        """Initialize the agent evaluator."""
        self.evaluation_history: List[Dict] = []
    
    def evaluate_report(self, report: str, company_name: str = None) -> Dict[str, Any]:
        """
        Evaluate a competitive analysis report.
        
        Assesses multiple quality dimensions:
        - Completeness (all required sections present)
        - Length (adequate detail)
        - Structure (proper formatting)
        - Content quality (key elements present)
        
        Args:
            report (str): The report text to evaluate
            company_name (str, optional): Company name for context
            
        Returns:
            dict: Evaluation results with scores and metrics:
                {
                    'overall_score': float (0-100),
                    'completeness_score': float (0-100),
                    'quality_score': float (0-100),
                    'word_count': int,
                    'sections_found': list,
                    'sections_missing': list,
                    'metrics': dict,
                    'recommendations': list
                }
                
        Example:
            >>> evaluator = AgentEvaluator()
            >>> result = evaluator.evaluate_report(report_text, "Netflix")
            >>> print(f"Score: {result['overall_score']}")
            Score: 87.5
        """
        evaluation = {
            'timestamp': datetime.now().isoformat(),
            'company_name': company_name,
            'word_count': len(report.split()),
            'char_count': len(report),
            'sections_found': [],
            'sections_missing': [],
            'metrics': {},
            'recommendations': []
        }
        
        # Check for required sections
        required_sections = {
            'Executive Summary': r'(?i)executive\s+summary',
            'Company Overview': r'(?i)company\s+overview',
            'Competitive Analysis': r'(?i)competitive\s+analysis',
            'SWOT Analysis': r'(?i)swot\s+analysis',
            'Strengths': r'(?i)\*\*strengths\*\*|\bstrengths\b:',
            'Weaknesses': r'(?i)\*\*weaknesses\*\*|\bweaknesses\b:',
            'Opportunities': r'(?i)\*\*opportunities\*\*|\bopportunities\b:',
            'Threats': r'(?i)\*\*threats\*\*|\bthreats\b:',
            'Pricing': r'(?i)pricing\s+(strategy|analysis)',
            'Recommendations': r'(?i)recommendations?|strategic\s+recommendations',
            'Conclusion': r'(?i)conclusion'
        }
        
        for section_name, pattern in required_sections.items():
            if re.search(pattern, report):
                evaluation['sections_found'].append(section_name)
            else:
                evaluation['sections_missing'].append(section_name)
        
        # Calculate completeness score (percentage of sections found)
        completeness_score = (len(evaluation['sections_found']) / len(required_sections)) * 100
        evaluation['completeness_score'] = round(completeness_score, 2)
        
        # Quality metrics
        evaluation['metrics'] = {
            'has_swot': 'SWOT Analysis' in evaluation['sections_found'],
            'has_all_swot_parts': all(s in evaluation['sections_found'] 
                                     for s in ['Strengths', 'Weaknesses', 'Opportunities', 'Threats']),
            'has_recommendations': 'Recommendations' in evaluation['sections_found'],
            'has_conclusion': 'Conclusion' in evaluation['sections_found'],
            'adequate_length': evaluation['word_count'] >= 1000,
            'comprehensive_length': evaluation['word_count'] >= 3000,
            'bullet_points': report.count('- ') + report.count('* '),
            'headers': report.count('#'),
        }
        
        # Quality score based on content depth
        quality_score = 0
        
        # Word count scoring (0-30 points)
        if evaluation['word_count'] >= 5000:
            quality_score += 30
        elif evaluation['word_count'] >= 3000:
            quality_score += 25
        elif evaluation['word_count'] >= 2000:
            quality_score += 20
        elif evaluation['word_count'] >= 1000:
            quality_score += 15
        else:
            quality_score += 10
        
        # SWOT completeness (0-25 points)
        if evaluation['metrics']['has_all_swot_parts']:
            quality_score += 25
        elif evaluation['metrics']['has_swot']:
            quality_score += 15
        
        # Structure quality (0-25 points)
        if evaluation['metrics']['bullet_points'] >= 20:
            quality_score += 15
        elif evaluation['metrics']['bullet_points'] >= 10:
            quality_score += 10
        
        if evaluation['metrics']['headers'] >= 8:
            quality_score += 10
        elif evaluation['metrics']['headers'] >= 5:
            quality_score += 5
        
        # Strategic elements (0-20 points)
        if evaluation['metrics']['has_recommendations']:
            quality_score += 10
        if evaluation['metrics']['has_conclusion']:
            quality_score += 10
        
        evaluation['quality_score'] = min(quality_score, 100)
        
        # Overall score (weighted average)
        evaluation['overall_score'] = round(
            (evaluation['completeness_score'] * 0.5) + 
            (evaluation['quality_score'] * 0.5), 
            2
        )
        
        # Generate recommendations
        if not evaluation['metrics']['has_all_swot_parts']:
            evaluation['recommendations'].append("Ensure all SWOT components are present")
        
        if evaluation['word_count'] < 3000:
            evaluation['recommendations'].append("Consider adding more detailed analysis")
        
        if not evaluation['metrics']['has_recommendations']:
            evaluation['recommendations'].append("Add strategic recommendations section")
        
        if len(evaluation['sections_missing']) > 3:
            evaluation['recommendations'].append(
                f"Missing key sections: {', '.join(evaluation['sections_missing'][:3])}"
            )
        
        # Store evaluation
        self.evaluation_history.append(evaluation)
        
        return evaluation
    
    def evaluate_comparison(self, comparison_report: str, companies: List[str]) -> Dict[str, Any]:
        """
        Evaluate a multi-company comparison report.
        
        Args:
            comparison_report (str): Comparison report text
            companies (list): List of company names being compared
            
        Returns:
            dict: Evaluation results with comparison-specific metrics
            
        Example:
            >>> result = evaluator.evaluate_comparison(report, ["Amazon", "Flipkart"])
        """
        evaluation = {
            'timestamp': datetime.now().isoformat(),
            'companies': companies,
            'num_companies': len(companies),
            'word_count': len(comparison_report.split()),
            'sections_found': [],
            'metrics': {}
        }
        
        # Check for comparison sections
        comparison_sections = {
            'Market Position Comparison': r'(?i)market\s+position\s+comparison',
            'Product Comparison': r'(?i)product.*comparison',
            'Competitive Advantages': r'(?i)competitive\s+advantages',
            'Competitive Weaknesses': r'(?i)competitive\s+weaknesses',
            'Pricing Comparison': r'(?i)pricing.*comparison',
            'SWOT Comparison': r'(?i)swot.*comparison',
            'Head-to-Head': r'(?i)head-to-head',
            'Winner Analysis': r'(?i)winner\s+analysis',
            'Final Verdict': r'(?i)final\s+verdict'
        }
        
        for section_name, pattern in comparison_sections.items():
            if re.search(pattern, comparison_report):
                evaluation['sections_found'].append(section_name)
        
        # Check if all companies are mentioned
        companies_mentioned = {}
        for company in companies:
            count = comparison_report.lower().count(company.lower())
            companies_mentioned[company] = count
        
        evaluation['metrics'] = {
            'all_companies_mentioned': all(count > 0 for count in companies_mentioned.values()),
            'companies_mention_count': companies_mentioned,
            'balanced_coverage': max(companies_mentioned.values()) / min(companies_mentioned.values()) < 2 
                                 if min(companies_mentioned.values()) > 0 else False,
            'adequate_length': evaluation['word_count'] >= 2000,
            'comprehensive': len(evaluation['sections_found']) >= 7
        }
        
        # Calculate score
        completeness = (len(evaluation['sections_found']) / len(comparison_sections)) * 100
        
        quality_score = 0
        if evaluation['metrics']['all_companies_mentioned']:
            quality_score += 30
        if evaluation['metrics']['balanced_coverage']:
            quality_score += 20
        if evaluation['metrics']['adequate_length']:
            quality_score += 25
        if evaluation['metrics']['comprehensive']:
            quality_score += 25
        
        evaluation['completeness_score'] = round(completeness, 2)
        evaluation['quality_score'] = quality_score
        evaluation['overall_score'] = round((completeness + quality_score) / 2, 2)
        
        return evaluation
    
    def evaluate_charts(self, chart_paths: Dict[str, str]) -> Dict[str, Any]:
        """
        Evaluate generated visualization charts.
        
        Args:
            chart_paths (dict): Dictionary of chart types to file paths
            
        Returns:
            dict: Evaluation of chart generation
            
        Example:
            >>> charts = {'radar': 'chart_radar.png', 'bar': 'chart_bar.png'}
            >>> result = evaluator.evaluate_charts(charts)
        """
        import os
        
        evaluation = {
            'timestamp': datetime.now().isoformat(),
            'charts_generated': len(chart_paths),
            'expected_charts': 3,
            'charts': {},
            'all_charts_present': False
        }
        
        expected_types = ['radar', 'bar', 'heatmap']
        
        for chart_type, path in chart_paths.items():
            chart_eval = {
                'type': chart_type,
                'path': path,
                'exists': os.path.exists(path) if path else False,
                'size': os.path.getsize(path) if path and os.path.exists(path) else 0
            }
            evaluation['charts'][chart_type] = chart_eval
        
        evaluation['all_charts_present'] = all(
            chart_type in chart_paths for chart_type in expected_types
        )
        
        evaluation['score'] = (len(chart_paths) / 3) * 100
        
        return evaluation
    
    def get_evaluation_summary(self) -> Dict[str, Any]:
        """
        Get summary of all evaluations.
        
        Returns:
            dict: Summary statistics across all evaluations
            
        Example:
            >>> summary = evaluator.get_evaluation_summary()
            >>> print(f"Average score: {summary['average_score']}")
        """
        if not self.evaluation_history:
            return {'message': 'No evaluations yet'}
        
        scores = [e['overall_score'] for e in self.evaluation_history]
        
        return {
            'total_evaluations': len(self.evaluation_history),
            'average_score': round(sum(scores) / len(scores), 2),
            'highest_score': max(scores),
            'lowest_score': min(scores),
            'evaluations': self.evaluation_history
        }
    
    def save_evaluation(self, filepath: str = None):
        """
        Save evaluation results to JSON file.
        
        Args:
            filepath (str, optional): Output file path
            
        Example:
            >>> evaluator.save_evaluation("evaluations/session_eval.json")
        """
        if filepath is None:
            from pathlib import Path
            eval_dir = Path("evaluations")
            eval_dir.mkdir(exist_ok=True)
            filepath = eval_dir / f"evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        summary = self.get_evaluation_summary()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        return filepath


def quick_evaluate(report: str, company_name: str = None) -> float:
    """
    Quick evaluation function returning just the overall score.
    
    Args:
        report (str): Report text to evaluate
        company_name (str, optional): Company name
        
    Returns:
        float: Overall quality score (0-100)
        
    Example:
        >>> score = quick_evaluate(report_text, "Netflix")
        >>> print(f"Score: {score}/100")
    """
    evaluator = AgentEvaluator()
    result = evaluator.evaluate_report(report, company_name)
    return result['overall_score']