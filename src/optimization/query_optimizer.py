from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Tuple
import logging
from ..utils.monitoring import MonitoringService

class QueryOptimizer:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        self.monitoring = MonitoringService()
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Initialize logger for query optimization"""
        logger = logging.getLogger('query_optimizer')
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler('query_optimizer.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def analyze_query(self, query: str) -> Dict:
        """Analyze query performance"""
        try:
            with self.engine.connect() as conn:
                # Get query plan
                explain_query = f"EXPLAIN ANALYZE {query}"
                result = conn.execute(text(explain_query))
                plan = [row[0] for row in result]

                # Parse the query plan
                analysis = self._parse_query_plan(plan)
                
                # Record metrics
                self.monitoring.record_metric('query_analysis', 1)
                
                return analysis
        except Exception as e:
            self.logger.error(f'Query analysis failed: {str(e)}')
            self.monitoring.record_error('query_analysis', str(e))
            return {}

    def _parse_query_plan(self, plan: List[str]) -> Dict:
        """Parse PostgreSQL query plan"""
        analysis = {
            'execution_time': None,
            'planning_time': None,
            'table_scans': [],
            'index_usage': [],
            'recommendations': []
        }

        for line in plan:
            # Extract execution time
            if 'Execution Time:' in line:
                analysis['execution_time'] = float(line.split(':')[1].strip().split(' ')[0])
            
            # Extract planning time
            elif 'Planning Time:' in line:
                analysis['planning_time'] = float(line.split(':')[1].strip().split(' ')[0])
            
            # Check for sequential scans
            elif 'Seq Scan' in line:
                table = line.split('on')[1].split()[0]
                analysis['table_scans'].append(table)
                analysis['recommendations'].append(
                    f"Consider adding an index on table '{table}'"
                )
            
            # Check for index usage
            elif 'Index Scan' in line:
                parts = line.split('using')[1].split()
                analysis['index_usage'].append({
                    'index': parts[0],
                    'table': parts[2] if len(parts) > 2 else None
                })

        return analysis

    def optimize_query(self, query: str) -> Tuple[str, List[str]]:
        """Optimize SQL query"""
        try:
            analysis = self.analyze_query(query)
            optimized_query = query
            recommendations = []

            # Check execution time
            if analysis.get('execution_time', 0) > 1000:  # > 1 second
                recommendations.append("Query is slow, consider optimization")

            # Check for table scans
            for table in analysis.get('table_scans', []):
                recommendations.append(f"Add index on frequently queried columns in {table}")

            # Add LIMIT if missing
            if 'LIMIT' not in query.upper() and 'SELECT' in query.upper():
                optimized_query += " LIMIT 1000"
                recommendations.append("Added LIMIT clause to prevent large result sets")

            # Suggest materialized views for complex queries
            if query.upper().count('JOIN') > 2:
                recommendations.append("Consider using materialized views for complex joins")

            return optimized_query, recommendations
        except Exception as e:
            self.logger.error(f'Query optimization failed: {str(e)}')
            self.monitoring.record_error('query_optimization', str(e))
            return query, []

    def create_index_recommendation(self, table_name: str) -> List[Dict]:
        """Generate index recommendations for a table"""
        try:
            with self.engine.connect() as conn:
                # Get column statistics
                stats_query = f"""
                    SELECT
                        a.attname as column_name,
                        n_distinct,
                        correlation
                    FROM pg_stats s
                    JOIN pg_attribute a ON a.attname = s.attname
                    WHERE schemaname = 'public'
                    AND tablename = :table_name
                """
                result = conn.execute(text(stats_query), {'table_name': table_name})
                
                recommendations = []
                for row in result:
                    if row.n_distinct > 100 and abs(row.correlation) < 0.5:
                        recommendations.append({
                            'column': row.column_name,
                            'reason': 'High cardinality, low correlation',
                            'sql': f'CREATE INDEX idx_{table_name}_{row.column_name} ON {table_name}({row.column_name});'
                        })

                return recommendations
        except Exception as e:
            self.logger.error(f'Index recommendation failed: {str(e)}')
            self.monitoring.record_error('index_recommendation', str(e))
            return []

    def vacuum_analyze(self, table_name: Optional[str] = None) -> bool:
        """Perform VACUUM ANALYZE"""
        try:
            with self.engine.connect() as conn:
                if table_name:
                    conn.execute(text(f"VACUUM ANALYZE {table_name}"))
                else:
                    conn.execute(text("VACUUM ANALYZE"))
                return True
        except Exception as e:
            self.logger.error(f'Vacuum analyze failed: {str(e)}')
            self.monitoring.record_error('vacuum_analyze', str(e))
            return False

    def get_table_statistics(self, table_name: str) -> Dict:
        """Get table statistics"""
        try:
            with self.engine.connect() as conn:
                query = """
                    SELECT
                        reltuples::bigint as row_estimate,
                        pg_total_relation_size(:table_name) as total_bytes,
                        pg_indexes_size(:table_name) as index_bytes,
                        pg_table_size(:table_name) as table_bytes
                    FROM pg_class
                    WHERE relname = :table_name
                """
                result = conn.execute(text(query), {'table_name': table_name}).first()
                
                return {
                    'row_count': result.row_estimate,
                    'total_size': result.total_bytes,
                    'index_size': result.index_bytes,
                    'table_size': result.table_bytes
                }
        except Exception as e:
            self.logger.error(f'Failed to get table statistics: {str(e)}')
            self.monitoring.record_error('table_statistics', str(e))
            return {}
