import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any
import click
from dotenv import load_dotenv

load_dotenv()
class DatabaseManager:
    
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        if not self.db_url:
            click.echo(click.style("DATABASE_URL not set in .env file", err=True, fg='red'))
            sys.exit(1)

    def get_connection(self):
        """Get database connection"""
        try:
            return psycopg2.connect(self.db_url)
        except psycopg2.Error as e:
            click.echo(click.style(f"Database connection error: {e}", err=True, fg='red'))
            sys.exit(1)
    
    def store_domains(self, domains_data: Dict[str, Any]) -> int:
        """Store domains and flags"""
        stored_count = 0
        
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Store domains
                for domain in domains_data.get('domains', []):
                    try:
                        cur.execute("""
                            INSERT INTO domain (fqdn, registered_at, unregistered_at)
                            VALUES (%(fqdn)s, %(registered_at)s, %(unregistered_at)s)
                            ON CONFLICT (fqdn, registered_at) DO NOTHING
                            RETURNING id
                        """, domain)
                        
                        if cur.rowcount > 0:
                            click.echo(click.style(f"Stored domain: {domain['fqdn']}", fg='green'))
                            stored_count += 1
                        else:
                            click.echo(click.style(f"Already exists: {domain['fqdn']}", fg='red'))

                    except psycopg2.Error as e:
                        click.echo(click.style(f"Error storing {domain['fqdn']}: {e}", err=True, fg='red'))

                # Store flags
                for flag_data in domains_data.get('flags', []):
                    try:
                        # Get domain ID first
                        cur.execute(
                            "SELECT id FROM domain WHERE fqdn = %s ORDER BY registered_at DESC LIMIT 1",
                            (flag_data['domain_fqdn'],)
                        )
                        domain_result = cur.fetchone()
                        
                        if domain_result:
                            domain_id = domain_result[0]
                            cur.execute("""
                                INSERT INTO domain_flag (domain_id, flag, valid_from, valid_to)
                                VALUES (%s, %s, %s, %s)
                                ON CONFLICT DO NOTHING
                            """, (
                                domain_id,
                                flag_data['flag'],
                                flag_data['valid_from'],
                                flag_data['valid_to']
                            ))
                            
                            if cur.rowcount > 0:
                                click.echo(click.style(f"Stored flag: {flag_data['flag']} for {flag_data['domain_fqdn']}", fg='green'))

                    except psycopg2.Error as e:
                        click.echo(click.style(f"Error storing flag: {e}", err=True, fg='red'))

                conn.commit()
        
        return stored_count
    
    def get_active_domains(self) -> List[Dict[str, Any]]:
        """Get currently registered domains without EXPIRED flag"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
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
                """)
                return cur.fetchall()
    
    def get_flagged_domains(self) -> List[Dict[str, Any]]:
        """Get domains that have had both EXPIRED and OUTZONE flags"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT DISTINCT d.fqdn
                    FROM domain d
                    JOIN domain_flag df1 ON d.id = df1.domain_id
                    JOIN domain_flag df2 ON d.id = df2.domain_id
                    WHERE df1.flag = 'EXPIRED'
                      AND df2.flag = 'OUTZONE'
                    ORDER BY d.fqdn;
                """)
                return cur.fetchall()
    
    def get_system_stats(self) -> Dict:
        """Get system statistics"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Total domains
                cur.execute("SELECT COUNT(*) FROM domain")
                total_domains = cur.fetchone()[0]
                
                # Active domains
                cur.execute("SELECT COUNT(*) FROM domain WHERE unregistered_at IS NULL")
                active_domains = cur.fetchone()[0]
                
                # Total flags
                cur.execute("SELECT COUNT(*) FROM domain_flag")
                total_flags = cur.fetchone()[0]
                
                # Active flags
                cur.execute("SELECT COUNT(*) FROM domain_flag WHERE valid_to IS NULL")
                active_flags = cur.fetchone()[0]
                
                return {
                    'total_domains': total_domains,
                    'active_domains': active_domains,
                    'total_flags': total_flags,
                    'active_flags': active_flags
                }