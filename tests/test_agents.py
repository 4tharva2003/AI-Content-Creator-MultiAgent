"""
Unit tests for AI Multi-Agent Content Creation Pipeline

This module contains basic tests to ensure the agents work correctly.
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.coordinator import CoordinatorAgent
from agents.researcher import ResearchAgent
from agents.writer import WriterAgent
from agents.editor import EditorAgent
from agents.seo_optimizer import SEOAgent


class TestCoordinatorAgent(unittest.TestCase):
    """Test the Coordinator Agent functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.requirements = {
            'topic': 'Test Topic',
            'word_count': 1000,
            'target_audience': 'General audience',
            'tone': 'Professional',
            'seo_keywords': ['test', 'example'],
            'content_type': 'Blog post'
        }
    
    def test_create_content_plan(self):
        """Test content plan creation"""
        coordinator = CoordinatorAgent()
        plan = coordinator.create_content_plan(self.requirements)
        
        self.assertIn('topic', plan)
        self.assertIn('tasks', plan)
        self.assertIn('quality_criteria', plan)
        self.assertEqual(plan['topic'], 'Test Topic')
        self.assertEqual(plan['word_count'], 1000)
    
    def test_validate_content_quality(self):
        """Test content quality validation"""
        coordinator = CoordinatorAgent()
        plan = coordinator.create_content_plan(self.requirements)
        
        test_content = "This is a test content. " * 100  # 500 words
        validation = coordinator.validate_content_quality(test_content, plan)
        
        self.assertIn('overall_score', validation)
        self.assertIn('passed', validation)
        self.assertIn('checks', validation)


class TestResearchAgent(unittest.TestCase):
    """Test the Research Agent functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.requirements = {
            'topic': 'Test Topic',
            'target_audience': 'General audience',
            'seo_keywords': ['test', 'example']
        }
    
    @patch('utils.tools.WebSearchTool.run')
    def test_conduct_research(self, mock_search):
        """Test research functionality"""
        # Mock search results
        mock_search.return_value = [
            {
                'title': 'Test Result',
                'url': 'https://example.com',
                'snippet': 'This is a test snippet about the topic.'
            }
        ]
        
        researcher = ResearchAgent()
        research_output = researcher.conduct_research('Test Topic', self.requirements)
        
        self.assertIn('topic', research_output)
        self.assertIn('research_summary', research_output)
        self.assertIn('key_facts', research_output)
        self.assertIn('source_references', research_output)
        self.assertEqual(research_output['topic'], 'Test Topic')


class TestWriterAgent(unittest.TestCase):
    """Test the Writer Agent functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.research_data = {
            'topic': 'Test Topic',
            'key_facts': ['Fact 1', 'Fact 2'],
            'statistics': ['Stat 1', 'Stat 2'],
            'expert_quotes': ['Quote 1'],
            'content_outline': ['Introduction', 'Main Content', 'Conclusion']
        }
        self.requirements = {
            'topic': 'Test Topic',
            'word_count': 500,
            'tone': 'Professional',
            'target_audience': 'General audience',
            'content_type': 'Blog post'
        }
    
    def test_create_content(self):
        """Test content creation functionality"""
        writer = WriterAgent()
        writer_output = writer.create_content(self.research_data, self.requirements)
        
        self.assertIn('content', writer_output)
        self.assertIn('word_count', writer_output)
        self.assertIn('readability_metrics', writer_output)
        self.assertIn('tone_analysis', writer_output)
        
        # Check that content is not empty
        self.assertTrue(len(writer_output['content']) > 0)
        self.assertTrue(writer_output['word_count'] > 0)


class TestEditorAgent(unittest.TestCase):
    """Test the Editor Agent functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_content = """
        # Test Article
        
        This is a test article. It has multiple sentences. Some sentences are longer than others.
        
        ## Section 1
        
        This section contains information about the topic. It provides details and explanations.
        """
        
        self.requirements = {
            'word_count': 100,
            'seo_keywords': ['test']
        }
    
    def test_edit_content(self):
        """Test content editing functionality"""
        editor = EditorAgent()
        editing_output = editor.edit_content(self.test_content, self.requirements)
        
        self.assertIn('edited_content', editing_output)
        self.assertIn('improvements_made', editing_output)
        self.assertIn('final_quality_score', editing_output)
        self.assertIn('recommendations', editing_output)
        
        # Check that edited content exists
        self.assertTrue(len(editing_output['edited_content']) > 0)


class TestSEOAgent(unittest.TestCase):
    """Test the SEO Agent functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_content = """
        # Test Article About AI
        
        This is an article about artificial intelligence. AI is important for technology.
        
        ## Benefits of AI
        
        Artificial intelligence offers many benefits including efficiency and automation.
        """
        
        self.requirements = {
            'topic': 'AI',
            'seo_keywords': ['artificial intelligence', 'AI', 'technology']
        }
    
    def test_optimize_content(self):
        """Test SEO optimization functionality"""
        seo_agent = SEOAgent()
        seo_output = seo_agent.optimize_content(self.test_content, self.requirements)
        
        self.assertIn('optimized_content', seo_output)
        self.assertIn('meta_tags', seo_output)
        self.assertIn('seo_score', seo_output)
        self.assertIn('keyword_report', seo_output)
        
        # Check that meta tags are generated
        meta_tags = seo_output['meta_tags']
        self.assertIn('title', meta_tags)
        self.assertIn('description', meta_tags)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete pipeline"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.requirements = {
            'topic': 'Machine Learning',
            'word_count': 300,
            'target_audience': 'Developers',
            'tone': 'Technical',
            'seo_keywords': ['machine learning', 'ML', 'algorithms'],
            'content_type': 'Article'
        }
    
    @patch('utils.tools.WebSearchTool.run')
    def test_pipeline_integration(self, mock_search):
        """Test basic pipeline integration"""
        # Mock search results for research agent
        mock_search.return_value = [
            {
                'title': 'Machine Learning Guide',
                'url': 'https://example.com/ml',
                'snippet': 'Machine learning is a subset of AI that focuses on algorithms.'
            }
        ]
        
        # Initialize agents
        coordinator = CoordinatorAgent()
        researcher = ResearchAgent()
        writer = WriterAgent()
        editor = EditorAgent()
        seo_agent = SEOAgent()
        
        # Test pipeline steps
        plan = coordinator.create_content_plan(self.requirements)
        self.assertIsInstance(plan, dict)
        
        research = researcher.conduct_research(self.requirements['topic'], self.requirements)
        self.assertIsInstance(research, dict)
        
        writing = writer.create_content(research, self.requirements)
        self.assertIsInstance(writing, dict)
        self.assertIn('content', writing)
        
        editing = editor.edit_content(writing['content'], self.requirements)
        self.assertIsInstance(editing, dict)
        self.assertIn('edited_content', editing)
        
        seo = seo_agent.optimize_content(editing['edited_content'], self.requirements)
        self.assertIsInstance(seo, dict)
        self.assertIn('optimized_content', seo)
        
        # Final validation
        final_report = coordinator.create_final_report(
            seo['optimized_content'], plan, {
                'research': research,
                'writing': writing, 
                'editing': editing,
                'seo': seo
            }
        )
        self.assertIsInstance(final_report, dict)


if __name__ == '__main__':
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestCoordinatorAgent))
    test_suite.addTest(unittest.makeSuite(TestResearchAgent))
    test_suite.addTest(unittest.makeSuite(TestWriterAgent))
    test_suite.addTest(unittest.makeSuite(TestEditorAgent))
    test_suite.addTest(unittest.makeSuite(TestSEOAgent))
    test_suite.addTest(unittest.makeSuite(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}") 