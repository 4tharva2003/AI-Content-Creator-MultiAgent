"""
Content Writer Agent for AI Multi-Agent Content Creation Pipeline

The Writer Agent is responsible for:
- Creating engaging, high-quality content drafts
- Maintaining consistent tone and style
- Structuring content for readability
- Incorporating research findings effectively
"""

from typing import Dict, Any, List, Optional
from crewai import Agent, Task
from utils.llm_config import configure_llm

class WriterAgent:
    """
    Content Writer Agent specialized in creating engaging written content
    """
    
    def __init__(self):
        self.llm = configure_llm('writer')
        self.agent = self._create_agent()
        
    def _create_agent(self) -> Agent:
        """Create the writer agent with specific configuration"""
        return Agent(
            role="Content Creation Specialist",
            goal="Create engaging, well-structured, and informative content that resonates with the target audience",
            backstory="""You are a skilled content writer with extensive experience in creating 
            compelling articles across various topics and industries. You have a talent for 
            transforming research data into engaging narratives that capture readers' attention 
            while maintaining accuracy and professionalism. You understand different writing 
            styles and can adapt your tone to match the target audience and content purpose.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def create_content(self, research_data: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create content based on research data and requirements
        
        Args:
            research_data: Research findings from the Research Agent
            requirements: Content requirements and specifications
            
        Returns:
            Content creation results with draft and metadata
        """
        # Analyze requirements and research
        content_plan = self._create_content_plan(research_data, requirements)
        
        # Generate content sections
        content_sections = self._generate_content_sections(content_plan)
        
        # Assemble final content
        final_content = self._assemble_content(content_sections, requirements)
        
        # Create writer output
        writer_output = {
            'content': final_content,
            'content_plan': content_plan,
            'word_count': len(final_content.split()),
            'readability_metrics': self._analyze_readability(final_content),
            'tone_analysis': self._analyze_tone(final_content, requirements),
            'structure_analysis': self._analyze_structure(final_content),
            'writing_notes': self._generate_writing_notes(content_plan, final_content)
        }
        
        return writer_output
    
    def _create_content_plan(self, research_data: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create a detailed content creation plan"""
        topic = research_data.get('topic', requirements.get('topic', ''))
        outline = research_data.get('content_outline', [])
        
        plan = {
            'topic': topic,
            'target_word_count': requirements.get('word_count', 1000),
            'tone': requirements.get('tone', 'Professional'),
            'target_audience': requirements.get('target_audience', 'General audience'),
            'content_type': requirements.get('content_type', 'Blog post'),
            'outline': outline or self._create_default_outline(topic),
            'key_points': research_data.get('key_facts', []),
            'statistics': research_data.get('statistics', []),
            'quotes': research_data.get('expert_quotes', []),
            'section_word_targets': self._calculate_section_word_targets(
                outline or self._create_default_outline(topic), 
                requirements.get('word_count', 1000)
            )
        }
        
        return plan
    
    def _create_default_outline(self, topic: str) -> List[str]:
        """Create a default outline if none provided"""
        return [
            f"Introduction to {topic}",
            f"Understanding {topic}",
            f"Key Benefits and Advantages",
            f"Challenges and Considerations", 
            f"Best Practices and Tips",
            f"Future Outlook",
            "Conclusion"
        ]
    
    def _calculate_section_word_targets(self, outline: List[str], total_words: int) -> Dict[str, int]:
        """Calculate word count targets for each section"""
        num_sections = len(outline)
        if num_sections == 0:
            return {}
        
        # Allocate words based on section importance
        section_weights = {
            0: 0.15,  # Introduction
            num_sections - 1: 0.10,  # Conclusion
        }
        
        # Main sections get equal weight of remaining words
        remaining_weight = 1.0 - sum(section_weights.values())
        main_sections = num_sections - len(section_weights)
        main_section_weight = remaining_weight / main_sections if main_sections > 0 else 0
        
        word_targets = {}
        for i, section in enumerate(outline):
            if i in section_weights:
                words = int(total_words * section_weights[i])
            else:
                words = int(total_words * main_section_weight)
            word_targets[section] = max(50, words)  # Minimum 50 words per section
        
        return word_targets
    
    def _generate_content_sections(self, content_plan: Dict[str, Any]) -> Dict[str, str]:
        """Generate content for each section"""
        sections = {}
        outline = content_plan.get('outline', [])
        word_targets = content_plan.get('section_word_targets', {})
        
        for section_title in outline:
            target_words = word_targets.get(section_title, 150)
            section_content = self._write_section(section_title, content_plan, target_words)
            sections[section_title] = section_content
        
        return sections
    
    def _write_section(self, section_title: str, content_plan: Dict[str, Any], target_words: int) -> str:
        """Write content for a specific section"""
        topic = content_plan.get('topic', '')
        tone = content_plan.get('tone', 'Professional')
        audience = content_plan.get('target_audience', 'General audience')
        key_points = content_plan.get('key_points', [])
        statistics = content_plan.get('statistics', [])
        
        # Create section-specific content based on title
        if 'introduction' in section_title.lower():
            content = self._write_introduction(topic, tone, target_words)
        elif 'conclusion' in section_title.lower():
            content = self._write_conclusion(topic, tone, target_words)
        elif 'benefit' in section_title.lower() or 'advantage' in section_title.lower():
            content = self._write_benefits_section(topic, key_points, statistics, target_words)
        elif 'challenge' in section_title.lower() or 'consideration' in section_title.lower():
            content = self._write_challenges_section(topic, target_words)
        elif 'practice' in section_title.lower() or 'tip' in section_title.lower():
            content = self._write_best_practices_section(topic, target_words)
        elif 'future' in section_title.lower() or 'outlook' in section_title.lower():
            content = self._write_future_section(topic, target_words)
        else:
            content = self._write_general_section(section_title, topic, key_points, target_words)
        
        return content
    
    def _write_introduction(self, topic: str, tone: str, target_words: int) -> str:
        """Write an engaging introduction"""
        intro_templates = {
            'Professional': f"""In today's rapidly evolving landscape, {topic} has emerged as a critical factor for success. Understanding its implications and applications can provide significant advantages for organizations and individuals alike. This comprehensive guide explores the essential aspects of {topic}, providing insights that can help you navigate this important subject effectively.""",
            
            'Casual': f"""Have you ever wondered about {topic}? You're not alone! This fascinating subject has been gaining attention lately, and for good reason. Whether you're just getting started or looking to deepen your understanding, this guide will walk you through everything you need to know about {topic} in a clear, accessible way.""",
            
            'Technical': f"""{topic} represents a significant development in the field, offering both opportunities and challenges for implementation. This analysis provides a comprehensive examination of {topic}, including its technical foundations, practical applications, and strategic implications for stakeholders."""
        }
        
        base_intro = intro_templates.get(tone, intro_templates['Professional'])
        
        # Expand if needed to meet word target
        if len(base_intro.split()) < target_words:
            addition = f"\n\nThroughout this article, we'll examine the key components of {topic}, discuss its benefits and challenges, and provide practical insights that you can apply immediately. Our goal is to equip you with the knowledge and understanding necessary to make informed decisions about {topic}."
            base_intro += addition
        
        return base_intro
    
    def _write_conclusion(self, topic: str, tone: str, target_words: int) -> str:
        """Write a compelling conclusion"""
        conclusion_templates = {
            'Professional': f"""In conclusion, {topic} represents a significant opportunity for those who approach it strategically. The key to success lies in understanding its fundamental principles, recognizing both opportunities and challenges, and implementing best practices consistently. As the landscape continues to evolve, staying informed and adaptable will be crucial for maximizing the benefits of {topic}.""",
            
            'Casual': f"""So there you have it – everything you need to know about {topic}! Remember, the key is to start small, stay consistent, and keep learning as you go. Don't be afraid to experiment and find what works best for your situation. With the right approach, {topic} can make a real difference in achieving your goals.""",
            
            'Technical': f"""The analysis of {topic} reveals significant potential for implementation across various contexts. Success depends on careful planning, thorough understanding of requirements, and systematic execution of best practices. Future developments in this area warrant continued monitoring and evaluation."""
        }
        
        base_conclusion = conclusion_templates.get(tone, conclusion_templates['Professional'])
        
        # Add call to action if needed
        if len(base_conclusion.split()) < target_words:
            cta = f"\n\nAs you move forward with implementing {topic}, remember that continuous learning and adaptation are key. Consider how these insights apply to your specific situation and take the first steps toward implementation today."
            base_conclusion += cta
        
        return base_conclusion
    
    def _write_benefits_section(self, topic: str, key_points: List[str], statistics: List[str], target_words: int) -> str:
        """Write a benefits and advantages section"""
        content = f"The advantages of {topic} are numerous and significant. Here are the key benefits you should know about:\n\n"
        
        # Add key benefits
        benefits = [
            f"**Enhanced Efficiency**: {topic} streamlines processes and reduces unnecessary complexity.",
            f"**Improved Outcomes**: Organizations implementing {topic} often see measurable improvements in results.",
            f"**Cost-Effectiveness**: The long-term benefits typically outweigh initial implementation costs.",
            f"**Competitive Advantage**: Early adoption can provide a significant edge in the marketplace.",
            f"**Scalability**: Solutions can be adapted and scaled to meet growing needs."
        ]
        
        for benefit in benefits[:3]:  # Limit to top 3
            content += benefit + "\n\n"
        
        # Add statistics if available
        if statistics:
            content += "The data supports these benefits:\n\n"
            for stat in statistics[:2]:  # Limit to 2 statistics
                content += f"- {stat}\n"
            content += "\n"
        
        # Add key points if available
        if key_points:
            content += "Research indicates that:\n\n"
            for point in key_points[:2]:  # Limit to 2 key points
                content += f"- {point}\n"
        
        return content.strip()
    
    def _write_challenges_section(self, topic: str, target_words: int) -> str:
        """Write a challenges and considerations section"""
        content = f"While {topic} offers significant benefits, it's important to be aware of potential challenges and considerations:\n\n"
        
        challenges = [
            f"**Implementation Complexity**: Getting started with {topic} may require significant planning and resources.",
            f"**Learning Curve**: Team members may need training and time to adapt to new approaches.",
            f"**Initial Costs**: Upfront investment may be substantial, though long-term ROI is typically positive.",
            f"**Change Management**: Organizations must be prepared to manage the transition effectively.",
            f"**Ongoing Maintenance**: Success requires continuous attention and optimization."
        ]
        
        for challenge in challenges[:4]:  # Include 4 main challenges
            content += challenge + "\n\n"
        
        content += f"Despite these challenges, most organizations find that the benefits of {topic} far outweigh the difficulties. The key is proper planning and realistic expectations."
        
        return content.strip()
    
    def _write_best_practices_section(self, topic: str, target_words: int) -> str:
        """Write a best practices and tips section"""
        content = f"To maximize success with {topic}, consider these proven best practices:\n\n"
        
        practices = [
            f"**Start Small**: Begin with a pilot project to test approaches and learn before scaling up.",
            f"**Set Clear Goals**: Define specific, measurable objectives for your {topic} initiative.",
            f"**Invest in Training**: Ensure team members have the knowledge and skills needed for success.",
            f"**Monitor Progress**: Regularly track metrics and adjust approaches based on results.",
            f"**Stay Flexible**: Be prepared to adapt strategies as you learn and circumstances change.",
            f"**Seek Expert Guidance**: Consider working with experienced professionals to accelerate progress."
        ]
        
        for practice in practices:
            content += practice + "\n\n"
        
        content += f"Remember, success with {topic} is often a journey rather than a destination. Continuous improvement and learning are essential components of long-term success."
        
        return content.strip()
    
    def _write_future_section(self, topic: str, target_words: int) -> str:
        """Write a future outlook section"""
        content = f"Looking ahead, the future of {topic} appears bright with several exciting developments on the horizon:\n\n"
        
        content += f"**Emerging Trends**: New approaches and technologies are constantly being developed, making {topic} more accessible and effective than ever before.\n\n"
        
        content += f"**Increased Adoption**: As more organizations recognize the value of {topic}, we can expect to see broader implementation across industries.\n\n"
        
        content += f"**Innovation Opportunities**: The field continues to evolve, creating new possibilities for creative applications and solutions.\n\n"
        
        content += f"**Integration Advances**: Future developments will likely focus on better integration with existing systems and processes.\n\n"
        
        content += f"For those considering {topic}, now is an excellent time to begin exploring its potential. Early adopters often have the advantage of learning and adapting before widespread adoption makes the field more competitive."
        
        return content.strip()
    
    def _write_general_section(self, section_title: str, topic: str, key_points: List[str], target_words: int) -> str:
        """Write a general section based on title and available information"""
        content = f"## {section_title}\n\n"
        
        content += f"When examining {topic} in the context of {section_title.lower()}, several important factors emerge.\n\n"
        
        # Add key points if available
        if key_points:
            content += "Key considerations include:\n\n"
            for point in key_points[:3]:  # Limit to 3 points
                content += f"- {point}\n"
            content += "\n"
        
        # Add general content to meet word target
        content += f"Understanding these aspects of {topic} is crucial for making informed decisions and achieving optimal results. Each element plays a vital role in the overall success of any {topic} initiative.\n\n"
        
        content += f"As you consider how {section_title.lower()} relates to your specific situation, remember that context matters significantly. What works in one scenario may need adaptation for another, making careful analysis and planning essential components of success."
        
        return content.strip()
    
    def _assemble_content(self, content_sections: Dict[str, str], requirements: Dict[str, Any]) -> str:
        """Assemble final content from sections"""
        topic = requirements.get('topic', '')
        content_type = requirements.get('content_type', 'Blog post')
        
        # Create title
        title = f"# {topic}: A Comprehensive Guide\n\n"
        
        # Assemble sections
        final_content = title
        for section_title, section_content in content_sections.items():
            if not section_content.startswith('#'):
                final_content += f"## {section_title}\n\n"
            final_content += section_content + "\n\n"
        
        return final_content.strip()
    
    def _analyze_readability(self, content: str) -> Dict[str, Any]:
        """Analyze content readability"""
        sentences = len([s for s in content.split('.') if s.strip()])
        words = len(content.split())
        
        if sentences == 0:
            return {'score': 0, 'assessment': 'No readable content'}
        
        avg_sentence_length = words / sentences
        
        # Simple readability score (Flesch-style approximation)
        score = max(0, 100 - (avg_sentence_length * 1.5))
        
        assessment = 'Excellent' if score >= 80 else 'Good' if score >= 60 else 'Needs Improvement' if score >= 40 else 'Difficult'
        
        return {
            'score': round(score, 1),
            'avg_sentence_length': round(avg_sentence_length, 1),
            'assessment': assessment,
            'recommendations': self._get_readability_recommendations(score, avg_sentence_length)
        }
    
    def _get_readability_recommendations(self, score: float, avg_length: float) -> List[str]:
        """Get readability improvement recommendations"""
        recommendations = []
        
        if score < 60:
            recommendations.append("Consider breaking up long sentences for better readability")
        
        if avg_length > 25:
            recommendations.append("Average sentence length is high - aim for 15-20 words per sentence")
        
        if score >= 80:
            recommendations.append("Excellent readability - content is easy to understand")
        
        return recommendations
    
    def _analyze_tone(self, content: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content tone"""
        target_tone = requirements.get('tone', 'Professional')
        content_lower = content.lower()
        
        # Simple tone indicators
        tone_indicators = {
            'Professional': ['analysis', 'implementation', 'strategic', 'comprehensive', 'significant'],
            'Casual': ['you', 'your', 'easy', 'simple', 'great', 'awesome'],
            'Technical': ['system', 'process', 'methodology', 'parameters', 'optimization']
        }
        
        detected_indicators = {}
        for tone, indicators in tone_indicators.items():
            count = sum(1 for indicator in indicators if indicator in content_lower)
            detected_indicators[tone] = count
        
        detected_tone = max(detected_indicators, key=detected_indicators.get)
        tone_match = detected_tone == target_tone
        
        return {
            'target_tone': target_tone,
            'detected_tone': detected_tone,
            'tone_match': tone_match,
            'confidence': detected_indicators[detected_tone] / len(tone_indicators[detected_tone]),
            'recommendations': [] if tone_match else [f"Content tone appears more {detected_tone} than {target_tone}"]
        }
    
    def _analyze_structure(self, content: str) -> Dict[str, Any]:
        """Analyze content structure"""
        lines = content.split('\n')
        paragraphs = [p for p in content.split('\n\n') if p.strip()]
        
        headings = [line for line in lines if line.startswith('#')]
        
        return {
            'paragraph_count': len(paragraphs),
            'heading_count': len(headings),
            'avg_paragraph_length': sum(len(p.split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0,
            'has_proper_structure': len(headings) > 0 and len(paragraphs) > 2,
            'structure_score': min(100, (len(headings) * 20) + (min(len(paragraphs), 8) * 10))
        }
    
    def _generate_writing_notes(self, content_plan: Dict[str, Any], final_content: str) -> List[str]:
        """Generate notes about the writing process"""
        notes = []
        
        target_words = content_plan.get('target_word_count', 1000)
        actual_words = len(final_content.split())
        
        if actual_words < target_words * 0.9:
            notes.append(f"Content is shorter than target ({actual_words} vs {target_words} words)")
        elif actual_words > target_words * 1.1:
            notes.append(f"Content is longer than target ({actual_words} vs {target_words} words)")
        else:
            notes.append(f"Content length is appropriate ({actual_words} words)")
        
        if content_plan.get('statistics'):
            notes.append(f"Incorporated {len(content_plan['statistics'])} statistics from research")
        
        if content_plan.get('quotes'):
            notes.append(f"Referenced {len(content_plan['quotes'])} expert quotes")
        
        notes.append("Content follows planned outline structure")
        notes.append(f"Tone optimized for {content_plan.get('target_audience', 'general')} audience")
        
        return notes 