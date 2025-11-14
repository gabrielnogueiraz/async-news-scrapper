"""
Example: How to use the benchmark system programmatically.

This script demonstrates how to:
1. Run benchmarks programmatically
2. Access metrics data
3. Generate custom reports
4. Compare multiple runs
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db import init_db, get_db_context
from benchmarks.metrics import MetricsCollector
from benchmarks.scraper_instrumented import InstrumentedG1Scraper
from benchmarks.reporter import BenchmarkReporter


async def run_custom_benchmark():
    """Example: Run a custom benchmark with specific configuration."""
    print("🔧 Running custom benchmark...")
    
    # Initialize database
    await init_db()
    
    # Create collector
    collector = MetricsCollector()
    
    # Start collection
    collector.start()
    await collector.start_cpu_monitoring()
    
    try:
        # Run scraper
        async with get_db_context() as db:
            scraper = InstrumentedG1Scraper(db, collector)
            news_scraped, news_saved = await scraper.scrape()
            
            collector.metrics.news_scraped = news_scraped
            collector.metrics.news_saved = news_saved
    finally:
        await collector.stop()
    
    # Get metrics
    metrics = collector.get_metrics()
    
    # Access specific metrics
    print(f"\n📊 Custom Metrics Access:")
    print(f"   Duration: {metrics.total_duration:.4f}s")
    print(f"   Memory: {metrics.memory_used_mb:.2f} MB")
    print(f"   CPU: {metrics.avg_cpu_percent:.2f}%")
    print(f"   Throughput: {metrics.throughput:.2f} req/s")
    
    return metrics


async def compare_multiple_runs(iterations: int = 3):
    """Example: Run multiple benchmarks and compare results."""
    print(f"\n🔄 Running {iterations} iterations for comparison...")
    
    all_metrics = []
    
    for i in range(iterations):
        print(f"\n   Iteration {i+1}/{iterations}...")
        metrics = await run_custom_benchmark()
        all_metrics.append(metrics)
        
        if i < iterations - 1:
            await asyncio.sleep(1)  # Wait between runs
    
    # Calculate statistics
    print(f"\n📈 Comparison Results:")
    print(f"   Average Duration: {sum(m.total_duration for m in all_metrics) / len(all_metrics):.4f}s")
    print(f"   Best Duration: {min(m.total_duration for m in all_metrics):.4f}s")
    print(f"   Worst Duration: {max(m.total_duration for m in all_metrics):.4f}s")
    
    # Find best run
    best = min(all_metrics, key=lambda m: m.total_duration)
    print(f"\n🏆 Best run metrics:")
    print(f"   Duration: {best.total_duration:.4f}s")
    print(f"   Memory: {best.memory_used_mb:.2f} MB")
    print(f"   CPU: {best.avg_cpu_percent:.2f}%")
    
    return all_metrics


async def generate_custom_report():
    """Example: Generate a custom report format."""
    print("\n📄 Generating custom report...")
    
    metrics = await run_custom_benchmark()
    
    # Create custom report
    print("\n" + "="*60)
    print("CUSTOM BENCHMARK REPORT".center(60))
    print("="*60)
    
    # Calculate custom metrics
    efficiency_score = (metrics.throughput * 100) / (metrics.memory_used_mb + 1)
    
    print(f"\n🎯 Custom Metrics:")
    print(f"   Efficiency Score: {efficiency_score:.2f}")
    print(f"   Memory Efficiency: {metrics.news_scraped / (metrics.memory_used_mb + 1):.2f} news/MB")
    print(f"   Time per News: {(metrics.total_duration / metrics.news_scraped * 1000):.2f} ms")
    
    # Generate standard reports
    reporter = BenchmarkReporter(metrics)
    reporter.print_console_report()
    
    return metrics


async def main():
    """Main example entry point."""
    print("\n" + "="*80)
    print("BENCHMARK SYSTEM - USAGE EXAMPLES".center(80))
    print("="*80)
    
    # Example 1: Single run
    print("\n" + "="*80)
    print("EXAMPLE 1: Single Benchmark Run".center(80))
    print("="*80)
    await run_custom_benchmark()
    
    # Example 2: Multiple runs comparison
    print("\n" + "="*80)
    print("EXAMPLE 2: Multiple Runs Comparison".center(80))
    print("="*80)
    await compare_multiple_runs(3)
    
    # Example 3: Custom report
    print("\n" + "="*80)
    print("EXAMPLE 3: Custom Report Generation".center(80))
    print("="*80)
    await generate_custom_report()
    
    print("\n✅ All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
