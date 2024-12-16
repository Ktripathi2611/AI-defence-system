import time
import statistics
import json
import threading
import asyncio
from typing import List, Dict, Any
import torch
import psutil
from src.optimization.resource_manager import ResourceManager

class ResourceBenchmark:
    def __init__(self):
        self.resource_manager = ResourceManager()
        self.results: Dict[str, List[float]] = {}

    def run_all_benchmarks(self, iterations: int = 1000) -> Dict[str, Dict[str, float]]:
        """Run all resource benchmarks"""
        benchmarks = [
            self.benchmark_resource_stats,
            self.benchmark_cpu_monitoring,
            self.benchmark_memory_monitoring,
            self.benchmark_gpu_monitoring,
            self.benchmark_disk_monitoring,
            self.benchmark_network_monitoring,
            self.benchmark_concurrent_monitoring
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
                'operations_per_second': len(times) / sum(times)
            }
        return stats

    def benchmark_resource_stats(self, iterations: int) -> None:
        """Benchmark overall resource statistics collection"""
        times: List[float] = []

        for _ in range(iterations):
            start_time = time.perf_counter()
            self.resource_manager.get_resource_stats()
            end_time = time.perf_counter()
            times.append(end_time - start_time)

        self.results['resource_stats_collection'] = times

    def benchmark_cpu_monitoring(self, iterations: int) -> None:
        """Benchmark CPU monitoring performance"""
        times: List[float] = []

        for _ in range(iterations):
            start_time = time.perf_counter()
            self.resource_manager._get_cpu_stats()
            end_time = time.perf_counter()
            times.append(end_time - start_time)

        self.results['cpu_monitoring'] = times

    def benchmark_memory_monitoring(self, iterations: int) -> None:
        """Benchmark memory monitoring performance"""
        times: List[float] = []

        for _ in range(iterations):
            start_time = time.perf_counter()
            self.resource_manager._get_memory_stats()
            end_time = time.perf_counter()
            times.append(end_time - start_time)

        self.results['memory_monitoring'] = times

    def benchmark_gpu_monitoring(self, iterations: int) -> None:
        """Benchmark GPU monitoring performance"""
        times: List[float] = []

        if not torch.cuda.is_available():
            self.results['gpu_monitoring'] = [0.0]  # Skip if no GPU
            return

        for _ in range(iterations):
            start_time = time.perf_counter()
            self.resource_manager._get_gpu_stats()
            end_time = time.perf_counter()
            times.append(end_time - start_time)

        self.results['gpu_monitoring'] = times

    def benchmark_disk_monitoring(self, iterations: int) -> None:
        """Benchmark disk monitoring performance"""
        times: List[float] = []

        for _ in range(iterations):
            start_time = time.perf_counter()
            self.resource_manager._get_disk_stats()
            end_time = time.perf_counter()
            times.append(end_time - start_time)

        self.results['disk_monitoring'] = times

    def benchmark_network_monitoring(self, iterations: int) -> None:
        """Benchmark network monitoring performance"""
        times: List[float] = []

        for _ in range(iterations):
            start_time = time.perf_counter()
            self.resource_manager._get_network_stats()
            end_time = time.perf_counter()
            times.append(end_time - start_time)

        self.results['network_monitoring'] = times

    def benchmark_concurrent_monitoring(self, iterations: int) -> None:
        """Benchmark concurrent resource monitoring"""
        times: List[float] = []
        threads: List[threading.Thread] = []
        results: List[float] = []

        def monitor_resources() -> None:
            start_time = time.perf_counter()
            self.resource_manager.get_resource_stats()
            end_time = time.perf_counter()
            results.append(end_time - start_time)

        # Create and start threads
        for _ in range(iterations):
            thread = threading.Thread(target=monitor_resources)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        self.results['concurrent_monitoring'] = results

    def simulate_load(self, duration: int = 10) -> Dict[str, List[float]]:
        """Simulate system load and measure resource usage"""
        load_stats: Dict[str, List[float]] = {
            'cpu_usage': [],
            'memory_usage': [],
            'disk_io': [],
            'network_io': []
        }

        def cpu_load() -> None:
            """Generate CPU load"""
            end_time = time.time() + duration
            while time.time() < end_time:
                _ = [i * i for i in range(10000)]

        def memory_load() -> None:
            """Generate memory load"""
            data = []
            end_time = time.time() + duration
            while time.time() < end_time:
                data.extend([i for i in range(10000)])
                time.sleep(0.1)

        def disk_load() -> None:
            """Generate disk I/O"""
            end_time = time.time() + duration
            while time.time() < end_time:
                with open('temp_benchmark.txt', 'w') as f:
                    f.write('x' * 1000000)
                time.sleep(0.1)

        # Start load generators
        threads = [
            threading.Thread(target=cpu_load),
            threading.Thread(target=memory_load),
            threading.Thread(target=disk_load)
        ]
        for thread in threads:
            thread.start()

        # Monitor resources during load
        start_time = time.time()
        while time.time() - start_time < duration:
            stats = self.resource_manager.get_resource_stats()
            load_stats['cpu_usage'].append(stats['cpu']['percent'])
            load_stats['memory_usage'].append(stats['memory']['percent'])
            load_stats['disk_io'].append(stats['disk']['io']['write_bytes'])
            load_stats['network_io'].append(stats['network']['bytes_sent'])
            time.sleep(0.1)

        # Wait for load generators to finish
        for thread in threads:
            thread.join()

        return load_stats

def run_benchmarks() -> None:
    """Run all resource benchmarks"""
    benchmark = ResourceBenchmark()
    
    # Run performance benchmarks
    results = benchmark.run_all_benchmarks()

    # Run load simulation
    load_results = benchmark.simulate_load()

    # Print performance results
    print("\nResource Manager Benchmark Results:")
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

    # Print load simulation results
    print("\nLoad Simulation Results:")
    print("=" * 50)
    for metric, values in load_results.items():
        print(f"\n{metric}:")
        print("-" * 30)
        print(f"Mean: {statistics.mean(values):.2f}")
        print(f"Max: {max(values):.2f}")
        print(f"Min: {min(values):.2f}")

    # Export all results to JSON
    with open('resource_benchmark_results.json', 'w') as f:
        json.dump({
            'performance_benchmarks': results,
            'load_simulation': load_results
        }, f, indent=2)

if __name__ == "__main__":
    run_benchmarks()
