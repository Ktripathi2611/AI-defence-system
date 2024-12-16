import asyncio
import json
import time
from typing import Dict, Any
from benchmark_cache import run_benchmarks as run_cache_benchmarks
from benchmark_query import run_benchmarks as run_query_benchmarks
from benchmark_resources import run_benchmarks as run_resource_benchmarks

async def run_all_benchmarks() -> Dict[str, Any]:
    """Run all benchmarks and aggregate results"""
    start_time = time.time()
    
    print("Starting comprehensive benchmarks...")
    print("=" * 50)

    # Run cache benchmarks
    print("\nRunning Cache Benchmarks...")
    await run_cache_benchmarks()

    # Run query benchmarks
    print("\nRunning Query Benchmarks...")
    run_query_benchmarks()

    # Run resource benchmarks
    print("\nRunning Resource Benchmarks...")
    run_resource_benchmarks()

    end_time = time.time()
    total_time = end_time - start_time

    # Aggregate results
    results = {
        'cache_results': json.load(open('cache_benchmark_results.json')),
        'query_results': json.load(open('query_benchmark_results.json')),
        'resource_results': json.load(open('resource_benchmark_results.json')),
        'total_benchmark_time': total_time
    }

    # Generate summary report
    print("\nBenchmark Summary Report")
    print("=" * 50)
    print(f"Total Benchmark Time: {total_time:.2f} seconds")
    
    # Cache performance summary
    print("\nCache Performance:")
    print("-" * 30)
    for operation, stats in results['cache_results'].items():
        print(f"{operation}:")
        print(f"  Avg Response Time: {stats['mean']*1000:.2f}ms")
        print(f"  Operations/sec: {stats['operations_per_second']:.2f}")

    # Query performance summary
    print("\nQuery Performance:")
    print("-" * 30)
    for operation, stats in results['query_results'].items():
        print(f"{operation}:")
        print(f"  Avg Response Time: {stats['mean']*1000:.2f}ms")
        print(f"  Queries/sec: {stats['queries_per_second']:.2f}")

    # Resource monitoring performance summary
    print("\nResource Monitoring Performance:")
    print("-" * 30)
    for operation, stats in results['resource_results']['performance_benchmarks'].items():
        print(f"{operation}:")
        print(f"  Avg Response Time: {stats['mean']*1000:.2f}ms")
        print(f"  Operations/sec: {stats['operations_per_second']:.2f}")

    # Export comprehensive results
    with open('comprehensive_benchmark_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    return results

if __name__ == "__main__":
    asyncio.run(run_all_benchmarks())
