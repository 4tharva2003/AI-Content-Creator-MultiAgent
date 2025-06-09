"""
AI Multi-Agent Content Creation Pipeline - Streamlit Web Application

This application provides a user-friendly interface for the AI multi-agent content creation system,
allowing users to generate high-quality, SEO-optimized content through collaborative AI agents.
"""

import streamlit as st
import time
import json
from datetime import datetime
from typing import Dict, Any, List

# Import agents
from agents.coordinator import CoordinatorAgent
from agents.researcher import ResearchAgent
from agents.writer import WriterAgent
from agents.editor import EditorAgent
from agents.seo_optimizer import SEOAgent

# Import utilities
from utils.llm_config import test_llm_connection, get_available_models

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="AI Content Creation Pipeline",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if 'pipeline_results' not in st.session_state:
        st.session_state.pipeline_results = None
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    
    # Header
    st.title("🤖 AI Multi-Agent Content Creation Pipeline")
    st.markdown("Transform your ideas into high-quality, SEO-optimized content using specialized AI agents")
    
    # Sidebar
    render_sidebar()
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Create Content", "📊 Results Dashboard", "🔧 Agent Configuration", "ℹ️ About"])
    
    with tab1:
        render_content_creation_tab()
    
    with tab2:
        render_results_dashboard()
    
    with tab3:
        render_agent_configuration()
    
    with tab4:
        render_about_tab()

def render_sidebar():
    """Render the sidebar with system status and quick settings"""
    st.sidebar.header("🎛️ Control Panel")
    
    # System status
    st.sidebar.subheader("System Status")
    with st.sidebar.expander("🔌 LLM Connection", expanded=False):
        if st.button("Test Connection", key="test_connection"):
            with st.spinner("Testing LLM connection..."):
                status = test_llm_connection()
                if status['status'] == 'success':
                    st.success(f"✅ Connected to {status['model']}")
                else:
                    st.error(f"❌ Connection failed: {status['message']}")
    
    # Quick settings
    st.sidebar.subheader("⚙️ Quick Settings")
    
    # Model selection
    models = get_available_models()
    selected_model = st.sidebar.selectbox(
        "LLM Model",
        list(models.keys()),
        help="Select the language model for content generation"
    )
    
    # Content quality level
    quality_level = st.sidebar.select_slider(
        "Quality Level",
        options=["Fast", "Balanced", "High Quality"],
        value="Balanced",
        help="Higher quality takes longer but produces better results"
    )
    
    # Pipeline progress
    if st.session_state.current_step > 0:
        st.sidebar.subheader("📈 Pipeline Progress")
        progress = st.session_state.current_step / 5  # 5 total steps
        st.sidebar.progress(progress)
        
        steps = ["🔍 Research", "✍️ Writing", "📝 Editing", "🔍 SEO", "✅ Review"]
        current_step_name = steps[min(st.session_state.current_step - 1, 4)]
        st.sidebar.write(f"Current: {current_step_name}")

