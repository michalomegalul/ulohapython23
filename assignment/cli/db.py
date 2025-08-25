import os
import psycopg2
from typing import List, Dict
from .errors import handle_error
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager for domain operations"""

    def __init__(self):
        self.connection_string = os.getenv("DATABASE_URL")
        if not self.connection_string:
            handle_error("DATABASE_URL environment variable not set")

    def get_connection(self):
        try:
            return psycopg2.connect(self.connection_string)
        except Exception as e:
            handle_error(f"Cannot connect to DB: {e}")

    def get_active_domains(self) -> List[str]:
        query = """
        SELECT d.fqdn
        FROM domain d
        WHERE d.unregistered_at IS NULL
          AND d.id NOT IN (
            SELECT df.domain_id 
            FROM domain_flag df 
            WHERE df.flag = 'EXPIRED' 
              AND df.valid_to IS NULL
          )
        ORDER BY d.fqdn;
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    return [row[0] for row in cur.fetchall()]
        except Exception as e:
            handle_error(f"Failed to fetch active domains: {e}")

    def get_flagged_domains(self) -> List[str]:
        query = """
        SELECT DISTINCT d.fqdn
        FROM domain d
        JOIN domain_flag df1 ON d.id = df1.domain_id
        JOIN domain_flag df2 ON d.id = df2.domain_id
        WHERE df1.flag = 'EXPIRED'
          AND df2.flag = 'OUTZONE'
        ORDER BY d.fqdn;
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    return [row[0] for row in cur.fetchall()]
        except Exception as e:
            handle_error(f"Failed to fetch flagged domains: {e}")

    def get_stats(self) -> Dict[str, int]:
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) FROM domain")
                    total = cur.fetchone()[0]
                    cur.execute("SELECT COUNT(*) FROM domain WHERE unregistered_at IS NULL")
                    active = cur.fetchone()[0]
                    cur.execute("SELECT COUNT(*) FROM domain_flag")
                    flags = cur.fetchone()[0]
                    return {"total_domains": total, "active_domains": active, "total_flags": flags}
        except Exception as e:
            handle_error(f"Failed to fetch database stats: {e}")
