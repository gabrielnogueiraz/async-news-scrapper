"""
Optional: Visualize benchmark results with charts.

Requirements:
    pip install matplotlib

Usage:
    python benchmarks/visualize.py
"""
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from datetime import datetime
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️  matplotlib not installed. Install with: pip install matplotlib")


def load_benchmark_results(directory: str = "benchmarks/results") -> List[Dict[str, Any]]:
    """Load all benchmark JSON results."""
    results_dir = Path(directory)
    if not results_dir.exists():
        return []
    
    results = []
    for json_file in results_dir.glob("benchmark_*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                results.append(data)
        except Exception as e:
            print(f"⚠️  Failed to load {json_file}: {e}")
    
    results.sort(key=lambda x: x.get('timestamp', ''))
    return results


def plot_performance_trends(results: List[Dict[str, Any]]):
    """Plot performance trends over time."""
    if not MATPLOTLIB_AVAILABLE:
        return
    
    if len(results) < 2:
        print("⚠️  Need at least 2 benchmark results to plot trends")
        return
    
    # Extract data
    timestamps = []
    durations = []
    throughputs = []
    memory_usage = []
    cpu_usage = []
    
    for result in results:
        try:
            timestamp = datetime.fromisoformat(result['timestamp'])
            timestamps.append(timestamp)
            durations.append(result['summary']['total_duration_seconds'])
            throughputs.append(result['requests']['throughput_req_per_sec'])
            memory_usage.append(result['memory']['peak_mb'])
            cpu_usage.append(result['cpu']['avg_percent'])
        except Exception as e:
            print(f"⚠️  Skipping invalid result: {e}")
            continue
    
    if not timestamps:
        print("❌ No valid data to plot")
        return
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Async News Scraper - Performance Trends', fontsize=16, fontweight='bold')
    
    # Plot 1: Duration over time
    ax1 = axes[0, 0]
    ax1.plot(timestamps, durations, marker='o', linewidth=2, markersize=8, color='#2196F3')
    ax1.set_title('Execution Duration', fontweight='bold')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Duration (seconds)')
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # Plot 2: Throughput over time
    ax2 = axes[0, 1]
    ax2.plot(timestamps, throughputs, marker='s', linewidth=2, markersize=8, color='#4CAF50')
    ax2.set_title('Throughput', fontweight='bold')
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Requests/second')
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
    
    # Plot 3: Memory usage over time
    ax3 = axes[1, 0]
    ax3.plot(timestamps, memory_usage, marker='^', linewidth=2, markersize=8, color='#FF9800')
    ax3.set_title('Memory Usage', fontweight='bold')
    ax3.set_xlabel('Time')
    ax3.set_ylabel('Memory (MB)')
    ax3.grid(True, alpha=0.3)
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
    
    # Plot 4: CPU usage over time
    ax4 = axes[1, 1]
    ax4.plot(timestamps, cpu_usage, marker='D', linewidth=2, markersize=8, color='#F44336')
    ax4.set_title('CPU Usage', fontweight='bold')
    ax4.set_xlabel('Time')
    ax4.set_ylabel('CPU (%)')
    ax4.grid(True, alpha=0.3)
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    
    # Save figure
    output_path = Path("benchmarks/results/performance_trends.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"📊 Chart saved to: {output_path.absolute()}")
    
    # Show plot
    plt.show()


def plot_metrics_comparison(results: List[Dict[str, Any]]):
    """Plot comparison of key metrics."""
    if not MATPLOTLIB_AVAILABLE:
        return
    
    if not results:
        print("❌ No results to plot")
        return
    
    # Use last result
    result = results[-1]
    
    # Extract metrics
    metrics = {
        'Duration (s)': result['summary']['total_duration_seconds'],
        'Throughput\n(req/s)': result['requests']['throughput_req_per_sec'],
        'Memory (MB)': result['memory']['peak_mb'],
        'CPU (%)': result['cpu']['avg_percent'],
    }
    
    # Create bar chart
    fig, ax = plt.subplots(figsize=(12, 6))
    
    colors = ['#2196F3', '#4CAF50', '#FF9800', '#F44336']
    bars = ax.bar(metrics.keys(), metrics.values(), color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    
    ax.set_title('Latest Benchmark - Key Metrics', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel('Value', fontsize=12)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}',
                ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    plt.tight_layout()
    
    # Save figure
    output_path = Path("benchmarks/results/metrics_comparison.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"📊 Chart saved to: {output_path.absolute()}")
    
    plt.show()


def main():
    """Main visualization entry point."""
    if not MATPLOTLIB_AVAILABLE:
        print("\n❌ matplotlib is required for visualization")
        print("   Install with: pip install matplotlib")
        return 1
    
    print("\n" + "="*80)
    print("BENCHMARK VISUALIZATION".center(80))
    print("="*80 + "\n")
    
    results_dir = "benchmarks/results"
    if len(sys.argv) > 1:
        results_dir = sys.argv[1]
    
    print(f"📁 Loading results from: {results_dir}")
    results = load_benchmark_results(results_dir)
    
    if not results:
        print("\n❌ No benchmark results found!")
        print("   Run benchmarks first: python run_benchmark.py")
        return 1
    
    print(f"✅ Loaded {len(results)} result(s)\n")
    
    # Generate visualizations
    print("📊 Generating visualizations...")
    
    if len(results) >= 2:
        print("\n1. Performance Trends (multiple runs)")
        plot_performance_trends(results)
    
    print("\n2. Metrics Comparison (latest run)")
    plot_metrics_comparison(results)
    
    print("\n✅ Visualization complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
