"""
Compare multiple benchmark results over time.
"""
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


def load_benchmark_results(directory: str = "benchmarks/results") -> List[Dict[str, Any]]:
    """Load all benchmark JSON results from directory."""
    results_dir = Path(directory)
    if not results_dir.exists():
        print(f"❌ Results directory not found: {results_dir}")
        return []
    
    results = []
    for json_file in results_dir.glob("benchmark_*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data['_filename'] = json_file.name
                results.append(data)
        except Exception as e:
            print(f"⚠️  Failed to load {json_file}: {e}")
    
    # Sort by timestamp
    results.sort(key=lambda x: x.get('timestamp', ''))
    return results


def compare_benchmarks(results: List[Dict[str, Any]]):
    """Compare multiple benchmark results."""
    if len(results) < 2:
        print("❌ Need at least 2 benchmark results to compare")
        return
    
    print("\n" + "="*80)
    print("BENCHMARK COMPARISON REPORT".center(80))
    print("="*80)
    print(f"\nComparing {len(results)} benchmark results\n")
    
    # Extract key metrics
    metrics = []
    for result in results:
        timestamp = result.get('timestamp', 'Unknown')
        summary = result.get('summary', {})
        requests = result.get('requests', {})
        memory = result.get('memory', {})
        cpu = result.get('cpu', {})
        
        metrics.append({
            'timestamp': timestamp,
            'duration': summary.get('total_duration_seconds', 0),
            'throughput': requests.get('throughput_req_per_sec', 0),
            'memory_mb': memory.get('peak_mb', 0),
            'cpu_percent': cpu.get('avg_percent', 0),
            'news_scraped': summary.get('news_scraped', 0),
        })
    
    # Print comparison table
    print("📊 PERFORMANCE METRICS COMPARISON")
    print("-" * 80)
    print(f"{'Timestamp':<20} {'Duration(s)':<12} {'Throughput':<12} {'Memory(MB)':<12} {'CPU(%)':<10}")
    print("-" * 80)
    
    for m in metrics:
        timestamp_short = m['timestamp'][:19] if len(m['timestamp']) > 19 else m['timestamp']
        print(f"{timestamp_short:<20} {m['duration']:<12.4f} {m['throughput']:<12.2f} "
              f"{m['memory_mb']:<12.2f} {m['cpu_percent']:<10.2f}")
    
    # Calculate trends
    print("\n📈 PERFORMANCE TRENDS")
    print("-" * 80)
    
    if len(metrics) >= 2:
        first = metrics[0]
        last = metrics[-1]
        
        duration_change = ((last['duration'] - first['duration']) / first['duration'] * 100) if first['duration'] > 0 else 0
        throughput_change = ((last['throughput'] - first['throughput']) / first['throughput'] * 100) if first['throughput'] > 0 else 0
        memory_change = ((last['memory_mb'] - first['memory_mb']) / first['memory_mb'] * 100) if first['memory_mb'] > 0 else 0
        cpu_change = ((last['cpu_percent'] - first['cpu_percent']) / first['cpu_percent'] * 100) if first['cpu_percent'] > 0 else 0
        
        def format_change(value: float, inverse: bool = False) -> str:
            """Format change with color indicator."""
            if inverse:
                value = -value
            if value > 5:
                return f"📈 +{value:.2f}% (improved)"
            elif value < -5:
                return f"📉 {value:.2f}% (degraded)"
            else:
                return f"➡️  {value:+.2f}% (stable)"
        
        print(f"Duration:     {format_change(duration_change, inverse=True)}")
        print(f"Throughput:   {format_change(throughput_change)}")
        print(f"Memory:       {format_change(memory_change, inverse=True)}")
        print(f"CPU Usage:    {format_change(cpu_change, inverse=True)}")
    
    # Calculate statistics
    print("\n📊 STATISTICAL SUMMARY")
    print("-" * 80)
    
    avg_duration = sum(m['duration'] for m in metrics) / len(metrics)
    avg_throughput = sum(m['throughput'] for m in metrics) / len(metrics)
    avg_memory = sum(m['memory_mb'] for m in metrics) / len(metrics)
    avg_cpu = sum(m['cpu_percent'] for m in metrics) / len(metrics)
    
    min_duration = min(m['duration'] for m in metrics)
    max_duration = max(m['duration'] for m in metrics)
    
    print(f"Average Duration:     {avg_duration:.4f}s")
    print(f"Average Throughput:   {avg_throughput:.2f} req/s")
    print(f"Average Memory:       {avg_memory:.2f} MB")
    print(f"Average CPU:          {avg_cpu:.2f}%")
    print(f"\nBest Duration:        {min_duration:.4f}s")
    print(f"Worst Duration:       {max_duration:.4f}s")
    print(f"Variance:             {max_duration - min_duration:.4f}s ({((max_duration - min_duration) / avg_duration * 100):.2f}%)")
    
    print("\n" + "="*80)


def main():
    """Main entry point."""
    results_dir = "benchmarks/results"
    
    if len(sys.argv) > 1:
        results_dir = sys.argv[1]
    
    print(f"📁 Loading benchmark results from: {results_dir}")
    results = load_benchmark_results(results_dir)
    
    if not results:
        print("\n❌ No benchmark results found!")
        print(f"   Run benchmarks first: python run_benchmark.py")
        return
    
    print(f"✅ Loaded {len(results)} benchmark result(s)")
    
    if len(results) == 1:
        print("\n⚠️  Only one benchmark result found. Run more benchmarks to compare.")
        print("   Example: python run_benchmark.py")
    else:
        compare_benchmarks(results)


if __name__ == "__main__":
    main()
