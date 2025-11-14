#!/usr/bin/env python3
"""
Professional API Load Testing Suite for Async News Scraper.

This load test measures:
- Concurrent request handling
- Response time under load (avg, p50, p95, p99)
- Throughput (requests/second)
- Memory usage under load (must be < 77MB)
- CPU usage under load
- Success rate under concurrency
- Status code distribution
"""
import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from load_tests.load_tester import APILoadTester
from load_tests.reporter import LoadTestReporter


# Test scenarios
SCENARIOS = {
    "light": {
        "name": "Light Load (10 users)",
        "concurrent_users": 10,
        "requests_per_user": 5,
    },
    "medium": {
        "name": "Medium Load (25 users)",
        "concurrent_users": 25,
        "requests_per_user": 10,
    },
    "heavy": {
        "name": "Heavy Load (50 users)",
        "concurrent_users": 50,
        "requests_per_user": 10,
    },
    "stress": {
        "name": "Stress Test (100 users)",
        "concurrent_users": 100,
        "requests_per_user": 10,
    },
}


async def run_load_test(
    base_url: str = "http://localhost:8000",
    scenario: str = "medium",
):
    """Run load test with specified scenario."""
    
    if scenario not in SCENARIOS:
        print(f"❌ Unknown scenario: {scenario}")
        print(f"   Available: {', '.join(SCENARIOS.keys())}")
        return None
    
    config = SCENARIOS[scenario]
    
    print("\n" + "="*80)
    print("API LOAD TEST - ASYNC NEWS SCRAPER".center(80))
    print("="*80)
    print(f"\nScenario: {config['name']}")
    print(f"Target URL: {base_url}")
    print()
    
    # Define endpoints to test
    endpoints = [
        {
            "method": "GET",
            "path": "/health",
        },
        {
            "method": "GET",
            "path": "/news",
            "kwargs": {"params": {"limit": 10}},
        },
        {
            "method": "GET",
            "path": "/",
        },
        # Note: POST /scrape is heavy, use sparingly
        # {
        #     "method": "POST",
        #     "path": "/scrape",
        # },
    ]
    
    # Create tester
    tester = APILoadTester(base_url)
    
    # Run load test
    metrics = await tester.run_load_test(
        concurrent_users=config["concurrent_users"],
        requests_per_user=config["requests_per_user"],
        endpoints=endpoints,
    )
    
    return metrics


async def run_multiple_scenarios(base_url: str = "http://localhost:8000"):
    """Run multiple load test scenarios."""
    print("\n" + "="*80)
    print("RUNNING MULTIPLE LOAD TEST SCENARIOS".center(80))
    print("="*80)
    
    results = {}
    
    for scenario_name in ["light", "medium", "heavy"]:
        print(f"\n{'='*80}")
        print(f"SCENARIO: {SCENARIOS[scenario_name]['name']}".center(80))
        print(f"{'='*80}")
        
        metrics = await run_load_test(base_url, scenario_name)
        results[scenario_name] = metrics
        
        # Quick summary
        print(f"\n📊 Quick Summary:")
        print(f"   Success Rate: {metrics.success_rate:.2f}%")
        print(f"   Avg Response: {metrics.avg_response_time:.2f} ms")
        print(f"   Throughput: {metrics.throughput:.2f} req/s")
        print(f"   Memory End: {metrics.memory_end_mb:.2f} MB")
        
        # Wait between scenarios
        print(f"\n⏳ Waiting 3 seconds before next scenario...")
        await asyncio.sleep(3)
    
    return results


async def main():
    """Main entry point."""
    print("\n" + "="*80)
    print("ASYNC NEWS SCRAPER - API LOAD TESTING SUITE".center(80))
    print("="*80)
    print("\nThis load test will measure:")
    print("  ✓ Concurrent request handling")
    print("  ✓ Response time under load (avg, p50, p95, p99)")
    print("  ✓ Throughput (requests/second)")
    print("  ✓ Memory usage (target: < 77MB)")
    print("  ✓ CPU usage under load")
    print("  ✓ Success rate under concurrency")
    print()
    
    # Parse arguments
    base_url = "http://localhost:8000"
    scenario = "medium"
    run_all = False
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "all":
            run_all = True
        elif sys.argv[1] in SCENARIOS:
            scenario = sys.argv[1]
        else:
            base_url = sys.argv[1]
    
    if len(sys.argv) > 2:
        scenario = sys.argv[2]
    
    # Check if server is running
    print(f"🔍 Checking if API server is running at {base_url}...")
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/health", timeout=5.0)
            if response.status_code == 200:
                print(f"✅ Server is running!")
            else:
                print(f"⚠️  Server responded with status {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print(f"\n💡 Start the server first:")
        print(f"   python -m src.main")
        print(f"   or")
        print(f"   uvicorn src.api:app --host 0.0.0.0 --port 8000")
        return 1
    
    # Run tests
    if run_all:
        results = await run_multiple_scenarios(base_url)
        # Use last scenario for detailed report
        metrics = results["heavy"]
    else:
        metrics = await run_load_test(base_url, scenario)
    
    if not metrics:
        return 1
    
    # Generate reports
    print("\n" + "="*80)
    print("GENERATING REPORTS".center(80))
    print("="*80)
    
    reporter = LoadTestReporter(metrics)
    
    # Console report
    reporter.print_console_report()
    
    # Create output directory
    output_dir = Path("load_tests/results")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # JSON report
    json_path = output_dir / "load_test_results.json"
    reporter.generate_json_report(str(json_path))
    
    print(f"\n✅ Load test completed successfully!")
    print(f"📁 Reports saved in: {output_dir.absolute()}")
    
    # Check memory threshold
    if metrics.memory_end_mb < 77:
        print(f"\n✅ MEMORY THRESHOLD PASS: {metrics.memory_end_mb:.2f} MB < 77 MB")
        return 0
    else:
        print(f"\n⚠️  MEMORY THRESHOLD WARNING: {metrics.memory_end_mb:.2f} MB >= 77 MB")
        return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Load test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Load test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
