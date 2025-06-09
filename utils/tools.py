"""
Specialized Tools for AI Multi-Agent Content Creation Pipeline

This module provides tools that agents can use to perform specific tasks:
- Web search for research
- Content validation and quality checks
- SEO analysis and optimization
"""

import re
import requests
from typing import Dict, List, Any, Optional
from urllib.parse import quote
from bs4 import BeautifulSoup

class WebSearchTool:
    """Tool for conducting web searches and extracting relevant information"""
    
    name: str = "Web Search Tool"
    description: str = "Search the web for information on a given topic and return relevant snippets"
    
    def run(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Perform web search and return results
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of search results with title, snippet, and URL
        """
        try:
            # Using a simple search approach - in production, you'd use proper search APIs
            search_url = f"https://www.google.com/search?q={quote(query)}&num={num_results}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            search_results = soup.find_all('div', class_='g')[:num_results]
            
            for result in search_results:
                title_elem = result.find('h3')
                link_elem = result.find('a')
                snippet_elem = result.find('span', {'data-ved': True})
                
                if title_elem and link_elem:
                    title = title_elem.get_text()
                    url = link_elem.get('href', '')
                    snippet = snippet_elem.get_text() if snippet_elem else "No snippet available"
                    
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet
                    })
            
            return results
            
        except Exception as e:
            return [{'error': f'Search failed: {str(e)}'}]

class ContentValidatorTool:
    """Tool for validating content quality and coherence"""
    
    name: str = "Content Validator Tool"
    description: str = "Validate content quality, check for coherence, and identify potential issues"
    
    def run(self, content: str) -> Dict[str, Any]:
        """
        Validate content and return quality metrics
        
        Args:
            content: Content to validate
            
        Returns:
            Dictionary with validation results
        """
        try:
            validation_results = {
                'word_count': len(content.split()),
                'character_count': len(content),
                'sentence_count': len(re.split(r'[.!?]+', content)) - 1,
                'paragraph_count': len([p for p in content.split('\n\n') if p.strip()]),
                'readability_score': self._calculate_readability(content),
                'issues': self._identify_issues(content),
                'quality_score': 0
            }
            
            # Calculate overall quality score
            validation_results['quality_score'] = self._calculate_quality_score(validation_results)
            
            return validation_results
            
        except Exception as e:
            return {'error': f'Validation failed: {str(e)}'}
    
    def _calculate_readability(self, content: str) -> float:
        """Calculate a simple readability score (0-100)"""
        sentences = len(re.split(r'[.!?]+', content)) - 1
        words = len(content.split())
        
        if sentences == 0:
            return 0
            
        avg_sentence_length = words / sentences
        
        # Simple readability calculation (lower is better)
        readability = max(0, 100 - (avg_sentence_length * 2))
        return round(readability, 2)
    
    def _identify_issues(self, content: str) -> List[str]:
        """Identify potential issues with the content"""
        issues = []
        
        # Check for very long paragraphs
        paragraphs = [p for p in content.split('\n\n') if p.strip()]
        for i, para in enumerate(paragraphs):
            if len(para.split()) > 200:
                issues.append(f"Paragraph {i+1} is very long ({len(para.split())} words)")
        
        # Check for repetitive phrases
        words = content.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 5:  # Only check longer words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        for word, freq in word_freq.items():
            if freq > 10:
                issues.append(f"Word '{word}' appears {freq} times (potentially repetitive)")
        
        # Check for missing punctuation
        if not re.search(r'[.!?]$', content.strip()):
            issues.append("Content doesn't end with proper punctuation")
        
        return issues
    
    def _calculate_quality_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall quality score based on metrics"""
        score = 100
        
        # Penalize for issues
        score -= len(metrics['issues']) * 5
        
        # Adjust for readability
        if metrics['readability_score'] < 30:
            score -= 20
        elif metrics['readability_score'] < 50:
            score -= 10
        
        # Adjust for length (too short or too long)
        word_count = metrics['word_count']
        if word_count < 100:
            score -= 30
        elif word_count < 300:
            score -= 15
        elif word_count > 3000:
            score -= 10
        
        return max(0, min(100, score))

class SEOAnalyzerTool:
    """Tool for analyzing and optimizing content for SEO"""
    
    name: str = "SEO Analyzer Tool"
    description: str = "Analyze content for SEO optimization and provide recommendations"
    
    def run(self, content: str, target_keywords: List[str] = None) -> Dict[str, Any]:
        """
        Analyze content for SEO and return optimization suggestions
        
        Args:
            content: Content to analyze
            target_keywords: List of target keywords
            
        Returns:
            Dictionary with SEO analysis results
        """
        try:
            target_keywords = target_keywords or []
            
            analysis = {
                'keyword_analysis': self._analyze_keywords(content, target_keywords),
                'content_structure': self._analyze_structure(content),
                'meta_suggestions': self._generate_meta_suggestions(content),
                'seo_score': 0,
                'recommendations': []
            }
            
            # Calculate SEO score and generate recommendations
            analysis['seo_score'] = self._calculate_seo_score(analysis)
            analysis['recommendations'] = self._generate_recommendations(analysis)
            
            return analysis
            
        except Exception as e:
            return {'error': f'SEO analysis failed: {str(e)}'}
    
    def _analyze_keywords(self, content: str, keywords: List[str]) -> Dict[str, Any]:
        """Analyze keyword usage in content"""
        content_lower = content.lower()
        
        keyword_analysis = {
            'target_keywords': keywords,
            'keyword_density': {},
            'keyword_positions': {},
            'missing_keywords': []
        }
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            count = content_lower.count(keyword_lower)
            total_words = len(content.split())
            
            if total_words > 0:
                density = (count / total_words) * 100
                keyword_analysis['keyword_density'][keyword] = round(density, 2)
            
            # Find positions
            positions = []
            start = 0
            while True:
                pos = content_lower.find(keyword_lower, start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + 1
            
            keyword_analysis['keyword_positions'][keyword] = positions
            
            if count == 0:
                keyword_analysis['missing_keywords'].append(keyword)
        
        return keyword_analysis
    
    def _analyze_structure(self, content: str) -> Dict[str, Any]:
        """Analyze content structure for SEO"""
        structure = {
            'has_headings': bool(re.search(r'#+\s', content)),  # Markdown headings
            'heading_hierarchy': self._check_heading_hierarchy(content),
            'paragraph_count': len([p for p in content.split('\n\n') if p.strip()]),
            'avg_paragraph_length': 0,
            'has_lists': bool(re.search(r'^\s*[-*+]\s', content, re.MULTILINE)),
            'internal_links': len(re.findall(r'\[.*?\]\(.*?\)', content)),
            'word_count': len(content.split())
        }
        
        paragraphs = [p for p in content.split('\n\n') if p.strip()]
        if paragraphs:
            total_words = sum(len(p.split()) for p in paragraphs)
            structure['avg_paragraph_length'] = round(total_words / len(paragraphs), 1)
        
        return structure
    
    def _check_heading_hierarchy(self, content: str) -> List[str]:
        """Check heading hierarchy in content"""
        headings = re.findall(r'^(#+)\s+(.+)$', content, re.MULTILINE)
        hierarchy = []
        
        for level, text in headings:
            hierarchy.append(f"H{len(level)}: {text}")
        
        return hierarchy
    
    def _generate_meta_suggestions(self, content: str) -> Dict[str, str]:
        """Generate meta tag suggestions"""
        sentences = re.split(r'[.!?]+', content)
        first_sentence = sentences[0].strip() if sentences else ""
        
        # Generate title suggestion (first sentence or first 60 characters)
        title_suggestion = first_sentence[:60] + "..." if len(first_sentence) > 60 else first_sentence
        
        # Generate description suggestion (first 155 characters)
        description_suggestion = content[:155] + "..." if len(content) > 155 else content
        
        return {
            'title': title_suggestion,
            'description': description_suggestion.replace('\n', ' ').strip()
        }
    
    def _calculate_seo_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall SEO score"""
        score = 100
        
        # Keyword optimization
        keyword_analysis = analysis['keyword_analysis']
        if keyword_analysis['missing_keywords']:
            score -= len(keyword_analysis['missing_keywords']) * 10
        
        # Content structure
        structure = analysis['content_structure']
        if not structure['has_headings']:
            score -= 20
        if structure['word_count'] < 300:
            score -= 15
        if structure['avg_paragraph_length'] > 150:
            score -= 10
        
        return max(0, min(100, score))
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate SEO recommendations"""
        recommendations = []
        
        keyword_analysis = analysis['keyword_analysis']
        structure = analysis['content_structure']
        
        # Keyword recommendations
        if keyword_analysis['missing_keywords']:
            recommendations.append(f"Include missing keywords: {', '.join(keyword_analysis['missing_keywords'])}")
        
        # Structure recommendations
        if not structure['has_headings']:
            recommendations.append("Add headings to improve content structure")
        
        if structure['word_count'] < 300:
            recommendations.append("Increase content length to at least 300 words")
        
        if structure['avg_paragraph_length'] > 150:
            recommendations.append("Break up long paragraphs for better readability")
        
        if not structure['has_lists']:
            recommendations.append("Consider adding bullet points or numbered lists")
        
        if structure['internal_links'] == 0:
            recommendations.append("Add internal links to related content")
        
        return recommendations 