def render_content_creation_tab():
    """Render the main content creation interface"""
    st.header("📝 Content Creation Pipeline")
    
    # Content requirements form
    with st.form("content_requirements"):
        st.subheader("📋 Content Requirements")
        
        col1, col2 = st.columns(2)
        
        with col1:
            topic = st.text_input(
                "Topic/Subject *",
                placeholder="e.g., Artificial Intelligence in Healthcare",
                help="The main topic you want to create content about"
            )
            
            content_type = st.selectbox(
                "Content Type",
                ["Blog post", "Article", "Guide", "Tutorial", "Review", "Case Study"],
                help="Type of content to generate"
            )
            
            word_count = st.number_input(
                "Target Word Count",
                min_value=300,
                max_value=5000,
                value=1000,
                step=100,
                help="Approximate number of words for the final content"
            )
        
        with col2:
            target_audience = st.text_input(
                "Target Audience",
                placeholder="e.g., Healthcare professionals, Tech enthusiasts",
                help="Who is the intended audience for this content?"
            )
            
            tone = st.selectbox(
                "Tone & Style",
                ["Professional", "Casual", "Technical", "Academic"],
                help="The writing tone and style for the content"
            )
            
            seo_keywords = st.text_area(
                "SEO Keywords (one per line)",
                placeholder="artificial intelligence\nAI healthcare\nmachine learning",
                help="Target keywords for SEO optimization"
            ).strip()
        
        # Advanced options
        with st.expander("🔧 Advanced Options"):
            include_statistics = st.checkbox("Include Statistics & Data", value=True)
            include_faq = st.checkbox("Generate FAQ Section", value=True)
            include_related_topics = st.checkbox("Add Related Topics", value=True)
            
            custom_outline = st.text_area(
                "Custom Content Outline (optional)",
                placeholder="Introduction\nKey Benefits\nImplementation Steps\nConclusion",
                help="Provide a custom outline or leave blank for automatic generation"
            )
        
        # Submit button
        submitted = st.form_submit_button("🚀 Generate Content", type="primary")
        
        if submitted:
            if not topic:
                st.error("❌ Please enter a topic to continue")
                return
            
            # Prepare requirements
            requirements = {
                'topic': topic,
                'content_type': content_type,
                'word_count': word_count,
                'target_audience': target_audience or 'General audience',
                'tone': tone,
                'seo_keywords': [kw.strip() for kw in seo_keywords.split('\n') if kw.strip()],
                'include_statistics': include_statistics,
                'include_faq': include_faq,
                'include_related_topics': include_related_topics,
                'custom_outline': [line.strip() for line in custom_outline.split('\n') if line.strip()] if custom_outline else None
            }
            
            # Run the pipeline
            run_content_pipeline(requirements)

def run_content_pipeline(requirements: Dict[str, Any]):
    """Execute the multi-agent content creation pipeline"""
    
    # Initialize progress tracking
    progress_container = st.container()
    status_container = st.container()
    
    with progress_container:
        st.subheader("🔄 Pipeline Execution")
        progress_bar = st.progress(0)
        status_text = st.empty()
    
    try:
        # Initialize agents
        coordinator = CoordinatorAgent()
        researcher = ResearchAgent()
        writer = WriterAgent()
        editor = EditorAgent()
        seo_optimizer = SEOAgent()
        
        results = {}
        
        # Step 1: Coordinator creates plan
        st.session_state.current_step = 1
        progress_bar.progress(0.1)
        status_text.text("🎯 Coordinator: Creating content plan...")
        
        plan = coordinator.create_content_plan(requirements)
        results['plan'] = plan
        time.sleep(1)  # Simulate processing time
        
        # Step 2: Research phase
        st.session_state.current_step = 2
        progress_bar.progress(0.3)
        status_text.text("🔍 Research Agent: Conducting topic research...")
        
        research_output = researcher.conduct_research(requirements['topic'], requirements)
        results['research'] = research_output
        time.sleep(2)
        
        # Step 3: Writing phase
        st.session_state.current_step = 3
        progress_bar.progress(0.5)
        status_text.text("✍️ Writer Agent: Creating content draft...")
        
        writer_output = writer.create_content(research_output, requirements)
        results['writing'] = writer_output
        time.sleep(2)
        
        # Step 4: Editing phase
        st.session_state.current_step = 4
        progress_bar.progress(0.7)
        status_text.text("📝 Editor Agent: Reviewing and improving content...")
        
        editor_output = editor.edit_content(writer_output['content'], requirements, writer_output)
        results['editing'] = editor_output
        time.sleep(1)
        
        # Step 5: SEO optimization
        st.session_state.current_step = 5
        progress_bar.progress(0.9)
        status_text.text("🔍 SEO Agent: Optimizing for search engines...")
        
        seo_output = seo_optimizer.optimize_content(editor_output['edited_content'], requirements, editor_output)
        results['seo'] = seo_output
        time.sleep(1)
        
        # Final review by coordinator
        progress_bar.progress(1.0)
        status_text.text("✅ Coordinator: Final quality review...")
        
        final_report = coordinator.create_final_report(
            seo_output['optimized_content'],
            plan,
            {
                'research': research_output,
                'writing': writer_output,
                'editing': editor_output,
                'seo': seo_output
            }
        )
        results['final_report'] = final_report
        results['final_content'] = seo_output['optimized_content']
        results['meta_tags'] = seo_output['meta_tags']
        
        # Store results
        st.session_state.pipeline_results = results
        st.session_state.current_step = 0
        
        # Success message
        with status_container:
            st.success("🎉 Content creation pipeline completed successfully!")
            
            # Quick preview
            with st.expander("👀 Quick Preview", expanded=True):
                st.markdown("### Generated Content")
                st.markdown(results['final_content'][:500] + "..." if len(results['final_content']) > 500 else results['final_content'])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Word Count", len(results['final_content'].split()))
                with col2:
                    st.metric("SEO Score", f"{results['seo']['seo_score']:.1f}/100")
                with col3:
                    quality_score = results['final_report']['quality_assessment']['overall_score']
                    st.metric("Quality Score", f"{quality_score:.1f}/100")
    
    except Exception as e:
        st.error(f"❌ Pipeline execution failed: {str(e)}")
        st.session_state.current_step = 0

