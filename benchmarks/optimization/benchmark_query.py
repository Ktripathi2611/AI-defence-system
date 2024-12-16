import time
import statistics
import json
from typing import List, Dict, Any
from sqlalchemy import create_engine, text
from src.optimization.query_optimizer import QueryOptimizer

class QueryBenchmark:
    def __init__(self, db_url: str = "postgresql://user:pass@localhost:5432/testdb"):
        self.query_optimizer = QueryOptimizer(db_url)
        self.engine = create_engine(db_url)
        self.results: Dict[str, List[float]] = {}

    def run_all_benchmarks(self, iterations: int = 100) -> Dict[str, Dict[str, float]]:
        """Run all query benchmarks"""
        benchmarks = [
            self.benchmark_simple_queries,
            self.benchmark_complex_queries,
            self.benchmark_query_analysis,
            self.benchmark_index_recommendations,
            self.benchmark_table_statistics
        ]

        for benchmark in benchmarks:
            benchmark(iterations)

        return self.get_statistics()

    def get_statistics(self) -> Dict[str, Dict[str, float]]:
        """Calculate statistics for benchmark results"""
        stats = {}
        for name, times in self.results.items():
            stats[name] = {
                'mean': statistics.mean(times),
                'median': statistics.median(times),
                'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
                'min': min(times),
                'max': max(times),
                'total_time': sum(times),
                'queries_per_second': len(times) / sum(times)
            }
        return stats

    def benchmark_simple_queries(self, iterations: int) -> None:
        """Benchmark simple query optimization"""
        times: List[float] = []
        queries = [
            "SELECT * FROM users WHERE id = 1",
            "SELECT name, email FROM users WHERE active = true",
            "SELECT COUNT(*) FROM orders WHERE status = 'completed'",
            "SELECT product_name FROM products WHERE price > 100"
        ]

        for _ in range(iterations):
            for query in queries:
                start_time = time.perf_counter()
                self.query_optimizer.optimize_query(query)
                end_time = time.perf_counter()
                times.append(end_time - start_time)

        self.results['simple_query_optimization'] = times

    def benchmark_complex_queries(self, iterations: int) -> None:
        """Benchmark complex query optimization"""
        times: List[float] = []
        queries = [
            """
            SELECT u.name, o.order_date, p.product_name, SUM(oi.quantity * p.price) as total
            FROM users u
            JOIN orders o ON u.id = o.user_id
            JOIN order_items oi ON o.id = oi.order_id
            JOIN products p ON oi.product_id = p.id
            WHERE o.order_date >= '2024-01-01'
            GROUP BY u.name, o.order_date, p.product_name
            HAVING SUM(oi.quantity * p.price) > 1000
            ORDER BY total DESC
            """,
            """
            WITH monthly_sales AS (
                SELECT 
                    DATE_TRUNC('month', o.order_date) as month,
                    p.category,
                    SUM(oi.quantity * p.price) as sales
                FROM orders o
                JOIN order_items oi ON o.id = oi.order_id
                JOIN products p ON oi.product_id = p.id
                GROUP BY month, p.category
            )
            SELECT 
                month,
                category,
                sales,
                LAG(sales) OVER (PARTITION BY category ORDER BY month) as prev_month_sales,
                sales - LAG(sales) OVER (PARTITION BY category ORDER BY month) as growth
            FROM monthly_sales
            ORDER BY month DESC, sales DESC
            """
        ]

        for _ in range(iterations):
            for query in queries:
                start_time = time.perf_counter()
                self.query_optimizer.optimize_query(query)
                end_time = time.perf_counter()
                times.append(end_time - start_time)

        self.results['complex_query_optimization'] = times

    def benchmark_query_analysis(self, iterations: int) -> None:
        """Benchmark query analysis performance"""
        times: List[float] = []
        query = """
        SELECT u.name, COUNT(o.id) as order_count
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        GROUP BY u.name
        HAVING COUNT(o.id) > 5
        """

        for _ in range(iterations):
            start_time = time.perf_counter()
            self.query_optimizer.analyze_query(query)
            end_time = time.perf_counter()
            times.append(end_time - start_time)

        self.results['query_analysis'] = times

    def benchmark_index_recommendations(self, iterations: int) -> None:
        """Benchmark index recommendation generation"""
        times: List[float] = []
        tables = ['users', 'orders', 'products', 'order_items']

        for _ in range(iterations):
            for table in tables:
                start_time = time.perf_counter()
                self.query_optimizer.create_index_recommendation(table)
                end_time = time.perf_counter()
                times.append(end_time - start_time)

        self.results['index_recommendations'] = times

    def benchmark_table_statistics(self, iterations: int) -> None:
        """Benchmark table statistics retrieval"""
        times: List[float] = []
        tables = ['users', 'orders', 'products', 'order_items']

        for _ in range(iterations):
            for table in tables:
                start_time = time.perf_counter()
                self.query_optimizer.get_table_statistics(table)
                end_time = time.perf_counter()
                times.append(end_time - start_time)

        self.results['table_statistics'] = times

def run_benchmarks() -> None:
    """Run all query benchmarks"""
    benchmark = QueryBenchmark()
    results = benchmark.run_all_benchmarks()

    # Print results
    print("\nQuery Optimizer Benchmark Results:")
    print("=" * 50)
    for name, stats in results.items():
        print(f"\n{name}:")
        print("-" * 30)
        print(f"Mean time: {stats['mean']*1000:.2f}ms")
        print(f"Median time: {stats['median']*1000:.2f}ms")
        print(f"Std Dev: {stats['std_dev']*1000:.2f}ms")
        print(f"Min time: {stats['min']*1000:.2f}ms")
        print(f"Max time: {stats['max']*1000:.2f}ms")
        print(f"Queries/sec: {stats['queries_per_second']:.2f}")

    # Export results to JSON
    with open('query_benchmark_results.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    run_benchmarks()
