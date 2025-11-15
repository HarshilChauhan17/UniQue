"""
Database Service - FIXED VERSION
All database operations with proper error handling
"""
import sqlite3
import json
from typing import Dict, List, Optional
from datetime import datetime
import os
import uuid
import bcrypt
from config import DB_PATH

class Database:
    """Database manager with all CRUD operations"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._initialize_database()
        self._create_default_admin()
    
    def get_connection(self):
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _initialize_database(self):
        """Create all required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
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
        ''')
        
        # Chat sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Chat messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
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
        ''')
        
        # Generated content table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS generated_content (
                content_id TEXT PRIMARY KEY,
                content_type TEXT NOT NULL,
                faculty_id TEXT NOT NULL,
                document_ids TEXT,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (faculty_id) REFERENCES users(id)
            )
        ''')
        
        # Analytics events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _create_default_admin(self):
        """Create default admin user if not exists"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if admin exists
            cursor.execute("SELECT id FROM users WHERE username = 'admin'")
            if not cursor.fetchone():
                admin_id = str(uuid.uuid4())
                password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                cursor.execute('''
                    INSERT INTO users (id, username, password_hash, role, email)
                    VALUES (?, ?, ?, ?, ?)
                ''', (admin_id, 'admin', password_hash, 'admin', 'admin@college.edu'))
                
                conn.commit()
                print("✅ Default admin user created (username: admin, password: admin123)")
            
            conn.close()
        except Exception as e:
            print(f"Error creating default admin: {e}")

    # ==================== USER OPERATIONS ====================
    
    def create_user(self, username: str, password: str, role: str, email: str = None) -> Optional[str]:
        """Create a new user and return user ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        user_id = str(uuid.uuid4())
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        try:
            cursor.execute('''
                INSERT INTO users (id, username, password_hash, role, email)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, password_hash, role, email))
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, role, email, created_at FROM users ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def count_users(self) -> int:
        """Count total users"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    # ==================== DOCUMENT OPERATIONS ====================
    
    def create_document(self, doc_id: str, filename: str, file_path: str, 
                       uploaded_by: str, course_name: str = None, status: str = "queued"):
        """Create new document record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO documents (id, filename, file_path, uploaded_by, course_name, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (doc_id, filename, file_path, uploaded_by, course_name, status))
        conn.commit()
        conn.close()
    
    def update_document_status(self, doc_id: str, status: str, 
                              chunks_created: int = None, error_message: str = None):
        """Update document processing status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE documents 
            SET status = ?, chunks_created = ?, error_message = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, chunks_created, error_message, doc_id))
        conn.commit()
        conn.close()
    
    def get_document(self, doc_id: str) -> Optional[Dict]:
        """Get document by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM documents WHERE id = ?', (doc_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_documents_by_user(self, user_id: str) -> List[Dict]:
        """Get all documents uploaded by user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM documents WHERE uploaded_by = ? ORDER BY created_at DESC', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_all_documents(self) -> List[Dict]:
        """Get all documents"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM documents ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def delete_document(self, doc_id: str):
        """Delete document record"""
        conn = self.get_connection()  # ← FIXED (was self.get_.get_connection())
        cursor = conn.cursor()
        cursor.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
        conn.commit()
        conn.close()
    
    def count_documents(self) -> int:
        """Count total documents"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM documents')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    # ==================== CHAT OPERATIONS ====================
    
    def create_chat_session(self, session_id: str, user_id: str, title: str):
        """Create new chat session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO chat_sessions (session_id, user_id, title) VALUES (?, ?, ?)',
                      (session_id, user_id, title))
        conn.commit()
        conn.close()
    
    def store_chat_message(self, session_id: str, user_id: str, message_id: str,
                          query: str, response: str, sources: List[str]):
        """Store chat message"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Ensure session exists
        cursor.execute('SELECT session_id FROM chat_sessions WHERE session_id = ?', (session_id,))
        if not cursor.fetchone():
            self.create_chat_session(session_id, user_id, f"Session {datetime.now().strftime('%Y-%m-%d')}")
        
        cursor.execute('''
            INSERT INTO chat_messages (message_id, session_id, user_id, query, response, sources)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (message_id, session_id, user_id, query, response, json.dumps(sources)))
        conn.commit()
        conn.close()
    
    def get_chat_history(self, session_id: str) -> List[Dict]:
        """Get chat history for session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM chat_messages WHERE session_id = ? ORDER BY created_at ASC', (session_id,))
        rows = cursor.fetchall()
        conn.close()
        
        messages = []
        for row in rows:
            msg = dict(row)
            msg['sources'] = json.loads(msg['sources']) if msg['sources'] else []
            messages.append(msg)
        return messages
    
    def get_user_sessions(self, user_id: str) -> List[Dict]:
        """Get all chat sessions for user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM chat_sessions WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def count_sessions(self) -> int:
        """Count total chat sessions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM chat_sessions')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    # ==================== GENERATED CONTENT OPERATIONS ====================
    
    def store_generated_content(self, content_id: str, content_type: str, faculty_id: str,
                               document_ids: List[str], content: List[Dict]):
        """Store generated content (assignments, MCQs, viva questions)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO generated_content (content_id, content_type, faculty_id, document_ids, content)
            VALUES (?, ?, ?, ?, ?)
        ''', (content_id, content_type, faculty_id, json.dumps(document_ids), json.dumps(content)))
        conn.commit()
        conn.close()
    
    def get_generated_content_by_faculty(self, faculty_id: str) -> List[Dict]:
        """Get all generated content by faculty"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM generated_content WHERE faculty_id = ? ORDER BY created_at DESC', (faculty_id,))
        rows = cursor.fetchall()
        conn.close()
        
        contents = []
        for row in rows:
            content = dict(row)
            content['document_ids'] = json.loads(content['document_ids'])
            content['content'] = json.loads(content['content'])
            contents.append(content)
        return contents
    
    # ==================== ANALYTICS OPERATIONS ====================
    
    def log_event(self, user_id: str, event_type: str, event_data: Dict = None):
        """Log analytics event"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO analytics_events (user_id, event_type, event_data)
            VALUES (?, ?, ?)
        ''', (user_id, event_type, json.dumps(event_data) if event_data else None))
        conn.commit()
        conn.close()
    
    # ==================== SYSTEM OPERATIONS ====================
    
    def check_connection(self) -> str:
        """Check database connection"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            conn.close()
            return "operational"
        except:
            return "unavailable"
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        tables = ['users', 'documents', 'chat_sessions', 'chat_messages', 'generated_content', 'analytics_events']
        
        for table in tables:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            stats[table] = cursor.fetchone()[0]
        
        conn.close()
        return stats