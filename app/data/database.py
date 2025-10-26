import sqlite3
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional
from app.core.config import settings
from app.core.models import MatchResult


class Database:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.database_path
        self._init_database()

    def _init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Match cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS match_cache (
                hash TEXT PRIMARY KEY,
                cv_content TEXT NOT NULL,
                job_content TEXT NOT NULL,
                result TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def _generate_hash(self, content: str) -> str:
        """Generate SHA256 hash for content"""
        return hashlib.sha256(content.encode()).hexdigest()

    def get_match(self, cv_content: str, job_content: str) -> Optional[MatchResult]:
        """Retrieve cached match result"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        match_hash = self._generate_hash(cv_content + job_content)
        cursor.execute(
            'SELECT result FROM match_cache WHERE hash = ?', (match_hash,))
        row = cursor.fetchone()
        conn.close()

        if row:
            data = json.loads(row[0])
            return MatchResult(**data)
        return None

    def cache_match(self, cv_content: str, job_content: str, match_result: MatchResult):
        """Cache match result"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        match_hash = self._generate_hash(cv_content + job_content)
        cursor.execute(
            'INSERT OR REPLACE INTO match_cache (hash, cv_content, job_content, result) VALUES (?, ?, ?, ?)',
            (match_hash, cv_content, job_content,
             json.dumps(match_result.model_dump()))
        )

        conn.commit()
        conn.close()

    def cleanup_old_cache(self):
        """Remove cache entries older than TTL"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff = datetime.now() - timedelta(hours=settings.cache_ttl_hours)

        cursor.execute(
            'DELETE FROM match_cache WHERE created_at < ?', (cutoff,))

        conn.commit()
        conn.close()


# Global database instance
db = Database()
