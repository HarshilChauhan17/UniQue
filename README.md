# 🎓 College AI Portal - Project Report

## Executive Summary

The **College AI Portal** is a comprehensive, multi-user, role-based web application built with Streamlit that leverages Artificial Intelligence and Retrieval-Augmented Generation (RAG) technology to transform educational workflows. The platform serves three distinct user roles—Students, Faculty, and Administrators—each with tailored functionalities designed to enhance learning, teaching, and administrative management.

**Repository:** [https://github.com/AXJOD/UniQue-Final.git](https://github.com/AXJOD/UniQue-Final.git)

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Design](#architecture--design)
3. [Features by Role](#features-by-role)
4. [Technical Stack](#technical-stack)
5. [Project Structure](#project-structure)
6. [Core Services & Modules](#core-services--modules)
7. [Database Schema](#database-schema)
8. [Setup & Installation](#setup--installation)
9. [Usage Guide](#usage-guide)
10. [System Requirements](#system-requirements)
11. [Security Features](#security-features)
12. [Future Enhancements](#future-enhancements)

---

## 🎯 Project Overview

### Purpose
The College AI Portal addresses the growing need for intelligent educational tools that can:
- Provide personalized learning experiences for students
- Automate content generation for faculty
- Offer comprehensive analytics for administrators

### Key Capabilities
- **AI-Powered Document Processing**: Automatically extracts, chunks, and indexes PDF documents into a vector database
- **RAG-Based Q&A System**: Enables students to ask questions and receive context-aware answers from course materials
- **Automated Content Generation**: Faculty can generate assignments, MCQs, and viva questions from uploaded documents
- **Comprehensive Analytics**: Track user engagement, document usage, and system performance

---

## 🏗️ Architecture & Design

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Student    │  │   Faculty    │  │    Admin     │     │
│  │    Portal    │  │    Portal     │  │  Dashboard   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   RAG Engine │  │   Document    │  │   Question   │     │
│  │              │  │   Processor   │  │   Generator  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐                       │
│  │   Analytics  │  │   Database    │                       │
│  │   Service    │  │   Service    │                       │
│  └──────────────┘  └──────────────┘                       │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        ▼                                       ▼
┌──────────────┐                      ┌──────────────┐
│   SQLite     │                      │   ChromaDB    │
│   Database   │                      │  Vector Store │
└──────────────┘                      └──────────────┘
        │                                       │
        └───────────────────┬───────────────────┘
                            ▼
                    ┌──────────────┐
                    │  HuggingFace │
                    │     LLM      │
                    └──────────────┘
```

### Design Patterns
- **MVC-like Architecture**: Separation of concerns with services, pages, and utilities
- **Singleton Services**: Cached resource initialization for performance
- **Async/Await**: Asynchronous processing for AI operations
- **Role-Based Access Control (RBAC)**: Secure authentication and authorization

---

## 👥 Features by Role

### 🎓 Student Portal

#### Core Features
1. **AI Chatbot Interface**
   - Three interaction modes:
     - **Q&A Mode**: Quick question-answering from course materials
     - **Study Notes Mode**: Comprehensive study notes with key concepts, examples, and practice questions
     - **Practice Questions Mode**: Mixed question types (MCQ, short answer, conceptual)

2. **Session Management**
   - Create new chat sessions
   - Download chat history
   - View conversation history

3. **Personal Statistics**
   - Track chat interactions
   - Monitor learning progress
   - View usage analytics

#### Technical Implementation
- Uses RAG engine with similarity search (k=5-7 chunks)
- Context-aware responses from uploaded documents
- Source citation for answers
- Real-time streaming responses

### 👨‍🏫 Faculty Portal

#### Core Features
1. **Document Management**
   - Upload PDF course materials
   - Automatic text extraction and chunking
   - Document status tracking (queued, processing, completed, failed)
   - View all uploaded documents
   - Delete documents

2. **Content Generation**
   - **Assignment Generator**: Create structured assignments with:
     - Multiple question types (theory, numerical, analytical, application)
     - Marking schemes
     - Sample answers
   - **MCQ Generator**: Generate multiple-choice questions with:
     - 4 options per question
     - Correct answer identification
     - Explanation for each answer
   - **Viva Questions Generator**: Create oral examination questions with:
     - Topic-based questions
     - Expected answer outlines

3. **Document Analytics**
   - View processing statistics
   - Track document usage
   - Monitor generation history

#### Technical Implementation
- PDF processing using PyPDF2 and pypdf
- Text chunking with RecursiveCharacterTextSplitter (1000 chars, 200 overlap)
- Vector embeddings using sentence-transformers
- ChromaDB for vector storage
- LLM-based content generation with structured prompts

### 👨‍💼 Admin Dashboard

#### Core Features
1. **System Overview**
   - Real-time system metrics
   - Platform statistics
   - Health monitoring

2. **User Management**
   - View all users
   - Create new users (students, faculty, admin)
   - Delete users
   - User role management

3. **Document Management**
   - View all documents across the platform
   - Monitor document processing status
   - System-wide document statistics

4. **Analytics & Reporting**
   - User engagement metrics
   - Document usage statistics
   - Chat session analytics
   - Storage usage monitoring
   - Active user tracking

#### Technical Implementation
- Comprehensive database queries
- Real-time statistics calculation
- Event logging and tracking
- Data visualization with Plotly

---

## 🛠️ Technical Stack

### Frontend
- **Streamlit 1.38.0**: Web application framework
- **Streamlit Option Menu**: Enhanced UI components
- **Custom CSS**: Styled components and animations

### Backend & AI
- **Python 3.x**: Core programming language
- **LangChain 0.3.0**: LLM orchestration framework
- **LangChain Community**: Community integrations
- **LangChain HuggingFace**: HuggingFace integration
- **HuggingFace Transformers**: Pre-trained models
- **Sentence Transformers 2.6.0**: Embedding generation

### Vector Database & Storage
- **ChromaDB 0.5.0**: Vector database for embeddings
- **SQLite**: Relational database for user data and metadata

### Document Processing
- **PyPDF2 3.0.1**: PDF text extraction
- **pypdf 3.17.0**: Alternative PDF processing
- **LangChain Text Splitters**: Document chunking

### Data & Visualization
- **Pandas 2.1.4**: Data manipulation
- **Plotly 5.18.0**: Interactive visualizations

### Security & Authentication
- **bcrypt 4.1.1**: Password hashing
- **python-dotenv 1.0.0**: Environment variable management

### Utilities
- **Requests 2.31.0**: HTTP operations
- **Pydantic ≥2.7.4**: Data validation

---

## 📂 Project Structure

```
UniQue-Final/
├── Minor/                          # Main application directory
│   ├── app.py                      # Main Streamlit entry point
│   ├── config.py                   # Configuration and paths
│   ├── requirements.txt            # Python dependencies
│   │
│   ├── pages/                      # Role-based portals
│   │   ├── 1_👤_Login.py          # Authentication page
│   │   ├── 2_👨‍💼_Admin_Dashboard.py    # Admin interface
│   │   ├── 3_👨‍🏫_Faculty_Portal.py     # Faculty interface
│   │   └── 4_👨‍🎓_Student_Portal.py     # Student interface
│   │
│   ├── services/                   # Core business logic
│   │   ├── __init__.py
│   │   ├── rag_engine.py           # RAG implementation
│   │   ├── document_processor.py   # PDF processing
│   │   ├── question_generator.py   # Content generation
│   │   ├── database.py             # Database operations
│   │   └── analytics.py            # Analytics service
│   │
│   ├── utils/                      # Utility functions
│   │   ├── __init__.py
│   │   ├── auth.py                 # Authentication utilities
│   │   ├── session.py              # Session management
│   │   └── ui_components.py        # Reusable UI components
│   │
│   ├── components/                 # UI assets
│   │   └── assets/
│   │       ├── logo.png
│   │       └── styles.css
│   │
│   └── data/                       # Data storage
│       ├── chroma/                 # ChromaDB vector stores
│       ├── uploads/                # Uploaded PDF files
│       └── college_ai.db          # SQLite database
│
├── venv/                          # Virtual environment (not in repo)
└── README.md                      # This file
```

---

## 🔧 Core Services & Modules

### 1. RAG Engine (`services/rag_engine.py`)

**Purpose**: Retrieval-Augmented Generation for student queries

**Key Methods**:
- `answer_query(query)`: Standard Q&A mode
- `generate_study_notes(topic)`: Comprehensive study notes
- `generate_practice_questions(topic)`: Practice question sets
- `get_documents_context(document_ids)`: Retrieve specific document content

**Configuration**:
- Embedding Model: `sentence-transformers/all-MiniLM-L6-v2`
- LLM Model: `mistralai/Mistral-7B-Instruct-v0.2`
- Retrieval: Similarity search with k=5-7 chunks
- Temperature: 0.3 (for consistent responses)

### 2. Document Processor (`services/document_processor.py`)

**Purpose**: PDF processing and vectorization

**Workflow**:
1. Extract text from PDF using PyPDF
2. Split text into chunks (1000 chars, 200 overlap)
3. Generate embeddings using HuggingFace embeddings
4. Store in ChromaDB with metadata

**Features**:
- Automatic text extraction
- Intelligent chunking
- Metadata preservation (doc_id, filename, uploaded_by)
- Error handling for corrupted PDFs

### 3. Question Generator (`services/question_generator.py`)

**Purpose**: Automated content generation for faculty

**Capabilities**:
- **Assignment Generation**: Structured questions with marking schemes
- **MCQ Generation**: Multiple-choice questions with explanations
- **Viva Questions**: Oral examination questions

**Configuration**:
- LLM Model: `mistralai/Mistral-7B-Instruct-v0.2`
- Temperature: 0.5 (for creative generation)
- Max Tokens: 2048

### 4. Database Service (`services/database.py`)

**Purpose**: Centralized database operations

**Tables**:
- `users`: User accounts and authentication
- `documents`: Document metadata and status
- `chat_sessions`: Student chat sessions
- `chat_messages`: Individual chat messages
- `generated_content`: Faculty-generated content
- `analytics_events`: System events and analytics

**Features**:
- Automatic table creation
- Default admin user creation
- Comprehensive CRUD operations
- Transaction support

### 5. Analytics Service (`services/analytics.py`)

**Purpose**: Track and analyze platform usage

**Metrics Tracked**:
- Document processing events
- Chat interactions
- Content generation
- Admin actions
- User activity
- Storage usage

**Reports**:
- Platform statistics
- User engagement metrics
- Document analytics
- Chat session statistics

---

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Documents Table
```sql
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    uploaded_by TEXT NOT NULL,
    course_name TEXT,
    status TEXT DEFAULT 'queued',
    chunks_created INTEGER,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uploaded_by) REFERENCES users(id)
)
```

### Chat Sessions Table
```sql
CREATE TABLE chat_sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
```

### Chat Messages Table
```sql
CREATE TABLE chat_messages (
    message_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    sources TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id),
    FOREIGN KEY (user_id) REFERENCES users(id)
)
```

### Generated Content Table
```sql
CREATE TABLE generated_content (
    content_id TEXT PRIMARY KEY,
    content_type TEXT NOT NULL,
    faculty_id TEXT NOT NULL,
    document_ids TEXT,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (faculty_id) REFERENCES users(id)
)
```

### Analytics Events Table
```sql
CREATE TABLE analytics_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_data TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
```

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- HuggingFace account with API token

### Step-by-Step Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/AXJOD/UniQue-Final.git
   cd UniQue-Final/Minor
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   ```

3. **Activate Virtual Environment**
   - **Windows**:
     ```bash
     .\venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set Up Environment Variables**
   - Create a `.env` file in the `Minor` directory
   - Add your HuggingFace API token:
     ```
     HUGGINGFACEHUB_API_TOKEN="your_hf_token_here"
     ```
   - Get your token from: https://huggingface.co/settings/tokens

6. **Initialize Database**
   - The database will be automatically created on first run
   - Default admin credentials:
     - Username: `admin`
     - Password: `admin123`

7. **Run the Application**
   ```bash
   streamlit run app.py
   ```

8. **Access the Application**
   - Open your browser and navigate to: `http://localhost:8501`

---

## 📖 Usage Guide

### For Students

1. **Sign Up/Login**
   - Create an account with role "student"
   - Or login with existing credentials

2. **Access Student Portal**
   - Navigate to Student Portal from sidebar
   - Select interaction mode (Q&A, Study Notes, or Practice Questions)

3. **Interact with AI**
   - Enter your question or topic
   - Wait for AI response
   - View sources and citations
   - Download chat history if needed

### For Faculty

1. **Sign Up/Login**
   - Create an account with role "faculty"
   - Or login with existing credentials

2. **Upload Documents**
   - Go to "Upload Documents" tab
   - Select PDF file
   - Enter course name
   - Click "Upload & Process"
   - Wait for processing completion

3. **Generate Content**
   - Go to "Generate Content" tab
   - Select document(s)
   - Choose content type (Assignment, MCQ, or Viva)
   - Configure parameters
   - Generate and review content

4. **Manage Documents**
   - View all uploaded documents
   - Check processing status
   - Delete documents if needed

### For Administrators

1. **Login**
   - Use admin credentials (default: admin/admin123)
   - Access Admin Dashboard

2. **Monitor System**
   - View system overview
   - Check platform statistics
   - Monitor user activity

3. **Manage Users**
   - View all users
   - Create new users
   - Delete users
   - Assign roles

4. **View Analytics**
   - Platform usage statistics
   - Document analytics
   - Chat session metrics
   - Storage usage

---

## 💻 System Requirements

### Minimum Requirements
- **OS**: Windows 10+, macOS 10.14+, or Linux
- **RAM**: 4GB (8GB recommended)
- **Storage**: 2GB free space
- **Python**: 3.8 or higher
- **Internet**: Required for HuggingFace API access

### Recommended Requirements
- **RAM**: 8GB or more
- **Storage**: 5GB free space (for vector database)
- **CPU**: Multi-core processor
- **Internet**: Stable connection for API calls

---

## 🔒 Security Features

### Authentication & Authorization
- **Password Hashing**: bcrypt with salt
- **Role-Based Access Control**: Separate portals for each role
- **Session Management**: Secure session state handling
- **Input Validation**: Form validation and sanitization

### Data Security
- **SQL Injection Prevention**: Parameterized queries
- **File Upload Validation**: PDF-only uploads with size limits
- **Environment Variables**: Sensitive data in .env file
- **Database Encryption**: SQLite with proper access controls

### Best Practices
- Default admin password should be changed
- Regular security updates
- API token protection
- Secure file storage

---

## 🔮 Future Enhancements

### Planned Features
1. **Multi-language Support**
   - Support for multiple languages in documents
   - Translation capabilities

2. **Advanced Analytics**
   - Machine learning-based insights
   - Predictive analytics
   - Custom report generation

3. **Collaboration Features**
   - Shared document libraries
   - Faculty-student collaboration
   - Discussion forums

4. **Mobile Application**
   - Native mobile apps
   - Offline capabilities
   - Push notifications

5. **Enhanced AI Capabilities**
   - Multi-modal support (images, audio)
   - Advanced question types
   - Personalized learning paths

6. **Integration Features**
   - LMS integration (Moodle, Canvas)
   - Calendar integration
   - Email notifications

7. **Performance Optimizations**
   - Caching mechanisms
   - Background job processing
   - CDN for static assets

8. **Accessibility**
   - Screen reader support
   - Keyboard navigation
   - High contrast mode

---

## 📊 Project Statistics

### Code Metrics
- **Total Python Files**: ~15
- **Lines of Code**: ~3000+
- **Services**: 5 core services
- **Pages**: 4 role-based portals
- **Database Tables**: 6 tables

### Technology Distribution
- **Frontend**: Streamlit (100%)
- **Backend**: Python
- **AI/ML**: LangChain, HuggingFace
- **Database**: SQLite, ChromaDB
- **Document Processing**: PyPDF2, pypdf

---

## 🤝 Contributing

This is a private repository. For contributions or issues, please contact the repository maintainers.

---

## 📝 License

This project is part of an educational initiative. Please refer to the repository for license information.

---

## 📧 Contact & Support

- **Repository**: [https://github.com/AXJOD/UniQue-Final.git](https://github.com/AXJOD/UniQue-Final.git)
- **Issues**: Please use GitHub Issues for bug reports and feature requests

---

## ✅ Conclusion

The College AI Portal represents a comprehensive solution for modern educational institutions, combining the power of AI with intuitive user interfaces. The platform successfully addresses the needs of students, faculty, and administrators through role-based access, intelligent document processing, and automated content generation.

The architecture is scalable, maintainable, and follows best practices in software development. With continued development and enhancement, this platform has the potential to significantly transform educational workflows and improve learning outcomes.

---

**Last Updated**: January 2025  
**Version**: 1.0  
**Status**: Active Development

