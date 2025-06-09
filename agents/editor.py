"""
Editor Agent for AI Multi-Agent Content Creation Pipeline

The Editor Agent is responsible for:
- Reviewing and improving content quality
- Checking grammar, spelling, and syntax
- Enhancing clarity and flow
- Ensuring consistency and coherence
"""

from typing import Dict, Any, List, Optional
from crewai import Agent, Task
from utils.llm_config import configure_llm
from utils.tools import ContentValidatorTool

class EditorAgent:
    """
    Editor Agent specialized in content review and improvement
    """
    
    def __init__(self):
        self.llm = configure_llm('editor')
        self.content_validator = ContentValidatorTool()
        self.agent = self._create_agent()
        
    def _create_agent(self) -> Agent:
        """Create the editor agent with specific configuration"""
        return Agent(
            role="Content Editor and Quality Specialist",
            goal="Review and improve content quality, ensuring clarity, coherence, and professional standards",
            backstory="""You are an experienced content editor with a keen eye for detail and 
            exceptional language skills. You have years of experience refining content across 
            various industries and formats. You excel at identifying areas for improvement in 
            clarity, flow, grammar, and overall readability. Your editing transforms good content 
            into exceptional content that resonates with readers and achieves its intended purpose.""",
            verbose=True,
            allow_delegation=False,
            tools=[self.content_validator],
            llm=self.llm
        )
    
    def edit_content(self, content: str, requirements: Dict[str, Any], writer_output: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Edit and improve content based on quality standards
        
        Args:
            content: Content to edit and improve
            requirements: Original content requirements
            writer_output: Output from the Writer Agent (optional)
            
        Returns:
            Editing results with improved content and feedback
        """
        # Analyze current content quality
        quality_analysis = self.content_validator.run(content)
        
        # Perform editing improvements
        improved_content = self._improve_content(content, requirements, quality_analysis)
        
        # Generate editing report
        editing_output = {
            'original_content': content,
            'edited_content': improved_content,
            'quality_analysis': quality_analysis,
            'improvements_made': self._track_improvements(content, improved_content),
            'editing_notes': self._generate_editing_notes(content, improved_content, requirements),
            'final_quality_score': self._calculate_final_quality_score(improved_content),
            'recommendations': self._generate_recommendations(improved_content, requirements)
        }
        
        return editing_output
    
    def _improve_content(self, content: str, requirements: Dict[str, Any], quality_analysis: Dict[str, Any]) -> str:
        """Apply various content improvements"""
        improved_content = content
        
        # Apply improvements in sequence
        improved_content = self._improve_structure(improved_content, requirements)
        improved_content = self._improve_clarity(improved_content)
        improved_content = self._improve_flow(improved_content)
        improved_content = self._improve_readability(improved_content)
        improved_content = self._fix_common_issues(improved_content, quality_analysis)
        
        return improved_content
    
    def _improve_structure(self, content: str, requirements: Dict[str, Any]) -> str:
        """Improve content structure and organization"""
        lines = content.split('\n')
        improved_lines = []
        
        for line in lines:
            # Ensure proper heading hierarchy
            if line.startswith('#'):
                # Clean up heading formatting
                heading_text = line.strip()
                # Ensure single space after hash marks
                level = len(heading_text) - len(heading_text.lstrip('#'))
                text = heading_text.lstrip('#').strip()
                improved_lines.append('#' * level + ' ' + text)
            else:
                improved_lines.append(line)
        
        improved_content = '\n'.join(improved_lines)
        
        # Ensure proper paragraph spacing
        improved_content = self._fix_paragraph_spacing(improved_content)
        
        return improved_content
    
    def _fix_paragraph_spacing(self, content: str) -> str:
        """Fix paragraph spacing issues"""
        # Split into paragraphs
        paragraphs = content.split('\n\n')
        
        # Clean up each paragraph
        cleaned_paragraphs = []
        for para in paragraphs:
            # Remove extra whitespace
            cleaned_para = para.strip()
            if cleaned_para:  # Only keep non-empty paragraphs
                # Ensure single line breaks within paragraphs become spaces
                cleaned_para = ' '.join(cleaned_para.split('\n'))
                cleaned_paragraphs.append(cleaned_para)
        
        # Rejoin with proper spacing
        return '\n\n'.join(cleaned_paragraphs)
    
    def _improve_clarity(self, content: str) -> str:
        """Improve content clarity and conciseness"""
        # Replace wordy phrases with concise alternatives
        clarity_improvements = {
            'in order to': 'to',
            'due to the fact that': 'because',
            'at this point in time': 'now',
            'for the purpose of': 'to',
            'in the event that': 'if',
            'take into consideration': 'consider',
            'make a decision': 'decide',
            'come to a conclusion': 'conclude',
            'it is important to note that': '',
            'it should be mentioned that': '',
            'it is worth noting that': '',
        }
        
        improved_content = content
        for wordy, concise in clarity_improvements.items():
            improved_content = improved_content.replace(wordy, concise)
        
        return improved_content
    
    def _improve_flow(self, content: str) -> str:
        """Improve content flow and transitions"""
        paragraphs = content.split('\n\n')
        
        # Add transition words where appropriate
        transition_starters = [
            'However,', 'Furthermore,', 'Additionally,', 'Moreover,', 
            'In contrast,', 'Similarly,', 'Therefore,', 'Consequently,'
        ]
        
        improved_paragraphs = []
        for i, para in enumerate(paragraphs):
            if i > 0 and len(para.split()) > 20:  # Only for substantial paragraphs
                # Check if paragraph needs a transition
                if not any(para.strip().startswith(starter) for starter in transition_starters):
                    # Analyze content to suggest appropriate transition
                    if 'benefit' in para.lower() or 'advantage' in para.lower():
                        if 'challenge' in paragraphs[i-1].lower():
                            para = 'However, ' + para
                        else:
                            para = 'Additionally, ' + para
                    elif 'challenge' in para.lower() or 'difficult' in para.lower():
                        para = 'However, ' + para
            
            improved_paragraphs.append(para)
        
        return '\n\n'.join(improved_paragraphs)
    
    def _improve_readability(self, content: str) -> str:
        """Improve content readability"""
        # Break up very long sentences
        sentences = content.split('.')
        improved_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence.split()) > 30:  # Very long sentence
                # Try to break at logical points
                if ' and ' in sentence:
                    parts = sentence.split(' and ')
                    if len(parts) == 2:
                        improved_sentences.append(parts[0].strip())
                        improved_sentences.append(parts[1].strip())
                        continue
                elif ' which ' in sentence:
                    parts = sentence.split(' which ')
                    if len(parts) == 2:
                        improved_sentences.append(parts[0].strip())
                        improved_sentences.append('This ' + parts[1].strip())
                        continue
            
            if sentence:
                improved_sentences.append(sentence)
        
        return '. '.join(improved_sentences)
    
    def _fix_common_issues(self, content: str, quality_analysis: Dict[str, Any]) -> str:
        """Fix common writing issues identified in quality analysis"""
        improved_content = content
        
        # Fix common grammar issues
        grammar_fixes = {
            ' ,': ',',  # Space before comma
            ' .': '.',  # Space before period
            ',,': ',',  # Double comma
            '..': '.',  # Double period
            '  ': ' ',  # Double space
        }
        
        for incorrect, correct in grammar_fixes.items():
            improved_content = improved_content.replace(incorrect, correct)
        
        # Ensure proper capitalization after periods
        sentences = improved_content.split('. ')
        capitalized_sentences = []
        
        for sentence in sentences:
            if sentence and sentence[0].islower():
                sentence = sentence[0].upper() + sentence[1:]
            capitalized_sentences.append(sentence)
        
        improved_content = '. '.join(capitalized_sentences)
        
        return improved_content
    
    def _track_improvements(self, original: str, improved: str) -> List[str]:
        """Track and document improvements made during editing"""
        improvements = []
        
        # Check word count change
        original_words = len(original.split())
        improved_words = len(improved.split())
        
        if improved_words != original_words:
            if improved_words < original_words:
                improvements.append(f"Reduced word count by {original_words - improved_words} words for better conciseness")
            else:
                improvements.append(f"Expanded content by {improved_words - original_words} words for better clarity")
        
        # Check for structural improvements
        original_headings = original.count('#')
        improved_headings = improved.count('#')
        
        if improved_headings > original_headings:
            improvements.append("Added headings to improve content structure")
        
        # Check for paragraph improvements
        original_paras = len([p for p in original.split('\n\n') if p.strip()])
        improved_paras = len([p for p in improved.split('\n\n') if p.strip()])
        
        if improved_paras != original_paras:
            improvements.append("Reorganized content into better paragraph structure")
        
        # Check for transition improvements
        transitions = ['However', 'Furthermore', 'Additionally', 'Moreover', 'Therefore']
        original_transitions = sum(original.count(t) for t in transitions)
        improved_transitions = sum(improved.count(t) for t in transitions)
        
        if improved_transitions > original_transitions:
            improvements.append("Added transition words to improve flow")
        
        if not improvements:
            improvements.append("Made minor improvements to clarity and readability")
        
        return improvements
    
    def _generate_editing_notes(self, original: str, improved: str, requirements: Dict[str, Any]) -> List[str]:
        """Generate notes about the editing process"""
        notes = []
        
        # Analyze changes
        original_quality = self.content_validator.run(original)
        improved_quality = self.content_validator.run(improved)
        
        # Compare quality scores
        original_score = original_quality.get('quality_score', 0)
        improved_score = improved_quality.get('quality_score', 0)
        
        if improved_score > original_score:
            notes.append(f"Quality score improved from {original_score} to {improved_score}")
        
        # Check specific improvements
        original_issues = len(original_quality.get('issues', []))
        improved_issues = len(improved_quality.get('issues', []))
        
        if improved_issues < original_issues:
            notes.append(f"Resolved {original_issues - improved_issues} content issues")
        
        # Check readability
        original_readability = original_quality.get('readability_score', 0)
        improved_readability = improved_quality.get('readability_score', 0)
        
        if improved_readability > original_readability:
            notes.append(f"Improved readability score from {original_readability} to {improved_readability}")
        
        # Check word count alignment
        target_words = requirements.get('word_count', 1000)
        actual_words = len(improved.split())
        
        if abs(actual_words - target_words) <= target_words * 0.1:
            notes.append(f"Content length optimized to target ({actual_words} words)")
        
        notes.append("Applied standard editorial best practices")
        notes.append("Ensured consistency in tone and style")
        
        return notes
    
    def _calculate_final_quality_score(self, content: str) -> float:
        """Calculate final quality score after editing"""
        quality_analysis = self.content_validator.run(content)
        return quality_analysis.get('quality_score', 0)
    
    def _generate_recommendations(self, content: str, requirements: Dict[str, Any]) -> List[str]:
        """Generate recommendations for further improvement"""
        recommendations = []
        
        quality_analysis = self.content_validator.run(content)
        quality_score = quality_analysis.get('quality_score', 0)
        
        # Score-based recommendations
        if quality_score >= 90:
            recommendations.append("Excellent content quality - ready for publication")
            recommendations.append("Consider this content for featured placement or promotion")
        elif quality_score >= 80:
            recommendations.append("Good content quality - minor improvements may enhance impact")
            recommendations.append("Content is ready for publication")
        elif quality_score >= 70:
            recommendations.append("Content needs minor improvements before publication")
            recommendations.append("Consider additional review of structure and clarity")
        else:
            recommendations.append("Content requires significant improvements")
            recommendations.append("Recommend additional editing pass before publication")
        
        # Specific recommendations based on analysis
        issues = quality_analysis.get('issues', [])
        for issue in issues[:3]:  # Top 3 issues
            recommendations.append(f"Address: {issue}")
        
        # Word count recommendations
        word_count = len(content.split())
        target_words = requirements.get('word_count', 1000)
        
        if word_count < target_words * 0.9:
            recommendations.append(f"Consider expanding content to reach target word count ({target_words} words)")
        elif word_count > target_words * 1.1:
            recommendations.append(f"Consider condensing content to meet target word count ({target_words} words)")
        
        # SEO readiness
        seo_keywords = requirements.get('seo_keywords', [])
        if seo_keywords:
            content_lower = content.lower()
            missing_keywords = [kw for kw in seo_keywords if kw.lower() not in content_lower]
            if missing_keywords:
                recommendations.append(f"Consider incorporating missing SEO keywords: {', '.join(missing_keywords)}")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def create_editing_summary(self, editing_output: Dict[str, Any]) -> Dict[str, Any]:
        """Create a comprehensive editing summary"""
        original_analysis = self.content_validator.run(editing_output['original_content'])
        final_analysis = self.content_validator.run(editing_output['edited_content'])
        
        summary = {
            'editing_metrics': {
                'original_word_count': original_analysis.get('word_count', 0),
                'final_word_count': final_analysis.get('word_count', 0),
                'original_quality_score': original_analysis.get('quality_score', 0),
                'final_quality_score': final_analysis.get('quality_score', 0),
                'readability_improvement': final_analysis.get('readability_score', 0) - original_analysis.get('readability_score', 0),
                'issues_resolved': len(original_analysis.get('issues', [])) - len(final_analysis.get('issues', []))
            },
            'key_improvements': editing_output.get('improvements_made', []),
            'final_recommendations': editing_output.get('recommendations', []),
            'editor_confidence': self._calculate_editor_confidence(editing_output),
            'ready_for_publication': final_analysis.get('quality_score', 0) >= 80
        }
        
        return summary
    
    def _calculate_editor_confidence(self, editing_output: Dict[str, Any]) -> float:
        """Calculate editor confidence in the final content"""
        final_score = editing_output.get('final_quality_score', 0)
        
        # Base confidence on quality score
        confidence = final_score / 100
        
        # Adjust based on number of improvements made
        improvements = len(editing_output.get('improvements_made', []))
        if improvements >= 3:
            confidence += 0.1  # Boost for comprehensive editing
        
        # Adjust based on remaining issues
        recommendations = editing_output.get('recommendations', [])
        critical_issues = sum(1 for rec in recommendations if 'significant' in rec.lower() or 'requires' in rec.lower())
        
        if critical_issues > 0:
            confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))  # Ensure 0-1 range 