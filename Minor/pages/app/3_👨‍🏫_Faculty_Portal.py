"""
Faculty Portal - Document Upload & Content Generation
"""

import streamlit as st
import asyncio
import time
from datetime import datetime
from utils.ui_components import (
    check_authentication, render_document_card,
    render_question_card, render_progress_bar, render_info_box
)
from services.document_processor import DocumentProcessor
from services.question_generator import QuestionGenerator
from services.rag_engine import RAGEngine
from services.database import Database
from services.analytics import AnalyticsService
from config import UPLOADS_DIR

# Page config
st.set_page_config(
    page_title="Faculty Portal",
    page_icon="👨‍🏫",
    layout="wide"
)

# Check authentication
check_authentication()

# Initialize services
@st.cache_resource
def init_services():
    return (
        DocumentProcessor(),
        QuestionGenerator(),
        RAGEngine(),
        Database(),
        AnalyticsService()
    )

doc_processor, question_gen, rag_engine, db, analytics = init_services()

# Page header
st.markdown("# 👨‍🏫 Faculty Portal")
st.markdown("### Document Management & Content Generation")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📤 Upload Documents",
    "📚 My Documents",
    "✏️ Generate Content",
    "📊 My Stats"
])

with tab1:
    st.markdown("### 📤 Upload Course Materials")
    
    render_info_box(
        "Document Upload",
        "Upload PDF files containing your course materials. The system will automatically process and index them for student queries.",
        "📄"
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload course notes, textbooks, or any educational PDF"
        )
        
        course_name = st.text_input(
            "Course Name",
            placeholder="e.g., Data Mining, Machine Learning"
        )
    
    with col2:
        st.markdown("### ℹ️ Upload Guidelines")
        st.markdown("""
        - Max file size: 50MB
        - Format: PDF only
        - Clear, readable text
        - Properly formatted content
        """)
    
    if st.button("🚀 Upload & Process", type="primary", use_container_width=True):
        if uploaded_file and course_name:
            with st.spinner("📤 Uploading and processing document..."):
                try:
                    # Save uploaded file
                    import os
                    import uuid
                    
                    doc_id = str(uuid.uuid4())
                    upload_dir = UPLOADS_DIR
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    file_path = os.path.join(upload_dir, f"{doc_id}_{uploaded_file.name}")
                    
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Save to database
                    db.create_document(
                        doc_id=doc_id,
                        filename=uploaded_file.name,
                        file_path=file_path,
                        uploaded_by=st.session_state.user_id,
                        course_name=course_name,
                        status="processing"
                    )
                    
                    # Process document
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("📄 Extracting text from PDF...")
                    progress_bar.progress(25)
                    
                    result = asyncio.run(doc_processor.process_pdf(
                        file_path=file_path,
                        doc_id=doc_id,
                        filename=uploaded_file.name,
                        uploaded_by=st.session_state.user_id
                    ))
                    
                    status_text.text("✂️ Splitting into chunks...")
                    progress_bar.progress(50)
                    time.sleep(0.5)
                    
                    status_text.text("🧠 Generating embeddings...")
                    progress_bar.progress(75)
                    time.sleep(0.5)
                    
                    # Update database
                    db.update_document_status(
                        doc_id,
                        "completed",
                        chunks_created=result['chunks_created']
                    )
                    
                    status_text.text("✅ Storing in vector database...")
                    progress_bar.progress(100)
                    
                    # Log analytics
                    analytics.log_document_processed(
                        st.session_state.user_id,
                        doc_id,
                        result['chunks_created']
                    )
                    
                    st.success(f"""
                    ✅ **Document processed successfully!**
                    - Filename: {uploaded_file.name}
                    - Chunks created: {result['chunks_created']}
                    - Status: Ready for student queries
                    """)
                    
                    time.sleep(2)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Processing failed: {str(e)}")
                    db.update_document_status(doc_id, "failed", error_message=str(e))
        else:
            st.warning("⚠️ Please upload a file and enter course name")

with tab2:
    st.markdown("### 📚 My Uploaded Documents")
    
    # Fetch user's documents
    documents = db.get_documents_by_user(st.session_state.user_id)
    
    if documents:
        st.info(f"📊 Total documents: {len(documents)}")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            filter_status = st.selectbox(
                "Filter by status:",
                ["All", "completed", "processing", "queued", "failed"]
            )
        
        # Display documents
        filtered_docs = documents if filter_status == "All" else [
            d for d in documents if d['status'] == filter_status
        ]
        
        for doc in filtered_docs:
            with st.expander(f"📄 {doc['filename']}", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"**Status:** {doc['status']}")
                    st.markdown(f"**Course:** {doc['course_name'] or 'N/A'}")
                
                with col2:
                    st.markdown(f"**Uploaded:** {doc['created_at'][:10]}")
                    if doc['chunks_created']:
                        st.markdown(f"**Chunks:** {doc['chunks_created']}")
                
                with col3:
                    if doc['status'] == 'failed':
                        st.error(f"Error: {doc['error_message']}")
                    
                    if st.button(f"🗑️ Delete", key=f"del_{doc['id']}"):
                        db.delete_document(doc['id'])
                        st.success("Document deleted!")
                        st.rerun()
    else:
        st.info("📭 No documents uploaded yet. Upload your first document above!")

