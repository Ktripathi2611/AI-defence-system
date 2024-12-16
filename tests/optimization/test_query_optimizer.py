import pytest
from unittest.mock import Mock, patch, call
from src.optimization.query_optimizer import QueryOptimizer
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

@pytest.fixture
def query_optimizer():
    """Create a query optimizer instance"""
    return QueryOptimizer("postgresql://user:pass@localhost:5432/testdb")

@pytest.fixture
def mock_engine():
    """Create a mock database engine"""
    with patch('sqlalchemy.create_engine') as mock:
        yield mock

class TestQueryOptimizer:
    def test_analyze_query(self, query_optimizer, mock_engine):
        """Test query analysis"""
        # Mock query plan
        mock_result = Mock()
        mock_result.return_value = [
            "Seq Scan on users  (cost=0.00..1.14 rows=14 width=36)",
            "Planning Time: 0.019 ms",
            "Execution Time: 0.039 ms"
        ]
        mock_engine.return_value.connect.return_value.__enter__.return_value.execute = mock_result

        analysis = query_optimizer.analyze_query("SELECT * FROM users")
        
        assert analysis['execution_time'] == 0.039
        assert analysis['planning_time'] == 0.019
        assert 'users' in analysis['table_scans']
        assert "Consider adding an index on table 'users'" in analysis['recommendations']

    def test_optimize_query(self, query_optimizer):
        """Test query optimization"""
        test_query = "SELECT * FROM users WHERE active = true"
        optimized_query, recommendations = query_optimizer.optimize_query(test_query)

        assert "LIMIT 1000" in optimized_query
        assert len(recommendations) > 0

    def test_create_index_recommendation(self, query_optimizer, mock_engine):
        """Test index recommendations"""
        # Mock column statistics
        mock_result = Mock()
        mock_result.return_value = [
            Mock(column_name='email', n_distinct=1000, correlation=0.1),
            Mock(column_name='name', n_distinct=50, correlation=0.8)
        ]
        mock_engine.return_value.connect.return_value.__enter__.return_value.execute = mock_result

        recommendations = query_optimizer.create_index_recommendation('users')
        
        assert len(recommendations) == 1
        assert recommendations[0]['column'] == 'email'
        assert 'CREATE INDEX' in recommendations[0]['sql']

    def test_vacuum_analyze(self, query_optimizer, mock_engine):
        """Test vacuum analyze operation"""
        mock_execute = Mock()
        mock_engine.return_value.connect.return_value.__enter__.return_value.execute = mock_execute

        # Test vacuum analyze on specific table
        result = query_optimizer.vacuum_analyze('users')
        assert result is True
        mock_execute.assert_called_with(text("VACUUM ANALYZE users"))

        # Test vacuum analyze on all tables
        result = query_optimizer.vacuum_analyze()
        assert result is True
        mock_execute.assert_called_with(text("VACUUM ANALYZE"))

    def test_get_table_statistics(self, query_optimizer, mock_engine):
        """Test retrieving table statistics"""
        mock_result = Mock()
        mock_result.return_value.first.return_value = Mock(
            row_estimate=1000,
            total_bytes=1024000,
            index_bytes=102400,
            table_bytes=921600
        )
        mock_engine.return_value.connect.return_value.__enter__.return_value.execute = mock_result

        stats = query_optimizer.get_table_statistics('users')
        
        assert stats['row_count'] == 1000
        assert stats['total_size'] == 1024000
        assert stats['index_size'] == 102400
        assert stats['table_size'] == 921600

    def test_error_handling(self, query_optimizer, mock_engine):
        """Test error handling"""
        # Simulate database error
        mock_engine.return_value.connect.return_value.__enter__.return_value.execute.side_effect = \
            SQLAlchemyError("Database error")

        # Test error handling in analyze_query
        analysis = query_optimizer.analyze_query("SELECT * FROM users")
        assert analysis == {}

        # Test error handling in get_table_statistics
        stats = query_optimizer.get_table_statistics('users')
        assert stats == {}

    def test_complex_query_optimization(self, query_optimizer):
        """Test optimization of complex queries"""
        complex_query = """
            SELECT u.name, o.order_date, p.product_name
            FROM users u
            JOIN orders o ON u.id = o.user_id
            JOIN order_items oi ON o.id = oi.order_id
            JOIN products p ON oi.product_id = p.id
            WHERE o.order_date > '2024-01-01'
        """
        
        optimized_query, recommendations = query_optimizer.optimize_query(complex_query)
        
        assert "Consider using materialized views for complex joins" in recommendations
        assert "LIMIT 1000" in optimized_query

    def test_query_plan_parsing(self, query_optimizer, mock_engine):
        """Test parsing of different query plan formats"""
        mock_result = Mock()
        mock_result.return_value = [
            "Nested Loop  (cost=0.00..32.97 rows=1 width=551)",
            "  ->  Index Scan using users_pkey on users  (cost=0.00..8.27 rows=1 width=551)",
            "  ->  Index Only Scan using orders_user_id_idx on orders  (cost=0.00..8.27 rows=1 width=551)",
            "Planning Time: 0.152 ms",
            "Execution Time: 0.258 ms"
        ]
        mock_engine.return_value.connect.return_value.__enter__.return_value.execute = mock_result

        analysis = query_optimizer.analyze_query("SELECT * FROM users JOIN orders ON users.id = orders.user_id")
        
        assert analysis['execution_time'] == 0.258
        assert analysis['planning_time'] == 0.152
        assert len(analysis['index_usage']) == 2

    def test_large_table_handling(self, query_optimizer, mock_engine):
        """Test handling of large tables"""
        # Simulate statistics for a large table
        mock_result = Mock()
        mock_result.return_value.first.return_value = Mock(
            row_estimate=10000000,  # 10 million rows
            total_bytes=10737418240,  # 10 GB
            index_bytes=1073741824,  # 1 GB
            table_bytes=9663676416   # 9 GB
        )
        mock_engine.return_value.connect.return_value.__enter__.return_value.execute = mock_result

        stats = query_optimizer.get_table_statistics('large_table')
        
        assert stats['row_count'] == 10000000
        assert stats['total_size'] == 10737418240
        assert stats['index_size'] == 1073741824
        assert stats['table_size'] == 9663676416

    def test_concurrent_optimization(self, query_optimizer, mock_engine):
        """Test concurrent query optimization"""
        import threading
        import queue

        results = queue.Queue()
        
        def optimize_query():
            query = "SELECT * FROM users WHERE id = 1"
            optimized, _ = query_optimizer.optimize_query(query)
            results.put(optimized)

        # Run multiple optimizations concurrently
        threads = [threading.Thread(target=optimize_query) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Check all results are consistent
        all_results = []
        while not results.empty():
            all_results.append(results.get())
        
        assert all(r == all_results[0] for r in all_results)
