"""
Research Agent for AI Multi-Agent Content Creation Pipeline

The Research Agent is responsible for:
- Conducting comprehensive topic research
- Finding relevant, credible sources
- Fact-checking and validation
- Providing structured research summaries
"""

from typing import Dict, Any, List, Optional
from crewai import Agent, Task
from utils.llm_config import configure_llm
from utils.tools import WebSearchTool

class ResearchAgent:
    """
    Research Agent specialized in topic research and fact-finding
    """
    
    def __init__(self):
        self.llm = configure_llm('researcher')
        self.web_search_tool = WebSearchTool()
        self.agent = self._create_agent()
        
    def _create_agent(self) -> Agent:
        """Create the research agent with specific configuration"""
        return Agent(
            role="Content Research Specialist",
            goal="Conduct thorough, accurate research on assigned topics and provide comprehensive, fact-based information",
            backstory="""You are a meticulous research specialist with extensive experience in 
            information gathering and verification. You have a talent for finding credible sources, 
            extracting key insights, and presenting complex information in an organized manner. 
            You understand the importance of accuracy and always verify information from multiple 
            sources. Your research forms the foundation for high-quality content creation.""",
            verbose=True,
            allow_delegation=False,
            tools=[self.web_search_tool],
            llm=self.llm
        )
    
    def conduct_research(self, topic: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Conduct comprehensive research on a given topic
        
        Args:
            topic: The main topic to research
            requirements: Additional requirements and specifications
            
        Returns:
            Comprehensive research results
        """
        # Generate research queries
        queries = self._generate_research_queries(topic, requirements)
        
        # Conduct searches
        search_results = []
        for query in queries:
            results = self.web_search_tool.run(query, num_results=5)
            search_results.extend(results)
        
        # Process and structure results
        research_output = {
            'topic': topic,
            'research_summary': self._create_research_summary(topic, search_results),
            'key_facts': self._extract_key_facts(search_results),
            'statistics': self._extract_statistics(search_results),
            'expert_quotes': self._extract_quotes(search_results),
            'source_references': self._compile_sources(search_results),
            'content_outline': self._suggest_content_outline(topic, requirements),
            'research_gaps': self._identify_research_gaps(topic, search_results),
            'credibility_assessment': self._assess_source_credibility(search_results)
        }
        
        return research_output
    
    def _generate_research_queries(self, topic: str, requirements: Dict[str, Any]) -> List[str]:
        """Generate specific research queries based on topic and requirements"""
        base_queries = [
            topic,
            f"{topic} definition",
            f"{topic} benefits",
            f"{topic} challenges",
            f"{topic} statistics",
            f"{topic} recent developments"
        ]
        
        # Add audience-specific queries
        audience = requirements.get('target_audience', '')
        if audience:
            base_queries.extend([
                f"{topic} for {audience}",
                f"{topic} {audience} case studies"
            ])
        
        # Add keyword-specific queries
        keywords = requirements.get('seo_keywords', [])
        for keyword in keywords[:3]:  # Limit to top 3 keywords
            base_queries.append(f"{keyword} {topic}")
        
        return base_queries[:8]  # Limit total queries
    
    def _create_research_summary(self, topic: str, search_results: List[Dict[str, str]]) -> str:
        """Create a comprehensive research summary"""
        # Filter out error results
        valid_results = [r for r in search_results if 'error' not in r]
        
        if not valid_results:
            return f"Limited research available on {topic}. Recommend using authoritative sources."
        
        # Combine snippets for analysis
        combined_text = " ".join([r.get('snippet', '') for r in valid_results[:10]])
        
        # Create structured summary
        summary = f"""
        Research Summary: {topic}
        
        Overview: Based on analysis of {len(valid_results)} sources, {topic} appears to be a significant subject with multiple dimensions worth exploring.
        
        Key Themes Identified:
        - {self._extract_main_themes(combined_text)}
        
        Current Status: The topic shows ongoing relevance with recent developments and continued interest from various stakeholders.
        
        Research Confidence: {'High' if len(valid_results) >= 5 else 'Medium' if len(valid_results) >= 3 else 'Low'}
        """
        
        return summary.strip()
    
    def _extract_key_facts(self, search_results: List[Dict[str, str]]) -> List[str]:
        """Extract key facts from search results"""
        facts = []
        valid_results = [r for r in search_results if 'error' not in r]
        
        for result in valid_results[:5]:
            snippet = result.get('snippet', '')
            # Simple fact extraction (in production, would use more sophisticated NLP)
            sentences = snippet.split('.')
            for sentence in sentences:
                if len(sentence.strip()) > 50 and any(word in sentence.lower() for word in 
                    ['is', 'are', 'was', 'were', 'has', 'have', 'can', 'will', 'according']):
                    facts.append(sentence.strip())
                    if len(facts) >= 5:
                        break
        
        return facts[:5]
    
    def _extract_statistics(self, search_results: List[Dict[str, str]]) -> List[str]:
        """Extract statistics and numerical data"""
        import re
        statistics = []
        valid_results = [r for r in search_results if 'error' not in r]
        
        for result in valid_results:
            snippet = result.get('snippet', '')
            # Find numbers and percentages
            stat_patterns = [
                r'\d+%',  # Percentages
                r'\$[\d,]+',  # Dollar amounts
                r'\d+\.\d+\s*(million|billion|thousand)',  # Large numbers
                r'\d+\s*(times|fold)',  # Multipliers
            ]
            
            for pattern in stat_patterns:
                matches = re.findall(pattern, snippet, re.IGNORECASE)
                for match in matches:
                    context = snippet[max(0, snippet.find(match)-50):snippet.find(match)+50]
                    statistics.append(f"{match}: {context.strip()}")
                    if len(statistics) >= 3:
                        break
        
        return statistics[:3]
    
    def _extract_quotes(self, search_results: List[Dict[str, str]]) -> List[str]:
        """Extract potential expert quotes or authoritative statements"""
        quotes = []
        valid_results = [r for r in search_results if 'error' not in r]
        
        for result in valid_results:
            snippet = result.get('snippet', '')
            title = result.get('title', '')
            
            # Look for quoted text or authoritative statements
            if '"' in snippet:
                quoted_parts = snippet.split('"')
                for i in range(1, len(quoted_parts), 2):  # Every other part is quoted
                    if len(quoted_parts[i]) > 20:
                        quotes.append(f'"{quoted_parts[i]}" - {title}')
                        if len(quotes) >= 3:
                            break
        
        return quotes[:3]
    
    def _compile_sources(self, search_results: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Compile credible sources with proper attribution"""
        sources = []
        valid_results = [r for r in search_results if 'error' not in r]
        
        for result in valid_results[:5]:
            source = {
                'title': result.get('title', 'Unknown Title'),
                'url': result.get('url', ''),
                'snippet': result.get('snippet', '')[:200] + '...',
                'credibility': self._assess_single_source_credibility(result)
            }
            sources.append(source)
        
        # Sort by credibility
        sources.sort(key=lambda x: x['credibility'], reverse=True)
        return sources
    
    def _suggest_content_outline(self, topic: str, requirements: Dict[str, Any]) -> List[str]:
        """Suggest a content outline based on research"""
        outline = [
            f"Introduction to {topic}",
            f"What is {topic}?",
            f"Key Benefits of {topic}",
            f"Challenges and Considerations",
            f"Current Trends and Developments",
            f"Practical Applications",
            f"Future Outlook",
            f"Conclusion"
        ]
        
        # Customize based on content type
        content_type = requirements.get('content_type', 'blog post')
        if content_type.lower() in ['guide', 'tutorial', 'how-to']:
            outline = [
                f"Introduction to {topic}",
                "Prerequisites and Requirements",
                "Step-by-Step Process",
                "Best Practices",
                "Common Mistakes to Avoid",
                "Advanced Tips",
                "Conclusion and Next Steps"
            ]
        elif content_type.lower() in ['review', 'comparison']:
            outline = [
                f"Overview of {topic}",
                "Methodology",
                "Detailed Analysis",
                "Pros and Cons",
                "Comparisons",
                "Recommendations",
                "Final Verdict"
            ]
        
        return outline
    
    def _identify_research_gaps(self, topic: str, search_results: List[Dict[str, str]]) -> List[str]:
        """Identify potential gaps in research"""
        gaps = []
        valid_results = [r for r in search_results if 'error' not in r]
        
        if len(valid_results) < 3:
            gaps.append("Limited source diversity - recommend finding additional authoritative sources")
        
        # Check for recency
        recent_indicators = ['2024', '2023', 'recent', 'latest', 'new', 'current']
        has_recent_content = any(indicator in ' '.join([r.get('snippet', '') + r.get('title', '') 
                                                      for r in valid_results]).lower() 
                                for indicator in recent_indicators)
        
        if not has_recent_content:
            gaps.append("Lack of recent information - consider finding more current sources")
        
        # Check for different perspectives
        combined_content = ' '.join([r.get('snippet', '') for r in valid_results]).lower()
        if 'however' not in combined_content and 'but' not in combined_content:
            gaps.append("Limited perspective diversity - consider finding contrasting viewpoints")
        
        return gaps
    
    def _assess_source_credibility(self, search_results: List[Dict[str, str]]) -> Dict[str, Any]:
        """Assess overall credibility of sources"""
        valid_results = [r for r in search_results if 'error' not in r]
        credibility_scores = [self._assess_single_source_credibility(r) for r in valid_results]
        
        if not credibility_scores:
            return {'overall_score': 0, 'assessment': 'No valid sources found'}
        
        avg_score = sum(credibility_scores) / len(credibility_scores)
        
        assessment = {
            'overall_score': round(avg_score, 2),
            'total_sources': len(valid_results),
            'high_credibility_sources': sum(1 for score in credibility_scores if score >= 0.8),
            'assessment': self._get_credibility_assessment(avg_score)
        }
        
        return assessment
    
    def _assess_single_source_credibility(self, source: Dict[str, str]) -> float:
        """Assess credibility of a single source (simple heuristic)"""
        url = source.get('url', '').lower()
        title = source.get('title', '').lower()
        
        score = 0.5  # Base score
        
        # Domain-based scoring
        high_credibility_domains = ['.edu', '.gov', '.org', 'wikipedia', 'scholar.google']
        medium_credibility_domains = ['.com', 'news', 'journal', 'research']
        
        for domain in high_credibility_domains:
            if domain in url:
                score += 0.3
                break
        else:
            for domain in medium_credibility_domains:
                if domain in url:
                    score += 0.1
                    break
        
        # Content quality indicators
        quality_indicators = ['research', 'study', 'analysis', 'report', 'official']
        for indicator in quality_indicators:
            if indicator in title:
                score += 0.1
                break
        
        return min(1.0, score)
    
    def _get_credibility_assessment(self, score: float) -> str:
        """Get textual assessment of credibility score"""
        if score >= 0.8:
            return "High credibility - sources are trustworthy and authoritative"
        elif score >= 0.6:
            return "Good credibility - sources are generally reliable"
        elif score >= 0.4:
            return "Medium credibility - sources should be verified"
        else:
            return "Low credibility - additional authoritative sources needed"
    
    def _extract_main_themes(self, text: str) -> str:
        """Extract main themes from combined text (simplified approach)"""
        # This is a simplified approach - in production, you'd use more sophisticated NLP
        common_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'among', 'around', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'a', 'an']
        
        words = text.lower().split()
        word_freq = {}
        
        for word in words:
            clean_word = word.strip('.,!?";:()[]{}')
            if len(clean_word) > 3 and clean_word not in common_words:
                word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
        
        # Get top themes
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        themes = [word for word, _ in top_words]
        
        return ", ".join(themes) if themes else "General information and insights" 