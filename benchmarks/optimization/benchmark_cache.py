import asyncio
import time
import statistics
from typing import List, Dict, Any
import json
import random
import string
from src.optimization.cache_manager import CacheManager

class CacheBenchmark:
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.cache_manager = CacheManager(redis_url)
        self.results: Dict[str, List[float]] = {}

    async def run_all_benchmarks(self, iterations: int = 1000) -> Dict[str, Dict[str, float]]:
        """Run all benchmarks and return results"""
        benchmarks = [
            self.benchmark_set_get,
            self.benchmark_cached_decorator,
            self.benchmark_large_data,
            self.benchmark_concurrent_access,
            self.benchmark_key_generation
        ]

        for benchmark in benchmarks:
            await benchmark(iterations)

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
                'operations_per_second': len(times) / sum(times)
            }
        return stats

    @staticmethod
    def generate_random_data(size_kb: int) -> Dict[str, str]:
        """Generate random data of specified size"""
        chars = string.ascii_letters + string.digits
        data = ''.join(random.choice(chars) for _ in range(size_kb * 1024))
        return {'data': data}

    async def benchmark_set_get(self, iterations: int) -> None:
        """Benchmark basic set/get operations"""
        times: List[float] = []
        
        for i in range(iterations):
            key = f"benchmark_key_{i}"
            value = {'test': f'value_{i}'}
            
            # Measure SET
            start_time = time.perf_counter()
            self.cache_manager.set(key, value)
            end_time = time.perf_counter()
            times.append(end_time - start_time)
            
            # Measure GET
            start_time = time.perf_counter()
            self.cache_manager.get(key)
            end_time = time.perf_counter()
            times.append(end_time - start_time)

        self.results['set_get_operations'] = times

    async def benchmark_cached_decorator(self, iterations: int) -> None:
        """Benchmark cached decorator performance"""
        times: List[float] = []

        @self.cache_manager.cached('benchmark')
        async def test_func(x: int) -> int:
            await asyncio.sleep(0.001)  # Simulate work
            return x * 2

        for i in range(iterations):
            start_time = time.perf_counter()
            await test_func(i % 100)  # Reuse some values to test cache hits
            end_time = time.perf_counter()
            times.append(end_time - start_time)

        self.results['cached_decorator'] = times

    async def benchmark_large_data(self, iterations: int) -> None:
        """Benchmark performance with large data"""
        times: List[float] = []
        sizes = [1, 10, 100, 1000]  # sizes in KB

        for size in sizes:
            data = self.generate_random_data(size)
            key = f"large_data_{size}"

            for _ in range(iterations // len(sizes)):
                # Measure SET
                start_time = time.perf_counter()
                self.cache_manager.set(key, data)
                end_time = time.perf_counter()
                times.append(end_time - start_time)

                # Measure GET
                start_time = time.perf_counter()
                self.cache_manager.get(key)
                end_time = time.perf_counter()
                times.append(end_time - start_time)

        self.results['large_data_operations'] = times

    async def benchmark_concurrent_access(self, iterations: int) -> None:
        """Benchmark concurrent cache access"""
        times: List[float] = []

        async def concurrent_operation(i: int) -> None:
            key = f"concurrent_key_{i}"
            value = {'test': f'value_{i}'}

            start_time = time.perf_counter()
            self.cache_manager.set(key, value)
            await asyncio.sleep(0.001)  # Simulate network latency
            self.cache_manager.get(key)
            end_time = time.perf_counter()
            times.append(end_time - start_time)

        # Run concurrent operations
        tasks = [concurrent_operation(i) for i in range(iterations)]
        await asyncio.gather(*tasks)

        self.results['concurrent_access'] = times

    async def benchmark_key_generation(self, iterations: int) -> None:
        """Benchmark key generation performance"""
        times: List[float] = []

        for i in range(iterations):
            start_time = time.perf_counter()
            self.cache_manager.cache_key(
                'benchmark',
                i,
                test=f'value_{i}',
                complex={'nested': {'data': i}}
            )
            end_time = time.perf_counter()
            times.append(end_time - start_time)

        self.results['key_generation'] = times

async def run_benchmarks() -> None:
    """Run all cache benchmarks"""
    benchmark = CacheBenchmark()
    results = await benchmark.run_all_benchmarks()

    # Print results
    print("\nCache Benchmark Results:")
    print("=" * 50)
    for name, stats in results.items():
        print(f"\n{name}:")
        print("-" * 30)
        print(f"Mean time: {stats['mean']*1000:.2f}ms")
        print(f"Median time: {stats['median']*1000:.2f}ms")
        print(f"Std Dev: {stats['std_dev']*1000:.2f}ms")
        print(f"Min time: {stats['min']*1000:.2f}ms")
        print(f"Max time: {stats['max']*1000:.2f}ms")
        print(f"Operations/sec: {stats['operations_per_second']:.2f}")

    # Export results to JSON
    with open('cache_benchmark_results.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    asyncio.run(run_benchmarks())
