"""
Student Portal - AI Chatbot & Study Tools
"""

import streamlit as st
import asyncio
from datetime import datetime
from utils.ui_components import (
    check_authentication, render_chat_message, 
    render_info_box, render_loading_spinner
)
from services.rag_engine import RAGEngine
from services.analytics import AnalyticsService

# Page config
st.set_page_config(
    page_title="Student Portal",
    page_icon="👨‍🎓",
    layout="wide"
)

# Check authentication
check_authentication()

# Initialize services
@st.cache_resource
def init_services():
    return RAGEngine(), AnalyticsService()

rag_engine, analytics = init_services()

# Initialize chat history in session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_session_id' not in st.session_state:
    st.session_state.current_session_id = None

# Page header
st.markdown("# 👨‍🎓 Student Portal")
st.markdown("### AI-Powered Learning Assistant")

# Sidebar - Mode Selection
with st.sidebar:
    st.markdown("### 🎯 Select Mode")
    
    mode = st.radio(
        "Choose how you want to learn:",
        ["💬 Q&A", "📚 Study Notes", "📝 Practice Questions"],
        help="Different modes for different learning needs"
    )
    
    mode_mapping = {
        "💬 Q&A": "qa",
        "📚 Study Notes": "notes",
        "📝 Practice Questions": "practice"
    }
    
    selected_mode = mode_mapping[mode]
    
    st.markdown("---")
    
    # Session management
    st.markdown("### 💾 Session")
    if st.button("🔄 New Chat Session", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.current_session_id = None
        st.success("Started new session!")
    
    if st.button("📥 Download Chat History", use_container_width=True):
        if st.session_state.chat_history:
            chat_text = "\n\n".join([
                f"{'You' if msg['is_user'] else 'AI'}: {msg['content']}"
                for msg in st.session_state.chat_history
            ])
            st.download_button(
                "Download",
                chat_text,
                file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

# Main content area
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 My Stats", "ℹ️ How to Use"])

with tab1:
    # Mode description
    if selected_mode == "qa":
        render_info_box(
            "Q&A Mode",
            "Ask any question and get instant answers from your course materials. Perfect for quick clarifications!",
            "💬"
        )
    elif selected_mode == "notes":
        render_info_box(
            "Study Notes Mode",
            "Generate comprehensive study notes on any topic. Includes key concepts, examples, and practice questions!",
            "📚"
        )
    else:
        render_info_box(
            "Practice Mode",
            "Get practice questions with answers. Includes MCQs, short answers, and conceptual questions!",
            "📝"
        )
    
    # Chat interface
    st.markdown("### 💬 Chat Interface")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            render_chat_message(message['content'], message['is_user'])
    
    # Chat input
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_area(
            "Your message:",
            height=100,
            placeholder="Type your question here... (e.g., 'Explain neural networks' or 'What is machine learning?')",
            key="chat_input"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        send_button = st.button("🚀 Send", use_container_width=True, type="primary")
    
    # Handle send
    if send_button and user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            'content': user_input,
            'is_user': True,
            'timestamp': datetime.now()
        })
        
        # Show processing
        with st.spinner("🤔 AI is thinking..."):
            try:
                # Get AI response
                if selected_mode == "qa":
                    result = asyncio.run(rag_engine.answer_query(user_input))
                elif selected_mode == "notes":
                    result = asyncio.run(rag_engine.generate_study_notes(user_input))
                else:
                    result = asyncio.run(rag_engine.generate_practice_questions(user_input))
                
                # Format response
                response = result['answer']
                sources = result.get('sources', [])
                
                if sources:
                    response += f"\n\n📚 **Sources:** {', '.join(sources)}"
                
                # Add AI response to history
                st.session_state.chat_history.append({
                    'content': response,
                    'is_user': False,
                    'timestamp': datetime.now()
                })
                
                # Log analytics
                analytics.log_chat_interaction(
                    st.session_state.user_id,
                    selected_mode
                )
                
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("💡 Tip: Make sure documents are uploaded and processed by faculty.")
    
    # Clear chat button
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()

with tab2:
    st.markdown("### 📊 Your Learning Statistics")
    
    try:
        stats = analytics.get_student_stats(st.session_state.user_id)
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Chat Sessions", stats['chat_sessions'])
        
        with col2:
            st.metric("Messages Sent", stats['messages_sent'])
        
        with col3:
            st.metric("Engagement Level", stats['engagement_level'].title())
        
        with col4:
            if stats['last_active']:
                st.metric("Last Active", stats['last_active'][:10])
        
        # Activity breakdown
        if stats['activity_breakdown']:
            st.markdown("### 📈 Activity Breakdown")
            
            import pandas as pd
            df = pd.DataFrame([
                {"Activity": k, "Count": v}
                for k, v in stats['activity_breakdown'].items()
            ])
            
            st.bar_chart(df.set_index('Activity'))
        
    except Exception as e:
        st.warning("No statistics available yet. Start chatting to see your stats!")

with tab3:
    st.markdown("""
    ### 📖 How to Use the Student Portal
    
    #### 🎯 Modes
    
    **1. Q&A Mode** 💬
    - Ask specific questions about your course material
    - Get instant, focused answers
    - Example: "What is supervised learning?"
    
    **2. Study Notes Mode** 📚
    - Request comprehensive notes on any topic
    - Includes key concepts, explanations, and examples
    - Example: "Create study notes on neural networks"
    
    **3. Practice Questions Mode** 📝
    - Generate practice questions with answers
    - Mix of MCQs, short answers, and conceptual questions
    - Example: "Give me practice questions on decision trees"
    
    #### 💡 Tips for Best Results
    
    1. **Be Specific**: Instead of "Tell me about AI", try "Explain the difference between supervised and unsupervised learning"
    
    2. **Use Context**: Reference specific topics or chapters
    
    3. **Follow Up**: Ask follow-up questions to dive deeper
    
    4. **Save Important Answers**: Download your chat history for later review
    
    5. **Try Different Modes**: Each mode gives different types of information
    
    #### 🚀 Getting Started
    
    1. Select your preferred mode from the sidebar
    2. Type your question in the input box
    3. Click "Send" and wait for AI response
    4. Continue the conversation or start a new session
    
    #### ⚠️ Important Notes
    
    - Responses are based on documents uploaded by faculty
    - If you get generic answers, faculty may need to upload more materials
    - Your chat history is saved during your session
    - Download important conversations before starting a new session
    """)

# Footer
st.markdown("---")
st.caption(f"Logged in as: {st.session_state.username} | Role: Student | Session: Active")