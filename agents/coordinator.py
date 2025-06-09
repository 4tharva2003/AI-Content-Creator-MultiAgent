"""
Coordinator Agent for AI Multi-Agent Content Creation Pipeline

The Coordinator Agent is responsible for:
- Orchestrating the entire content creation workflow
- Managing task delegation between agents
- Ensuring quality standards are met
- Coordinating agent interactions and data flow
"""

from typing import Dict, Any, List, Optional
from crewai import Agent, Task, Crew
from utils.llm_config import configure_llm

class CoordinatorAgent:
    """
    Coordinator Agent that orchestrates the content creation pipeline
    """
    
    def __init__(self):
        self.llm = configure_llm('coordinator')
        self.agent = self._create_agent()
        
    def _create_agent(self) -> Agent:
        """Create the coordinator agent with specific configuration"""
        return Agent(
            role="Content Creation Coordinator",
            goal="Orchestrate the content creation pipeline to produce high-quality, SEO-optimized content",
            backstory="""You are an experienced content project manager with expertise in coordinating 
            content creation workflows. You understand how to break down content requirements into 
            actionable tasks for specialized team members, ensure quality standards, and manage 
            the flow of information between different specialists. You have a keen eye for detail 
            and can identify when content meets publication standards.""",
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )
    
    def create_content_plan(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a comprehensive content creation plan based on requirements
        
        Args:
            requirements: Dictionary containing content requirements
            
        Returns:
            Detailed content creation plan
        """
        plan = {
            'topic': requirements.get('topic', ''),
            'target_audience': requirements.get('target_audience', 'General audience'),
            'word_count': requirements.get('word_count', 1000),
            'tone': requirements.get('tone', 'Professional'),
            'seo_keywords': requirements.get('seo_keywords', []),
            'content_type': requirements.get('content_type', 'Blog post'),
            'tasks': self._generate_task_sequence(requirements),
            'quality_criteria': self._define_quality_criteria(requirements),
            'timeline': self._estimate_timeline(requirements)
        }
        
        return plan
    
    def _generate_task_sequence(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate the sequence of tasks for content creation"""
        tasks = [
            {
                'name': 'research',
                'agent': 'researcher',
                'description': f"Research comprehensive information about '{requirements.get('topic', '')}'",
                'deliverables': ['research_summary', 'key_facts', 'source_references'],
                'estimated_time': '15 minutes'
            },
            {
                'name': 'content_writing',
                'agent': 'writer',
                'description': f"Write a {requirements.get('word_count', 1000)}-word {requirements.get('content_type', 'blog post')}",
                'deliverables': ['first_draft'],
                'dependencies': ['research'],
                'estimated_time': '20 minutes'
            },
            {
                'name': 'editing',
                'agent': 'editor',
                'description': "Review and improve content for clarity, flow, and grammar",
                'deliverables': ['edited_content', 'improvement_notes'],
                'dependencies': ['content_writing'],
                'estimated_time': '10 minutes'
            },
            {
                'name': 'seo_optimization',
                'agent': 'seo',
                'description': f"Optimize content for SEO with keywords: {', '.join(requirements.get('seo_keywords', []))}",
                'deliverables': ['seo_optimized_content', 'meta_tags', 'seo_report'],
                'dependencies': ['editing'],
                'estimated_time': '10 minutes'
            },
            {
                'name': 'final_review',
                'agent': 'coordinator',
                'description': "Conduct final quality assurance and approval",
                'deliverables': ['final_content', 'quality_report'],
                'dependencies': ['seo_optimization'],
                'estimated_time': '5 minutes'
            }
        ]
        
        return tasks
    
    def _define_quality_criteria(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Define quality criteria for the content"""
        return {
            'minimum_word_count': requirements.get('word_count', 1000) * 0.9,  # 90% of target
            'maximum_word_count': requirements.get('word_count', 1000) * 1.1,  # 110% of target
            'required_keywords': requirements.get('seo_keywords', []),
            'readability_score': 60,  # Minimum readability score
            'structure_requirements': {
                'has_introduction': True,
                'has_conclusion': True,
                'has_headings': True,
                'max_paragraph_length': 150
            },
            'seo_requirements': {
                'keyword_density': {'min': 0.5, 'max': 3.0},  # Percentage
                'meta_title_length': {'min': 30, 'max': 60},
                'meta_description_length': {'min': 120, 'max': 160}
            }
        }
    
    def _estimate_timeline(self, requirements: Dict[str, Any]) -> Dict[str, str]:
        """Estimate timeline for content creation"""
        word_count = requirements.get('word_count', 1000)
        complexity_multiplier = 1.0
        
        # Adjust for complexity
        if word_count > 2000:
            complexity_multiplier = 1.5
        elif word_count > 1500:
            complexity_multiplier = 1.2
        
        base_time = 60  # minutes
        estimated_time = int(base_time * complexity_multiplier)
        
        return {
            'estimated_duration': f"{estimated_time} minutes",
            'research_phase': "15 minutes",
            'writing_phase': "20 minutes", 
            'editing_phase': "10 minutes",
            'seo_phase': "10 minutes",
            'review_phase': "5 minutes"
        }
    
    def validate_content_quality(self, content: str, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that content meets the defined quality criteria
        
        Args:
            content: The content to validate
            plan: The content creation plan with quality criteria
            
        Returns:
            Validation results with pass/fail status and feedback
        """
        criteria = plan.get('quality_criteria', {})
        validation_results = {
            'overall_score': 0,
            'passed': False,
            'checks': {},
            'feedback': [],
            'improvements_needed': []
        }
        
        # Word count check
        word_count = len(content.split())
        min_words = criteria.get('minimum_word_count', 900)
        max_words = criteria.get('maximum_word_count', 1100)
        
        validation_results['checks']['word_count'] = {
            'current': word_count,
            'target_range': f"{min_words}-{max_words}",
            'passed': min_words <= word_count <= max_words
        }
        
        if not validation_results['checks']['word_count']['passed']:
            if word_count < min_words:
                validation_results['improvements_needed'].append(f"Content is too short ({word_count} words). Add {min_words - word_count} more words.")
            else:
                validation_results['improvements_needed'].append(f"Content is too long ({word_count} words). Remove {word_count - max_words} words.")
        
        # Structure checks
        structure_reqs = criteria.get('structure_requirements', {})
        
        # Check for introduction and conclusion
        has_intro = any(keyword in content.lower()[:200] for keyword in ['introduction', 'overview', 'begin', 'start'])
        has_conclusion = any(keyword in content.lower()[-200:] for keyword in ['conclusion', 'summary', 'final', 'end'])
        
        validation_results['checks']['structure'] = {
            'has_introduction': has_intro,
            'has_conclusion': has_conclusion,
            'has_headings': '#' in content or any(line.isupper() for line in content.split('\n')),
        }
        
        # Calculate overall score
        passed_checks = sum(1 for check in validation_results['checks'].values() 
                          if isinstance(check, dict) and check.get('passed', True))
        total_checks = len(validation_results['checks'])
        
        if total_checks > 0:
            validation_results['overall_score'] = (passed_checks / total_checks) * 100
            validation_results['passed'] = validation_results['overall_score'] >= 80
        
        # Generate feedback
        if validation_results['passed']:
            validation_results['feedback'].append("Content meets quality standards and is ready for publication.")
        else:
            validation_results['feedback'].append("Content needs improvements before publication.")
            validation_results['feedback'].extend(validation_results['improvements_needed'])
        
        return validation_results
    
    def create_final_report(self, content: str, plan: Dict[str, Any], agent_outputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a comprehensive report of the content creation process
        
        Args:
            content: Final content
            plan: Content creation plan
            agent_outputs: Outputs from all agents
            
        Returns:
            Comprehensive final report
        """
        validation = self.validate_content_quality(content, plan)
        
        report = {
            'content_metadata': {
                'topic': plan.get('topic'),
                'word_count': len(content.split()),
                'target_audience': plan.get('target_audience'),
                'content_type': plan.get('content_type'),
                'creation_date': None  # Would be set to current timestamp
            },
            'quality_assessment': validation,
            'agent_contributions': {
                'research': agent_outputs.get('research', {}),
                'writing': agent_outputs.get('writing', {}),
                'editing': agent_outputs.get('editing', {}),
                'seo': agent_outputs.get('seo', {})
            },
            'seo_summary': agent_outputs.get('seo', {}).get('seo_score', 0),
            'recommendations': self._generate_final_recommendations(validation, agent_outputs),
            'next_steps': self._suggest_next_steps(validation)
        }
        
        return report
    
    def _generate_final_recommendations(self, validation: Dict[str, Any], agent_outputs: Dict[str, Any]) -> List[str]:
        """Generate final recommendations based on all agent outputs"""
        recommendations = []
        
        # Add validation-based recommendations
        if validation.get('improvements_needed'):
            recommendations.extend(validation['improvements_needed'])
        
        # Add SEO recommendations
        seo_output = agent_outputs.get('seo', {})
        if 'recommendations' in seo_output:
            recommendations.extend(seo_output['recommendations'])
        
        # Add general recommendations
        if validation.get('overall_score', 0) >= 90:
            recommendations.append("Excellent content quality! Consider this for featured placement.")
        elif validation.get('overall_score', 0) >= 80:
            recommendations.append("Good content quality. Ready for publication with minor improvements.")
        else:
            recommendations.append("Content needs significant improvements before publication.")
        
        return recommendations
    
    def _suggest_next_steps(self, validation: Dict[str, Any]) -> List[str]:
        """Suggest next steps based on validation results"""
        next_steps = []
        
        if validation.get('passed', False):
            next_steps.extend([
                "Content is ready for publication",
                "Schedule social media promotion",
                "Consider internal linking opportunities",
                "Monitor performance metrics after publication"
            ])
        else:
            next_steps.extend([
                "Address quality issues identified in validation",
                "Re-run content through editing agent if needed",
                "Consider additional research if content gaps exist",
                "Re-validate content after improvements"
            ])
        
        return next_steps 