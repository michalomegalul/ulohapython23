# import click
# import psycopg2
# import requests
# import logging
# import sys
# import uuid as uuid_lib
# from datetime import datetime
# from typing import List, Dict
# import os

# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S'
# )
# logger = logging.getLogger(__name__)


# class DatabaseManager:
#     """Database manager for domain operations"""
    
#     def __init__(self):
#         self.connection_string = os.getenv('DATABASE_URL', '')
#         logger.debug("Database connection initialized")
    
#     def get_connection(self):
#         """Get database connection"""
#         return psycopg2.connect(self.connection_string)
    
#     def get_active_domains(self) -> List[str]:
#         """Get domains that are registered and dont have active EXPIRED flag"""
#         logger.debug("Fetching active domains")
#         query = """
#         SELECT d.fqdn
#         FROM domain d
#         WHERE d.unregistered_at IS NULL
#           AND d.id NOT IN (
#             SELECT df.domain_id 
#             FROM domain_flag df 
#             WHERE df.flag = 'EXPIRED' 
#                 AND df.valid_to IS NULL
#           )
#         ORDER BY d.fqdn;
#         """
        
#         with self.get_connection() as conn:
#             with conn.cursor() as cur:
#                 cur.execute(query)
#                 results = [row[0] for row in cur.fetchall()]
#                 logger.info("Found {len(results)} active domains")
#                 return results
    
#     def get_flagged_domains(self) -> List[str]:
#         """Get domains that had both EXPIRED and OUTZONE flags"""
#         logger.debug("Fetching flagged domains")
#         query = """
#         SELECT DISTINCT d.fqdn
#         FROM domain d
#         JOIN domain_flag df1 ON d.id = df1.domain_id
#         JOIN domain_flag df2 ON d.id = df2.domain_id
#         WHERE df1.flag = 'EXPIRED'
#           AND df2.flag = 'OUTZONE'
#         ORDER BY d.fqdn;
#         """
        
#         with self.get_connection() as conn:
#             with conn.cursor() as cur:
#                 cur.execute(query)
#                 results = [row[0] for row in cur.fetchall()]
#                 logger.info("Found {len(results)} flagged domains")
#                 return results
    
#     def get_stats(self) -> Dict[str, int]:
#         """Get database statistics"""
#         logger.debug("Fetching database stats")
#         with self.get_connection() as conn:
#             with conn.cursor() as cur:
#                 cur.execute("SELECT COUNT(*) FROM domain")
#                 total_domains = cur.fetchone()[0]
                
#                 cur.execute("SELECT COUNT(*) FROM domain WHERE unregistered_at IS NULL")
#                 active_domains = cur.fetchone()[0]
                
#                 cur.execute("SELECT COUNT(*) FROM domain_flag")
#                 total_flags = cur.fetchone()[0]
                
#                 stats = {
#                     'total_domains': total_domains,
#                     'active_domains': active_domains,
#                     'total_flags': total_flags
#                 }
#                 logger.info("Database stats: {stats}")
#                 return stats


# def validate_uuid(uuid_str):
#     """Validate UUID format"""
#     try:
#         uuid_lib.UUID(uuid_str)
#         return True
#     except ValueError:
#         return False


# def stat_rest(uuid, base_url, output):
#     """Get file metadata via REST API"""
#     try:
#         url = "{base_url.rstrip('/')}/file/{uuid}/stat/"
#         logger.debug("Making stat request to: {url}")
#         response = requests.get(url, timeout=30)
        
#         if response.status_code == 404:
#             click.echo("File not found", err=True)
#             sys.exit(1)
        
#         response.raise_for_status()
#         data = response.json()
        
#         # Format as human-readable text (as per assignment)
#         output_text = f"""Name: {data.get('name', 'Unknown')}
#                          Size: {data.get('size', 0)} bytes
#                          MIME Type: {data.get('mimetype', 'Unknown')}
#                          Created: {data.get('create_datetime', 'Unknown')}"""
        
#         if output == '-':
#             click.echo(output_text)
#         else:
#             with open(output, 'w') as f:
#                 f.write(output_text)
#             logger.info("Metadata saved to {output}")
        
#     except requests.RequestException as e:
#         logger.error("Request failed: {e}")
#         click.echo("Error: {e}", err=True)
#         sys.exit(1)



# # CLI Commands