with tab3:
    st.markdown("### ✏️ Generate Assessment Content")
    
    # Get completed documents
    completed_docs = [d for d in db.get_documents_by_user(st.session_state.user_id) 
                     if d['status'] == 'completed']
    
    if not completed_docs:
        st.warning("⚠️ No processed documents available. Please upload and process documents first.")
    else:
        # Document selection
        st.markdown("#### 1️⃣ Select Documents")
        selected_docs = st.multiselect(
            "Choose documents to generate content from:",
            options=[d['id'] for d in completed_docs],
            format_func=lambda x: next(d['filename'] for d in completed_docs if d['id'] == x)
        )
        
        if selected_docs:
            # Generation type
            st.markdown("#### 2️⃣ Select Content Type")
            
            gen_type = st.radio(
                "What would you like to generate?",
                ["📝 Assignment Questions", "☑️ Multiple Choice Questions (MCQs)", "🎤 Viva Questions"]
            )
            
            # Configuration
            st.markdown("#### 3️⃣ Configure Generation")
            
            col1, col2 = st.columns(2)
            
            with col1:
                num_questions = st.slider("Number of questions:", 1, 20, 5)
            
            with col2:
                if "MCQ" not in gen_type:
                    difficulty = st.select_slider(
                        "Difficulty level:",
                        options=["easy", "medium", "hard"]
                    )
                else:
                    difficulty = st.select_slider(
                        "Difficulty level:",
                        options=["easy", "medium", "hard"]
                    )
            
            # Generate button
            if st.button("🎯 Generate Content", type="primary", use_container_width=True):
                with st.spinner("🤖 AI is generating content..."):
                    try:
                        # Get context from selected documents
                        context = asyncio.run(rag_engine.get_documents_context(selected_docs))
                        
                        # Generate based on type
                        if "Assignment" in gen_type:
                            questions = asyncio.run(question_gen.generate_assignment(
                                context=context,
                                num_questions=num_questions,
                                difficulty=difficulty
                            ))
                            content_type = "assignment"
                        
                        elif "MCQ" in gen_type:
                            questions = asyncio.run(question_gen.generate_mcqs(
                                context=context,
                                num_questions=num_questions,
                                difficulty=difficulty
                            ))
                            content_type = "mcq"
                        
                        else:  # Viva
                            questions = asyncio.run(question_gen.generate_viva_questions(
                                context=context,
                                num_questions=num_questions
                            ))
                            content_type = "viva"
                        
                        # Store generated content
                        import uuid
                        content_id = str(uuid.uuid4())
                        
                        db.store_generated_content(
                            content_id=content_id,
                            content_type=content_type,
                            faculty_id=st.session_state.user_id,
                            document_ids=selected_docs,
                            content=questions
                        )
                        
                        # Log analytics
                        analytics.log_content_generation(
                            st.session_state.user_id,
                            content_type,
                            len(questions)
                        )
                        
                        st.success(f"✅ Generated {len(questions)} questions successfully!")
                        
                        # Display questions
                        st.markdown("### 📋 Generated Questions")
                        
                        for i, question in enumerate(questions):
                            render_question_card(question, i)
                        
                        # Download option
                        import json
                        questions_json = json.dumps(questions, indent=2)
                        
                        st.download_button(
                            "📥 Download Questions (JSON)",
                            questions_json,
                            file_name=f"{content_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                        
                    except Exception as e:
                        st.error(f"❌ Generation failed: {str(e)}")

with tab4:
    st.markdown("### 📊 My Statistics")
    
    try:
        stats = analytics.get_faculty_stats(st.session_state.user_id)
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Documents Uploaded", stats['documents_uploaded'])
        
        with col2:
            st.metric("Content Generated", stats['total_items_generated'])
        
        with col3:
            total_content = sum(stats['content_generated'].values())
            st.metric("Total Items", total_content)
        
        # Content breakdown
        if stats['content_generated']:
            st.markdown("### 📈 Generated Content Breakdown")
            
            import pandas as pd
            df = pd.DataFrame([
                {"Type": k.upper(), "Count": v}
                for k, v in stats['content_generated'].items()
            ])
            
            st.bar_chart(df.set_index('Type'))
        
        # Recent uploads
        if stats['recent_uploads']:
            st.markdown("### 📚 Recent Uploads")
            
            for upload in stats['recent_uploads']:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.text(upload['filename'])
                with col2:
                    st.text(upload['uploaded_at'][:10])
                with col3:
                    status_color = "🟢" if upload['status'] == 'completed' else "🟡"
                    st.text(f"{status_color} {upload['status']}")
        
    except Exception as e:
        st.warning("No statistics available yet.")

# Footer
st.markdown("---")
st.caption(f"Logged in as: {st.session_state.username} | Role: Faculty | Session: Active")