"""
SEO Optimizer Agent for AI Multi-Agent Content Creation Pipeline

The SEO Agent is responsible for:
- Optimizing content for search engines
- Integrating target keywords naturally
- Generating meta tags and descriptions
- Providing SEO recommendations and analysis
"""

from typing import Dict, Any, List, Optional
from crewai import Agent, Task
from utils.llm_config import configure_llm
from utils.tools import SEOAnalyzerTool

class SEOAgent:
    """
    SEO Optimizer Agent specialized in search engine optimization
    """
    
    def __init__(self):
        self.llm = configure_llm('seo')
        self.seo_analyzer = SEOAnalyzerTool()
        self.agent = self._create_agent()
        
    def _create_agent(self) -> Agent:
        """Create the SEO agent with specific configuration"""
        return Agent(
            role="SEO Optimization Specialist",
            goal="Optimize content for search engines while maintaining quality and readability",
            backstory="""You are an experienced SEO specialist with deep knowledge of search engine 
            algorithms and optimization techniques. You understand how to integrate keywords naturally, 
            optimize content structure for search engines, and create compelling meta tags that drive 
            clicks. Your expertise helps content rank higher in search results while maintaining 
            excellent user experience and readability.""",
            verbose=True,
            allow_delegation=False,
            tools=[self.seo_analyzer],
            llm=self.llm
        )
    
    def optimize_content(self, content: str, requirements: Dict[str, Any], editor_output: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Optimize content for SEO based on target keywords and requirements
        
        Args:
            content: Content to optimize
            requirements: SEO requirements including target keywords
            editor_output: Output from the Editor Agent (optional)
            
        Returns:
            SEO optimization results with optimized content and analysis
        """
        target_keywords = requirements.get('seo_keywords', [])
        
        # Analyze current SEO status
        seo_analysis = self.seo_analyzer.run(content, target_keywords)
        
        # Perform SEO optimizations
        optimized_content = self._optimize_content_seo(content, target_keywords, requirements)
        
        # Generate meta tags
        meta_tags = self._generate_meta_tags(optimized_content, target_keywords, requirements)
        
        # Create final SEO analysis
        final_analysis = self.seo_analyzer.run(optimized_content, target_keywords)
        
        # Generate SEO output
        seo_output = {
            'original_content': content,
            'optimized_content': optimized_content,
            'target_keywords': target_keywords,
            'seo_analysis': seo_analysis,
            'final_seo_analysis': final_analysis,
            'meta_tags': meta_tags,
            'optimizations_made': self._track_seo_optimizations(content, optimized_content, target_keywords),
            'seo_score': final_analysis.get('seo_score', 0),
            'recommendations': final_analysis.get('recommendations', []),
            'keyword_report': self._generate_keyword_report(optimized_content, target_keywords)
        }
        
        return seo_output
    
    def _optimize_content_seo(self, content: str, keywords: List[str], requirements: Dict[str, Any]) -> str:
        """Apply SEO optimizations to content"""
        optimized_content = content
        
        # Apply optimizations in sequence
        optimized_content = self._optimize_title_seo(optimized_content, keywords)
        optimized_content = self._optimize_headings_seo(optimized_content, keywords)
        optimized_content = self._integrate_keywords_naturally(optimized_content, keywords)
        optimized_content = self._optimize_content_structure(optimized_content)
        optimized_content = self._add_seo_elements(optimized_content, keywords, requirements)
        
        return optimized_content
    
    def _optimize_title_seo(self, content: str, keywords: List[str]) -> str:
        """Optimize the title for SEO"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if line.startswith('# '):
                title = line[2:].strip()
                
                # Check if primary keyword is in title
                if keywords and keywords[0].lower() not in title.lower():
                    # Try to integrate primary keyword naturally
                    primary_keyword = keywords[0]
                    
                    # If title doesn't have keyword, try to add it
                    if ':' in title:
                        parts = title.split(':')
                        # Add keyword to first part if possible
                        if primary_keyword.lower() not in parts[0].lower():
                            title = f"{primary_keyword}: {parts[1].strip()}"
                    else:
                        # Add keyword at beginning
                        title = f"{primary_keyword}: {title}"
                    
                    lines[i] = f"# {title}"
                break
        
        return '\n'.join(lines)
    
    def _optimize_headings_seo(self, content: str, keywords: List[str]) -> str:
        """Optimize headings for SEO"""
        if not keywords:
            return content
        
        lines = content.split('\n')
        keyword_index = 0
        
        for i, line in enumerate(lines):
            if line.startswith('##') and not line.startswith('###'):
                heading = line.strip()
                heading_text = heading.lstrip('#').strip()
                
                # Try to integrate keywords into headings
                if keyword_index < len(keywords):
                    keyword = keywords[keyword_index]
                    
                    # Check if keyword already in heading
                    if keyword.lower() not in heading_text.lower():
                        # Try to integrate keyword naturally
                        if 'benefits' in heading_text.lower() or 'advantages' in heading_text.lower():
                            heading_text = f"{keyword} Benefits and Advantages"
                        elif 'challenges' in heading_text.lower():
                            heading_text = f"{keyword} Challenges and Solutions"
                        elif 'best practices' in heading_text.lower():
                            heading_text = f"Best Practices for {keyword}"
                        elif 'future' in heading_text.lower():
                            heading_text = f"Future of {keyword}"
                        
                        lines[i] = f"## {heading_text}"
                        keyword_index += 1
        
        return '\n'.join(lines)
    
    def _integrate_keywords_naturally(self, content: str, keywords: List[str]) -> str:
        """Integrate keywords naturally throughout the content"""
        if not keywords:
            return content
        
        optimized_content = content
        
        for keyword in keywords:
            # Calculate target density (aim for 1-2%)
            word_count = len(optimized_content.split())
            current_count = optimized_content.lower().count(keyword.lower())
            target_count = max(1, int(word_count * 0.015))  # 1.5% density
            
            if current_count < target_count:
                # Need to add more instances
                additions_needed = target_count - current_count
                optimized_content = self._add_keyword_naturally(optimized_content, keyword, additions_needed)
        
        return optimized_content
    
    def _add_keyword_naturally(self, content: str, keyword: str, count: int) -> str:
        """Add keyword naturally to content"""
        paragraphs = content.split('\n\n')
        modified_paragraphs = []
        additions_made = 0
        
        for para in paragraphs:
            if additions_made >= count:
                modified_paragraphs.append(para)
                continue
            
            # Skip headings and very short paragraphs
            if para.startswith('#') or len(para.split()) < 20:
                modified_paragraphs.append(para)
                continue
            
            # Try to add keyword naturally
            if keyword.lower() not in para.lower():
                # Find good insertion points
                sentences = para.split('.')
                for i, sentence in enumerate(sentences):
                    if len(sentence.split()) > 10 and additions_made < count:
                        # Try to replace generic terms with keyword
                        generic_terms = ['this technology', 'this approach', 'this method', 'this solution', 'it']
                        
                        for term in generic_terms:
                            if term in sentence.lower():
                                sentences[i] = sentence.replace(term, keyword, 1)
                                additions_made += 1
                                break
                        
                        if additions_made >= count:
                            break
                
                para = '.'.join(sentences)
            
            modified_paragraphs.append(para)
        
        return '\n\n'.join(modified_paragraphs)
    
    def _optimize_content_structure(self, content: str) -> str:
        """Optimize content structure for SEO"""
        lines = content.split('\n')
        optimized_lines = []
        
        for line in lines:
            # Ensure proper heading hierarchy
            if line.startswith('#'):
                # Keep existing structure but ensure consistency
                optimized_lines.append(line)
            elif line.strip() and not line.startswith('#'):
                # Ensure paragraphs are not too long for SEO
                if len(line.split()) > 200:
                    # Break into smaller paragraphs
                    sentences = line.split('.')
                    current_para = []
                    
                    for sentence in sentences:
                        current_para.append(sentence)
                        if len(' '.join(current_para).split()) > 100:
                            optimized_lines.append('.'.join(current_para).strip() + '.')
                            current_para = []
                    
                    if current_para:
                        optimized_lines.append('.'.join(current_para).strip())
                else:
                    optimized_lines.append(line)
            else:
                optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def _add_seo_elements(self, content: str, keywords: List[str], requirements: Dict[str, Any]) -> str:
        """Add additional SEO elements to content"""
        # Add FAQ section if appropriate
        if len(keywords) >= 2:
            faq_section = self._generate_faq_section(keywords, requirements)
            content += f"\n\n{faq_section}"
        
        # Add internal linking opportunities (placeholders)
        if 'related topics' not in content.lower():
            related_section = self._generate_related_topics_section(keywords)
            content += f"\n\n{related_section}"
        
        return content
    
    def _generate_faq_section(self, keywords: List[str], requirements: Dict[str, Any]) -> str:
        """Generate FAQ section for SEO"""
        primary_keyword = keywords[0] if keywords else requirements.get('topic', '')
        
        faq_section = f"## Frequently Asked Questions about {primary_keyword}\n\n"
        
        # Generate common FAQ questions
        faqs = [
            f"**What is {primary_keyword}?**\n{primary_keyword} is a comprehensive approach that offers numerous benefits for organizations and individuals looking to improve their outcomes.",
            
            f"**How does {primary_keyword} work?**\nThe implementation of {primary_keyword} involves several key steps and considerations that must be carefully planned and executed.",
            
            f"**What are the benefits of {primary_keyword}?**\nThe main benefits include improved efficiency, better results, cost-effectiveness, and competitive advantages in the marketplace.",
            
            f"**Is {primary_keyword} suitable for beginners?**\nYes, {primary_keyword} can be adapted for users at all levels, from beginners to advanced practitioners."
        ]
        
        for faq in faqs[:3]:  # Limit to 3 FAQs
            faq_section += faq + "\n\n"
        
        return faq_section.strip()
    
    def _generate_related_topics_section(self, keywords: List[str]) -> str:
        """Generate related topics section for internal linking"""
        section = "## Related Topics\n\n"
        section += "Explore these related subjects to deepen your understanding:\n\n"
        
        for keyword in keywords[:4]:  # Limit to 4 related topics
            section += f"- {keyword} Best Practices\n"
            section += f"- {keyword} Implementation Guide\n"
        
        section += "\nThese topics provide additional insights and practical guidance for your journey."
        
        return section
    
    def _generate_meta_tags(self, content: str, keywords: List[str], requirements: Dict[str, Any]) -> Dict[str, str]:
        """Generate SEO meta tags"""
        # Extract title
        title_line = next((line for line in content.split('\n') if line.startswith('# ')), '')
        title = title_line[2:].strip() if title_line else requirements.get('topic', 'Untitled')
        
        # Ensure title is within SEO limits (50-60 characters)
        if len(title) > 60:
            title = title[:57] + "..."
        elif len(title) < 30:
            primary_keyword = keywords[0] if keywords else ''
            if primary_keyword and primary_keyword not in title:
                title = f"{primary_keyword} - {title}"
        
        # Generate description
        # Find first substantial paragraph
        paragraphs = [p for p in content.split('\n\n') if p.strip() and not p.startswith('#')]
        first_para = paragraphs[0] if paragraphs else ''
        
        # Clean up for description
        description = first_para.replace('\n', ' ').strip()
        if len(description) > 160:
            description = description[:157] + "..."
        elif len(description) < 120:
            # Expand with keyword information
            if keywords:
                description += f" Learn about {', '.join(keywords[:2])} and more."
        
        # Generate keywords meta (though less important for modern SEO)
        meta_keywords = ', '.join(keywords[:5]) if keywords else ''
        
        # Generate Open Graph tags
        og_title = title
        og_description = description
        
        return {
            'title': title,
            'description': description,
            'keywords': meta_keywords,
            'og:title': og_title,
            'og:description': og_description,
            'og:type': 'article',
            'robots': 'index, follow',
            'canonical': f"https://example.com/{'-'.join(title.lower().split())}"
        }
    
    def _track_seo_optimizations(self, original: str, optimized: str, keywords: List[str]) -> List[str]:
        """Track SEO optimizations made"""
        optimizations = []
        
        # Check keyword integration
        for keyword in keywords:
            original_count = original.lower().count(keyword.lower())
            optimized_count = optimized.lower().count(keyword.lower())
            
            if optimized_count > original_count:
                optimizations.append(f"Increased '{keyword}' mentions from {original_count} to {optimized_count}")
        
        # Check structural improvements
        original_headings = len([line for line in original.split('\n') if line.startswith('##')])
        optimized_headings = len([line for line in optimized.split('\n') if line.startswith('##')])
        
        if optimized_headings > original_headings:
            optimizations.append("Added SEO-optimized headings")
        
        # Check for FAQ addition
        if 'frequently asked questions' in optimized.lower() and 'frequently asked questions' not in original.lower():
            optimizations.append("Added FAQ section for long-tail keyword targeting")
        
        # Check for related topics
        if 'related topics' in optimized.lower() and 'related topics' not in original.lower():
            optimizations.append("Added related topics section for internal linking")
        
        # Check title optimization
        original_title = next((line for line in original.split('\n') if line.startswith('# ')), '')
        optimized_title = next((line for line in optimized.split('\n') if line.startswith('# ')), '')
        
        if original_title != optimized_title:
            optimizations.append("Optimized title for primary keyword")
        
        if not optimizations:
            optimizations.append("Applied general SEO best practices")
        
        return optimizations
    
    def _generate_keyword_report(self, content: str, keywords: List[str]) -> Dict[str, Any]:
        """Generate detailed keyword usage report"""
        report = {
            'total_words': len(content.split()),
            'keyword_analysis': {},
            'density_analysis': {},
            'placement_analysis': {}
        }
        
        content_lower = content.lower()
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            count = content_lower.count(keyword_lower)
            density = (count / report['total_words']) * 100 if report['total_words'] > 0 else 0
            
            # Check placement
            in_title = keyword_lower in content_lower[:100]  # First 100 chars
            in_headings = any(keyword_lower in line.lower() for line in content.split('\n') if line.startswith('#'))
            in_first_para = keyword_lower in content_lower[:500]  # First 500 chars
            
            report['keyword_analysis'][keyword] = {
                'count': count,
                'density': round(density, 2),
                'in_title': in_title,
                'in_headings': in_headings,
                'in_first_paragraph': in_first_para,
                'optimal_density': 1.0 <= density <= 2.5
            }
            
            # Density assessment
            if density < 0.5:
                assessment = 'Too low - increase usage'
            elif density > 3.0:
                assessment = 'Too high - reduce usage'
            else:
                assessment = 'Optimal range'
            
            report['density_analysis'][keyword] = assessment
            
            # Placement score
            placement_score = sum([in_title, in_headings, in_first_para])
            report['placement_analysis'][keyword] = {
                'score': placement_score,
                'assessment': 'Excellent' if placement_score >= 2 else 'Good' if placement_score == 1 else 'Needs improvement'
            }
        
        return report
    
    def create_seo_summary(self, seo_output: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive SEO summary"""
        final_analysis = seo_output.get('final_seo_analysis', {})
        keyword_report = seo_output.get('keyword_report', {})
        
        summary = {
            'seo_score': final_analysis.get('seo_score', 0),
            'keyword_optimization': self._assess_keyword_optimization(keyword_report),
            'technical_seo': self._assess_technical_seo(seo_output),
            'content_optimization': self._assess_content_optimization(final_analysis),
            'recommendations': final_analysis.get('recommendations', []),
            'next_steps': self._generate_seo_next_steps(final_analysis),
            'meta_tags_ready': bool(seo_output.get('meta_tags')),
            'search_engine_ready': final_analysis.get('seo_score', 0) >= 70
        }
        
        return summary
    
    def _assess_keyword_optimization(self, keyword_report: Dict[str, Any]) -> Dict[str, Any]:
        """Assess keyword optimization quality"""
        if not keyword_report.get('keyword_analysis'):
            return {'score': 0, 'assessment': 'No keywords analyzed'}
        
        keyword_scores = []
        for keyword, analysis in keyword_report['keyword_analysis'].items():
            score = 0
            if analysis['optimal_density']:
                score += 40
            if analysis['in_title']:
                score += 20
            if analysis['in_headings']:
                score += 20
            if analysis['in_first_paragraph']:
                score += 20
            
            keyword_scores.append(score)
        
        avg_score = sum(keyword_scores) / len(keyword_scores) if keyword_scores else 0
        
        return {
            'score': round(avg_score, 1),
            'assessment': 'Excellent' if avg_score >= 80 else 'Good' if avg_score >= 60 else 'Needs improvement'
        }
    
    def _assess_technical_seo(self, seo_output: Dict[str, Any]) -> Dict[str, Any]:
        """Assess technical SEO elements"""
        meta_tags = seo_output.get('meta_tags', {})
        score = 0
        
        # Check meta tags
        if meta_tags.get('title') and 30 <= len(meta_tags['title']) <= 60:
            score += 25
        if meta_tags.get('description') and 120 <= len(meta_tags['description']) <= 160:
            score += 25
        if meta_tags.get('keywords'):
            score += 15
        if meta_tags.get('og:title') and meta_tags.get('og:description'):
            score += 20
        if meta_tags.get('canonical'):
            score += 15
        
        return {
            'score': score,
            'assessment': 'Excellent' if score >= 80 else 'Good' if score >= 60 else 'Needs improvement'
        }
    
    def _assess_content_optimization(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess content-level SEO optimization"""
        structure = analysis.get('content_structure', {})
        score = 0
        
        if structure.get('has_headings'):
            score += 30
        if structure.get('word_count', 0) >= 300:
            score += 25
        if structure.get('has_lists'):
            score += 15
        if structure.get('internal_links', 0) > 0:
            score += 15
        if len(structure.get('heading_hierarchy', [])) >= 3:
            score += 15
        
        return {
            'score': score,
            'assessment': 'Excellent' if score >= 80 else 'Good' if score >= 60 else 'Needs improvement'
        }
    
    def _generate_seo_next_steps(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate next steps for SEO improvement"""
        seo_score = analysis.get('seo_score', 0)
        recommendations = analysis.get('recommendations', [])
        
        next_steps = []
        
        if seo_score >= 80:
            next_steps.extend([
                "Content is SEO-ready for publication",
                "Monitor search rankings after publication",
                "Consider creating related content for topic clusters"
            ])
        elif seo_score >= 60:
            next_steps.extend([
                "Address remaining SEO recommendations",
                "Content is nearly ready for publication",
                "Consider additional keyword integration"
            ])
        else:
            next_steps.extend([
                "Significant SEO improvements needed",
                "Focus on keyword integration and content structure",
                "Review meta tags and technical elements"
            ])
        
        # Add specific recommendations
        next_steps.extend(recommendations[:2])
        
        return next_steps[:5] 