def render_results_dashboard():
    """Render the results dashboard"""
    st.header("📊 Results Dashboard")
    
    if st.session_state.pipeline_results is None:
        st.info("💡 No results available. Generate content first using the 'Create Content' tab.")
        return
    
    results = st.session_state.pipeline_results
    
    # Metrics overview
    st.subheader("📈 Content Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        word_count = len(results['final_content'].split())
        st.metric("Word Count", word_count)
    
    with col2:
        seo_score = results['seo']['seo_score']
        st.metric("SEO Score", f"{seo_score:.1f}/100")
    
    with col3:
        quality_score = results['final_report']['quality_assessment']['overall_score']
        st.metric("Quality Score", f"{quality_score:.1f}/100")
    
    with col4:
        readability = results['writing']['readability_metrics']['score']
        st.metric("Readability", f"{readability:.1f}/100")
    
    # Content sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📄 Final Content", "🔍 Research", "📝 Writing", "✏️ Editing", "🔍 SEO"])
    
    with tab1:
        render_final_content_tab(results)
    
    with tab2:
        render_research_results(results['research'])
    
    with tab3:
        render_writing_results(results['writing'])
    
    with tab4:
        render_editing_results(results['editing'])
    
    with tab5:
        render_seo_results(results['seo'])

def render_final_content_tab(results: Dict[str, Any]):
    """Render the final content tab"""
    st.subheader("📄 Final Content")
    
    # Content display
    st.markdown("### Content")
    st.markdown(results['final_content'])
    
    # Download options
    st.subheader("💾 Download Options")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            "📄 Download as Markdown",
            data=results['final_content'],
            file_name=f"content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )
    
    with col2:
        # Convert to HTML (basic)
        html_content = results['final_content'].replace('\n\n', '</p><p>').replace('\n', '<br>')
        html_content = f"<html><body><p>{html_content}</p></body></html>"
        st.download_button(
            "🌐 Download as HTML",
            data=html_content,
            file_name=f"content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            mime="text/html"
        )
    
    with col3:
        # Full report as JSON
        report_data = json.dumps(results['final_report'], indent=2)
        st.download_button(
            "📊 Download Report (JSON)",
            data=report_data,
            file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    # Meta tags
    st.subheader("🏷️ SEO Meta Tags")
    meta_tags = results['meta_tags']
    
    col1, col2 = st.columns(2)
    with col1:
        st.code(f'<title>{meta_tags["title"]}</title>', language='html')
        st.code(f'<meta name="description" content="{meta_tags["description"]}">', language='html')
    
    with col2:
        st.code(f'<meta name="keywords" content="{meta_tags["keywords"]}">', language='html')
        st.code(f'<meta property="og:title" content="{meta_tags["og:title"]}">', language='html')

def render_research_results(research: Dict[str, Any]):
    """Render research results"""
    st.subheader("🔍 Research Results")
    
    # Research summary
    st.markdown("### Research Summary")
    st.markdown(research['research_summary'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Key facts
        st.markdown("### Key Facts")
        for i, fact in enumerate(research['key_facts'][:5], 1):
            st.markdown(f"{i}. {fact}")
        
        # Statistics
        if research['statistics']:
            st.markdown("### Statistics")
            for stat in research['statistics']:
                st.markdown(f"• {stat}")
    
    with col2:
        # Source credibility
        credibility = research['credibility_assessment']
        st.markdown("### Source Credibility")
        st.metric("Overall Score", f"{credibility['overall_score']:.2f}/1.0")
        st.markdown(f"**Assessment:** {credibility['assessment']}")
        
        # Content outline
        st.markdown("### Suggested Outline")
        for item in research['content_outline']:
            st.markdown(f"• {item}")

def render_writing_results(writing: Dict[str, Any]):
    """Render writing results"""
    st.subheader("✍️ Writing Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Readability metrics
        st.markdown("### Readability Analysis")
        readability = writing['readability_metrics']
        st.metric("Readability Score", f"{readability['score']:.1f}/100")
        st.metric("Avg Sentence Length", f"{readability['avg_sentence_length']:.1f} words")
        st.write(f"**Assessment:** {readability['assessment']}")
        
        # Tone analysis
        st.markdown("### Tone Analysis")
        tone = writing['tone_analysis']
        st.write(f"**Target Tone:** {tone['target_tone']}")
        st.write(f"**Detected Tone:** {tone['detected_tone']}")
        match_icon = "✅" if tone['tone_match'] else "❌"
        st.write(f"**Match:** {match_icon}")
    
    with col2:
        # Structure analysis
        st.markdown("### Structure Analysis")
        structure = writing['structure_analysis']
        st.metric("Paragraphs", structure['paragraph_count'])
        st.metric("Headings", structure['heading_count'])
        st.metric("Structure Score", f"{structure['structure_score']:.0f}/100")
        
        # Writing notes
        st.markdown("### Writing Notes")
        for note in writing['writing_notes']:
            st.markdown(f"• {note}")

def render_editing_results(editing: Dict[str, Any]):
    """Render editing results"""
    st.subheader("📝 Editing Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Quality improvement
        st.markdown("### Quality Improvement")
        st.metric("Final Quality Score", f"{editing['final_quality_score']:.1f}/100")
        
        # Improvements made
        st.markdown("### Improvements Made")
        for improvement in editing['improvements_made']:
            st.markdown(f"✅ {improvement}")
    
    with col2:
        # Editing recommendations
        st.markdown("### Recommendations")
        for rec in editing['recommendations']:
            st.markdown(f"💡 {rec}")
        
        # Quality analysis
        quality = editing['quality_analysis']
        if quality.get('issues'):
            st.markdown("### Issues Addressed")
            for issue in quality['issues']:
                st.markdown(f"🔧 {issue}")

def render_seo_results(seo: Dict[str, Any]):
    """Render SEO results"""
    st.subheader("🔍 SEO Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # SEO score
        st.metric("SEO Score", f"{seo['seo_score']:.1f}/100")
        
        # Keyword report
        st.markdown("### Keyword Analysis")
        keyword_report = seo['keyword_report']
        
        for keyword, analysis in keyword_report['keyword_analysis'].items():
            st.markdown(f"**{keyword}**")
            st.write(f"• Count: {analysis['count']}")
            st.write(f"• Density: {analysis['density']}%")
            density_icon = "✅" if analysis['optimal_density'] else "⚠️"
            st.write(f"• Optimal: {density_icon}")
    
    with col2:
        # SEO recommendations
        st.markdown("### SEO Recommendations")
        for rec in seo['recommendations']:
            st.markdown(f"📈 {rec}")
        
        # Optimizations made
        st.markdown("### Optimizations Applied")
        for opt in seo['optimizations_made']:
            st.markdown(f"✅ {opt}")

def render_agent_configuration():
    """Render agent configuration tab"""
    st.header("🔧 Agent Configuration")
    
    st.info("🔧 Agent configuration features will be available in future updates. Currently using default optimized settings.")
    
    # Model information
    st.subheader("🤖 Available Models")
    models = get_available_models()
    
    for model_id, info in models.items():
        with st.expander(f"{info['name']} ({info['provider']})"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Cost:** {info['cost']}")
                st.write(f"**Context Length:** {info['context_length']:,} tokens")
            with col2:
                st.write(f"**Description:** {info['description']}")

def render_about_tab():
    """Render about tab"""
    st.header("ℹ️ About the AI Multi-Agent Content Creation Pipeline")
    
    st.markdown("""
    ### 🎯 Project Overview
    
    This project demonstrates the power of **AI multi-agent systems** for content creation. It uses specialized 
    AI agents that collaborate to produce high-quality, SEO-optimized content automatically.
    
    ### 🤖 Agent Architecture
    
    The system consists of 5 specialized agents:
    
    1. **🎯 Coordinator Agent** - Orchestrates the entire pipeline and ensures quality standards
    2. **🔍 Research Agent** - Conducts comprehensive topic research and fact-checking
    3. **✍️ Writer Agent** - Creates engaging, well-structured content drafts
    4. **📝 Editor Agent** - Reviews and improves content for clarity and flow
    5. **🔍 SEO Agent** - Optimizes content for search engines with keyword integration
    
    ### 🛠️ Technologies Used
    
    - **CrewAI**: Multi-agent orchestration framework
    - **LangChain**: LLM integration and prompt management
    - **Streamlit**: Web application interface
    - **OpenAI GPT**: Language model for content generation
    - **Python**: Core programming language
    
    ### 🎓 Why Multi-Agent Systems?
    
    Multi-agent systems are ideal for content creation because:
    
    - **Specialization**: Each agent excels at specific tasks
    - **Quality**: Multiple perspectives improve output quality  
    - **Scalability**: Easy to add new specialized agents
    - **Collaboration**: Agents work together for superior results
    
    ### 🚀 Key Features
    
    ✅ **Automated Research** - Comprehensive topic research with source validation  
    ✅ **Quality Writing** - Engaging content tailored to your audience  
    ✅ **Professional Editing** - Grammar, clarity, and flow improvements  
    ✅ **SEO Optimization** - Keyword integration and meta tag generation  
    ✅ **Real-time Progress** - Watch agents collaborate in real-time  
    ✅ **Multiple Formats** - Download as Markdown, HTML, or JSON  
    
    ### 📊 Performance Metrics
    
    The system tracks multiple quality metrics:
    - Content quality score (grammar, structure, coherence)
    - SEO optimization score (keyword density, meta tags)
    - Readability score (sentence length, complexity)
    - Source credibility assessment
    
    ### 🔮 Future Enhancements
    
    - **Fact-Checking Agent** for claim verification
    - **Social Media Agent** for platform-specific content
    - **Image Generation Agent** for visual content
    - **Translation Agent** for multi-language support
    - **Analytics Agent** for performance tracking
    """)
    
    # Demo video placeholder
    st.subheader("🎥 Demo Video")
    st.info("📹 Demo video coming soon! This will showcase the full pipeline in action.")
    
    # Contact and credits
    st.subheader("👥 Credits & Contact")
    st.markdown("""
    **Built with:**
    - CrewAI framework for multi-agent coordination
    - LangChain for LLM integration
    - Streamlit for the web interface
    
    **Created for:** CN Assignment - AI Multi-Agent Systems
    
    **GitHub Repository:** [Link to be added]
    """)

if __name__ == "__main__":
    main() 