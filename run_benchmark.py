#!/usr/bin/env python3
"""
Professional benchmark suite for Async News Scraper.

This benchmark measures:
- Total execution time
- Average request latency
- Peak memory usage (RSS and tracemalloc)
- CPU usage (% and time)
- Throughput (requests/second)
- Network I/O (optional)
"""
import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.db import init_db, get_db_context
from benchmarks.metrics import MetricsCollector
from benchmarks.scraper_instrumented import InstrumentedG1Scraper
from benchmarks.reporter import BenchmarkReporter


async def run_single_benchmark():
    """Run a single benchmark iteration."""
    print("🚀 Starting Async News Scraper Benchmark...")
    print("-" * 80)
    
    # Initialize database
    print("📦 Initializing database...")
    await init_db()
    
    # Create metrics collector
    collector = MetricsCollector()
    
    # Start metrics collection
    print("📊 Starting metrics collection...")
    collector.start()
    
    # Start CPU monitoring in background
    await collector.start_cpu_monitoring()
    
    try:
        # Run the scraper
        print("🔍 Running scraper...")
        async with get_db_context() as db:
            scraper = InstrumentedG1Scraper(db, collector)
            news_scraped, news_saved = await scraper.scrape()
            
            # Record results
            collector.metrics.news_scraped = news_scraped
            collector.metrics.news_saved = news_saved
            
            print(f"✅ Scraping completed: {news_scraped} news found, {news_saved} new saved")
    
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        raise
    
    finally:
        # Stop metrics collection
        print("⏹️  Stopping metrics collection...")
        await collector.stop()
    
    return collector.get_metrics()


async def run_multiple_benchmarks(iterations: int = 3):
    """Run multiple benchmark iterations for statistical analysis."""
    print(f"\n{'='*80}")
    print(f"RUNNING {iterations} BENCHMARK ITERATIONS".center(80))
    print(f"{'='*80}\n")
    
    all_metrics = []
    
    for i in range(iterations):
        print(f"\n{'='*80}")
        print(f"ITERATION {i+1}/{iterations}".center(80))
        print(f"{'='*80}\n")
        
        metrics = await run_single_benchmark()
        all_metrics.append(metrics)
        
        # Print quick summary
        print(f"\n📈 Iteration {i+1} Summary:")
        print(f"   Duration: {metrics.total_duration:.4f}s")
        print(f"   Throughput: {metrics.throughput:.2f} req/s")
        print(f"   Memory: {metrics.memory_used_mb:.2f} MB")
        print(f"   CPU: {metrics.avg_cpu_percent:.2f}%")
        
        # Wait between iterations
        if i < iterations - 1:
            print(f"\n⏳ Waiting 2 seconds before next iteration...")
            await asyncio.sleep(2)
    
    # Calculate aggregate statistics
    print(f"\n{'='*80}")
    print("AGGREGATE STATISTICS".center(80))
    print(f"{'='*80}\n")
    
    avg_duration = sum(m.total_duration for m in all_metrics) / len(all_metrics)
    avg_throughput = sum(m.throughput for m in all_metrics) / len(all_metrics)
    avg_memory = sum(m.memory_used_mb for m in all_metrics) / len(all_metrics)
    avg_cpu = sum(m.avg_cpu_percent for m in all_metrics) / len(all_metrics)
    
    print(f"Average Duration:    {avg_duration:.4f} seconds")
    print(f"Average Throughput:  {avg_throughput:.2f} req/s")
    print(f"Average Memory:      {avg_memory:.2f} MB")
    print(f"Average CPU:         {avg_cpu:.2f}%")
    
    # Return the best performing iteration (fastest)
    best_metrics = min(all_metrics, key=lambda m: m.total_duration)
    print(f"\n🏆 Best iteration: {best_metrics.total_duration:.4f}s")
    
    return best_metrics


async def main():
    """Main benchmark entry point."""
    print("\n" + "="*80)
    print("ASYNC NEWS SCRAPER - PROFESSIONAL BENCHMARK SUITE".center(80))
    print("="*80)
    print("\nThis benchmark will measure:")
    print("  ✓ Total execution time")
    print("  ✓ Average request latency")
    print("  ✓ Peak memory usage (RSS + tracemalloc)")
    print("  ✓ CPU usage (% and time)")
    print("  ✓ Throughput (requests/second)")
    print("  ✓ Network I/O")
    print("  ✓ Success rate")
    print()
    
    # Check if multiple iterations requested
    iterations = 1
    if len(sys.argv) > 1:
        try:
            iterations = int(sys.argv[1])
            if iterations < 1:
                iterations = 1
        except ValueError:
            print("⚠️  Invalid iteration count, using default (1)")
    
    # Run benchmark
    if iterations > 1:
        metrics = await run_multiple_benchmarks(iterations)
    else:
        metrics = await run_single_benchmark()
    
    # Generate reports
    print("\n" + "="*80)
    print("GENERATING REPORTS".center(80))
    print("="*80)
    
    reporter = BenchmarkReporter(metrics)
    
    # Console report
    reporter.print_console_report()
    
    # Create benchmarks output directory
    output_dir = Path("benchmarks/results")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # JSON report
    json_path = output_dir / "benchmark_results.json"
    reporter.generate_json_report(str(json_path))
    
    # Markdown report
    md_path = output_dir / "benchmark_results.md"
    reporter.generate_markdown_report(str(md_path))
    
    print("\n✅ Benchmark completed successfully!")
    print(f"📁 Reports saved in: {output_dir.absolute()}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
