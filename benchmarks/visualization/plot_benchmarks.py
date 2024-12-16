import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, Any, List
import os

class BenchmarkVisualizer:
    def __init__(self, results_file: str = 'comprehensive_benchmark_results.json'):
        """Initialize visualizer with benchmark results"""
        with open(results_file, 'r') as f:
            self.results = json.load(f)
        
        # Create output directory if it doesn't exist
        os.makedirs('benchmark_visualizations', exist_ok=True)

    def create_all_visualizations(self) -> None:
        """Generate all visualizations"""
        self.plot_cache_performance()
        self.plot_query_performance()
        self.plot_resource_performance()
        self.plot_load_simulation()
        self.create_performance_dashboard()
        self.plot_comparative_analysis()

    def plot_cache_performance(self) -> None:
        """Visualize cache performance metrics"""
        cache_results = self.results['cache_results']
        
        # Prepare data
        operations = list(cache_results.keys())
        response_times = [stats['mean'] * 1000 for stats in cache_results.values()]
        throughput = [stats['operations_per_second'] for stats in cache_results.values()]

        # Create subplot with two y-axes
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add response time bars
        fig.add_trace(
            go.Bar(name='Response Time (ms)', x=operations, y=response_times),
            secondary_y=False
        )

        # Add throughput line
        fig.add_trace(
            go.Scatter(name='Operations/sec', x=operations, y=throughput, mode='lines+markers'),
            secondary_y=True
        )

        # Update layout
        fig.update_layout(
            title='Cache Performance Metrics',
            barmode='group',
            template='plotly_white'
        )
        fig.update_yaxes(title_text="Response Time (ms)", secondary_y=False)
        fig.update_yaxes(title_text="Operations per Second", secondary_y=True)

        # Save plot
        fig.write_html('benchmark_visualizations/cache_performance.html')

    def plot_query_performance(self) -> None:
        """Visualize query performance metrics"""
        query_results = self.results['query_results']

        # Prepare data
        df = pd.DataFrame([
            {
                'Query Type': op,
                'Response Time (ms)': stats['mean'] * 1000,
                'Queries/sec': stats['queries_per_second'],
                'Std Dev': stats['std_dev'] * 1000
            }
            for op, stats in query_results.items()
        ])

        # Create figure
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Query Response Times', 'Query Throughput')
        )

        # Add response time bars with error bars
        fig.add_trace(
            go.Bar(
                name='Response Time',
                x=df['Query Type'],
                y=df['Response Time (ms)'],
                error_y=dict(type='data', array=df['Std Dev'])
            ),
            row=1, col=1
        )

        # Add throughput bars
        fig.add_trace(
            go.Bar(
                name='Throughput',
                x=df['Query Type'],
                y=df['Queries/sec']
            ),
            row=2, col=1
        )

        # Update layout
        fig.update_layout(
            height=800,
            title_text="Query Performance Analysis",
            showlegend=False,
            template='plotly_white'
        )

        # Save plot
        fig.write_html('benchmark_visualizations/query_performance.html')

    def plot_resource_performance(self) -> None:
        """Visualize resource monitoring performance"""
        resource_results = self.results['resource_results']['performance_benchmarks']

        # Prepare data
        operations = list(resource_results.keys())
        response_times = [stats['mean'] * 1000 for stats in resource_results.values()]
        throughput = [stats['operations_per_second'] for stats in resource_results.values()]

        # Create figure
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Resource Monitoring Response Times', 'Monitoring Operations per Second')
        )

        # Add response time bars
        fig.add_trace(
            go.Bar(name='Response Time', x=operations, y=response_times),
            row=1, col=1
        )

        # Add throughput bars
        fig.add_trace(
            go.Bar(name='Throughput', x=operations, y=throughput),
            row=2, col=1
        )

        # Update layout
        fig.update_layout(
            height=800,
            title_text="Resource Monitoring Performance",
            showlegend=False,
            template='plotly_white'
        )

        # Save plot
        fig.write_html('benchmark_visualizations/resource_performance.html')

    def plot_load_simulation(self) -> None:
        """Visualize load simulation results"""
        load_results = self.results['resource_results']['load_simulation']

        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add traces for each metric
        metrics = ['cpu_usage', 'memory_usage']
        colors = ['blue', 'red']

        for metric, color in zip(metrics, colors):
            fig.add_trace(
                go.Scatter(
                    name=metric.replace('_', ' ').title(),
                    y=load_results[metric],
                    line=dict(color=color)
                ),
                secondary_y=False
            )

        # Add I/O metrics on secondary axis
        io_metrics = ['disk_io', 'network_io']
        colors = ['green', 'purple']

        for metric, color in zip(io_metrics, colors):
            fig.add_trace(
                go.Scatter(
                    name=metric.replace('_', ' ').title(),
                    y=load_results[metric],
                    line=dict(color=color)
                ),
                secondary_y=True
            )

        # Update layout
        fig.update_layout(
            title='System Load Simulation Results',
            template='plotly_white'
        )
        fig.update_yaxes(title_text="Usage (%)", secondary_y=False)
        fig.update_yaxes(title_text="I/O (bytes)", secondary_y=True)

        # Save plot
        fig.write_html('benchmark_visualizations/load_simulation.html')

    def create_performance_dashboard(self) -> None:
        """Create a comprehensive performance dashboard"""
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Cache Performance',
                'Query Performance',
                'Resource Monitoring',
                'Load Simulation',
                'Response Time Distribution',
                'Throughput Comparison'
            )
        )

        # Add cache performance
        cache_stats = pd.DataFrame(self.results['cache_results']).T
        fig.add_trace(
            go.Bar(x=cache_stats.index, y=cache_stats['mean']*1000, name='Cache Response Time'),
            row=1, col=1
        )

        # Add query performance
        query_stats = pd.DataFrame(self.results['query_results']).T
        fig.add_trace(
            go.Bar(x=query_stats.index, y=query_stats['mean']*1000, name='Query Response Time'),
            row=1, col=2
        )

        # Add resource monitoring
        resource_stats = pd.DataFrame(self.results['resource_results']['performance_benchmarks']).T
        fig.add_trace(
            go.Bar(x=resource_stats.index, y=resource_stats['mean']*1000, name='Resource Response Time'),
            row=2, col=1
        )

        # Add load simulation
        load_data = self.results['resource_results']['load_simulation']
        fig.add_trace(
            go.Scatter(y=load_data['cpu_usage'], name='CPU Usage'),
            row=2, col=2
        )

        # Add response time distribution
        all_times = pd.concat([
            cache_stats['mean'],
            query_stats['mean'],
            resource_stats['mean']
        ])
        fig.add_trace(
            go.Box(y=all_times*1000, name='Response Times'),
            row=3, col=1
        )

        # Add throughput comparison
        fig.add_trace(
            go.Bar(
                x=['Cache', 'Query', 'Resource'],
                y=[
                    cache_stats['operations_per_second'].mean(),
                    query_stats['queries_per_second'].mean(),
                    resource_stats['operations_per_second'].mean()
                ],
                name='Avg Throughput'
            ),
            row=3, col=2
        )

        # Update layout
        fig.update_layout(
            height=1200,
            title_text="Performance Dashboard",
            showlegend=True,
            template='plotly_white'
        )

        # Save dashboard
        fig.write_html('benchmark_visualizations/performance_dashboard.html')

    def plot_comparative_analysis(self) -> None:
        """Create comparative analysis plots"""
        # Prepare data
        cache_stats = pd.DataFrame(self.results['cache_results']).T
        query_stats = pd.DataFrame(self.results['query_results']).T
        resource_stats = pd.DataFrame(self.results['resource_results']['performance_benchmarks']).T

        # Create figure
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Response Time Comparison',
                'Throughput Comparison',
                'Performance Stability (Std Dev)',
                'Operation Efficiency'
            )
        )

        # Response Time Comparison
        components = ['Cache', 'Query', 'Resource']
        mean_times = [
            cache_stats['mean'].mean() * 1000,
            query_stats['mean'].mean() * 1000,
            resource_stats['mean'].mean() * 1000
        ]
        fig.add_trace(
            go.Bar(x=components, y=mean_times, name='Avg Response Time'),
            row=1, col=1
        )

        # Throughput Comparison
        throughputs = [
            cache_stats['operations_per_second'].mean(),
            query_stats['queries_per_second'].mean(),
            resource_stats['operations_per_second'].mean()
        ]
        fig.add_trace(
            go.Bar(x=components, y=throughputs, name='Avg Throughput'),
            row=1, col=2
        )

        # Stability Comparison (Standard Deviation)
        std_devs = [
            cache_stats['std_dev'].mean() * 1000,
            query_stats['std_dev'].mean() * 1000,
            resource_stats['std_dev'].mean() * 1000
        ]
        fig.add_trace(
            go.Bar(x=components, y=std_devs, name='Std Dev'),
            row=2, col=1
        )

        # Efficiency Score (throughput/response_time)
        efficiency = [t/(r/1000) for t, r in zip(throughputs, mean_times)]
        fig.add_trace(
            go.Bar(x=components, y=efficiency, name='Efficiency Score'),
            row=2, col=2
        )

        # Update layout
        fig.update_layout(
            height=800,
            title_text="Comparative Performance Analysis",
            showlegend=False,
            template='plotly_white'
        )

        # Save plot
        fig.write_html('benchmark_visualizations/comparative_analysis.html')

def generate_visualizations() -> None:
    """Generate all benchmark visualizations"""
    visualizer = BenchmarkVisualizer()
    visualizer.create_all_visualizations()
    
    print("Benchmark visualizations have been generated in the 'benchmark_visualizations' directory:")
    print("1. cache_performance.html - Cache operation performance metrics")
    print("2. query_performance.html - Query optimization performance analysis")
    print("3. resource_performance.html - Resource monitoring performance")
    print("4. load_simulation.html - System load simulation results")
    print("5. performance_dashboard.html - Comprehensive performance dashboard")
    print("6. comparative_analysis.html - Comparative performance analysis")

if __name__ == "__main__":
    generate_visualizations()
