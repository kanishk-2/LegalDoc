import sqlite3
import json
from datetime import datetime
from typing import List, Tuple, Optional

class Database:
    def __init__(self, db_path: str = "legal_documents.db"):
        """Initialize the database connection and create tables if they don't exist."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create the documents table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    upload_date TEXT NOT NULL,
                    content TEXT NOT NULL,
                    analysis TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def store_document(self, filename: str, content: str, analysis: dict, file_type: str) -> Optional[int]:
        """Store a document and its analysis in the database."""
        try:
            upload_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            analysis_json = json.dumps(analysis) if analysis else None
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO documents (filename, file_type, upload_date, content, analysis)
                    VALUES (?, ?, ?, ?, ?)
                """, (filename, file_type, upload_date, content, analysis_json))
                
                doc_id = cursor.lastrowid
                conn.commit()
                return doc_id
                
        except Exception as e:
            print(f"Error storing document: {e}")
            return None
    
    def get_all_documents(self) -> List[Tuple]:
        """Retrieve all documents from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, filename, file_type, upload_date, content, analysis
                    FROM documents
                    ORDER BY upload_date DESC
                """)
                return cursor.fetchall()
                
        except Exception as e:
            print(f"Error retrieving documents: {e}")
            return []
    
    def get_document_by_id(self, doc_id: int) -> Optional[Tuple]:
        """Retrieve a specific document by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, filename, file_type, upload_date, content, analysis
                    FROM documents
                    WHERE id = ?
                """, (doc_id,))
                return cursor.fetchone()
                
        except Exception as e:
            print(f"Error retrieving document {doc_id}: {e}")
            return None
    
    def delete_document(self, doc_id: int) -> bool:
        """Delete a document from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error deleting document {doc_id}: {e}")
            return False
    
    def search_documents(self, search_term: str) -> List[Tuple]:
        """Search documents by filename or content."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, filename, file_type, upload_date, content, analysis
                    FROM documents
                    WHERE filename LIKE ? OR content LIKE ?
                    ORDER BY upload_date DESC
                """, (f"%{search_term}%", f"%{search_term}%"))
                return cursor.fetchall()
                
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def get_document_stats(self) -> dict:
        """Get statistics about stored documents."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total documents
                cursor.execute("SELECT COUNT(*) FROM documents")
                total_docs = cursor.fetchone()[0]
                
                # Total content length
                cursor.execute("SELECT SUM(LENGTH(content)) FROM documents")
                total_content = cursor.fetchone()[0] or 0
                
                # File type distribution
                cursor.execute("""
                    SELECT file_type, COUNT(*) 
                    FROM documents 
                    GROUP BY file_type
                """)
                file_types = dict(cursor.fetchall())
                
                # Recent uploads (last 7 days)
                cursor.execute("""
                    SELECT COUNT(*) FROM documents 
                    WHERE upload_date >= date('now', '-7 days')
                """)
                recent_uploads = cursor.fetchone()[0]
                
                return {
                    "total_documents": total_docs,
                    "total_content_length": total_content,
                    "file_types": file_types,
                    "recent_uploads": recent_uploads
                }
                
        except Exception as e:
            print(f"Error getting document stats: {e}")
            return {}
    
    def cleanup_old_documents(self, days: int = 30) -> int:
        """Remove documents older than specified days."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM documents 
                    WHERE upload_date < date('now', '-{} days')
                """.format(days))
                deleted_count = cursor.rowcount
                conn.commit()
                return deleted_count
                
        except Exception as e:
            print(f"Error cleaning up old documents: {e}")
            return 0
