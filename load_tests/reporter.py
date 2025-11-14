"""
Professional load test report generator.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from load_tests.metrics import LoadTestMetrics


class LoadTestReporter:
    """Generate professional load test reports."""
    
    def __init__(self, metrics: LoadTestMetrics):
        self.metrics = metrics
    
    def print_console_report(self):
        """Print formatted console report."""
        print("\n" + "="*80)
        print("API LOAD TEST - PERFORMANCE REPORT".center(80))
        print("="*80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Test Configuration
        print("\n⚙️  TEST CONFIGURATION")
        print("-" * 80)
        print(f"Concurrent Users:         {self.metrics.total_users}")
        print(f"Requests per User:        {self.metrics.requests_per_user}")
        print(f"Total Requests:           {self.metrics.total_requests}")
        print(f"Test Duration:            {self.metrics.total_duration:.4f} seconds")
        
        # Request Summary
        print("\n📊 REQUEST SUMMARY")
        print("-" * 80)
        print(f"Successful Requests:      {self.metrics.successful_requests}")
        print(f"Failed Requests:          {self.metrics.failed_requests}")
        print(f"Success Rate:             {self.metrics.success_rate:.2f}%")
        print(f"Throughput:               {self.metrics.throughput:.2f} req/s")
        
        # Response Time Statistics
        print("\n⏱️  RESPONSE TIME STATISTICS")
        print("-" * 80)
        print(f"Average Response Time:    {self.metrics.avg_response_time:.2f} ms")
        print(f"Min Response Time:        {self.metrics.min_response_time:.2f} ms")
        print(f"Max Response Time:        {self.metrics.max_response_time:.2f} ms")
        print(f"P50 (Median):             {self.metrics.p50_response_time:.2f} ms")
        print(f"P95:                      {self.metrics.p95_response_time:.2f} ms")
        print(f"P99:                      {self.metrics.p99_response_time:.2f} ms")
        
        # Memory Metrics
        print("\n💾 MEMORY METRICS")
        print("-" * 80)
        print(f"Memory Start:             {self.metrics.memory_start / (1024*1024):.2f} MB")
        print(f"Memory Peak:              {self.metrics.memory_peak / (1024*1024):.2f} MB")
        print(f"Memory End:               {self.metrics.memory_end_mb:.2f} MB")
        print(f"Memory Used:              {self.metrics.memory_used_mb:.2f} MB")
        print(f"Tracemalloc Peak:         {self.metrics.tracemalloc_peak_mb:.2f} MB")
        
        # Memory threshold check
        if self.metrics.memory_end_mb < 77:
            print(f"✅ Memory End < 77MB:     PASS ({self.metrics.memory_end_mb:.2f} MB)")
        else:
            print(f"❌ Memory End < 77MB:     FAIL ({self.metrics.memory_end_mb:.2f} MB)")
        
        # CPU Metrics
        print("\n⚡ CPU METRICS")
        print("-" * 80)
        print(f"Average CPU Usage:        {self.metrics.avg_cpu_percent:.2f}%")
        print(f"CPU Samples Collected:    {len(self.metrics.cpu_samples)}")
        
        # Status Code Distribution
        print("\n📈 STATUS CODE DISTRIBUTION")
        print("-" * 80)
        for status_code, count in sorted(self.metrics.requests_by_status.items()):
            percentage = (count / self.metrics.total_requests) * 100
            status_emoji = "✅" if 200 <= status_code < 300 else "❌"
            print(f"{status_emoji} {status_code}: {count:>6} ({percentage:>6.2f}%)")
        
        # Endpoint Performance
        print("\n🎯 ENDPOINT PERFORMANCE")
        print("-" * 80)
        for endpoint, avg_time in self.metrics.avg_response_time_by_endpoint.items():
            count = self.metrics.requests_by_endpoint[endpoint]
            print(f"{endpoint:<30} {avg_time:>8.2f} ms  ({count} requests)")
        
        # Performance Analysis
        print("\n📊 PERFORMANCE ANALYSIS")
        print("-" * 80)
        
        # Concurrent users per second
        concurrent_rps = self.metrics.throughput / self.metrics.total_users if self.metrics.total_users > 0 else 0
        print(f"Requests/sec per User:    {concurrent_rps:.2f}")
        
        # Memory per request
        if self.metrics.total_requests > 0:
            memory_per_req = self.metrics.memory_used_mb / self.metrics.total_requests
            print(f"Memory per Request:       {memory_per_req:.4f} MB")
        
        # Latency assessment
        if self.metrics.avg_response_time < 100:
            latency_rating = "Excellent (< 100ms)"
        elif self.metrics.avg_response_time < 300:
            latency_rating = "Good (< 300ms)"
        elif self.metrics.avg_response_time < 1000:
            latency_rating = "Acceptable (< 1s)"
        else:
            latency_rating = "Poor (> 1s)"
        print(f"Latency Rating:           {latency_rating}")
        
        # Concurrency handling
        if self.metrics.success_rate >= 99:
            concurrency_rating = "Excellent (≥99% success)"
        elif self.metrics.success_rate >= 95:
            concurrency_rating = "Good (≥95% success)"
        elif self.metrics.success_rate >= 90:
            concurrency_rating = "Fair (≥90% success)"
        else:
            concurrency_rating = "Poor (<90% success)"
        print(f"Concurrency Handling:     {concurrency_rating}")
        
        print("\n" + "="*80)
        print("END OF REPORT".center(80))
        print("="*80 + "\n")
    
    def generate_json_report(self, output_path: str = "load_test_results.json") -> Dict[str, Any]:
        """Generate JSON report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "configuration": {
                "concurrent_users": self.metrics.total_users,
                "requests_per_user": self.metrics.requests_per_user,
                "total_requests": self.metrics.total_requests,
                "test_duration_seconds": self.metrics.total_duration,
            },
            "summary": {
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "success_rate_percent": self.metrics.success_rate,
                "throughput_req_per_sec": self.metrics.throughput,
            },
            "response_times": {
                "avg_ms": self.metrics.avg_response_time,
                "min_ms": self.metrics.min_response_time,
                "max_ms": self.metrics.max_response_time,
                "p50_ms": self.metrics.p50_response_time,
                "p95_ms": self.metrics.p95_response_time,
                "p99_ms": self.metrics.p99_response_time,
            },
            "memory": {
                "start_mb": self.metrics.memory_start / (1024 * 1024),
                "peak_mb": self.metrics.memory_peak / (1024 * 1024),
                "end_mb": self.metrics.memory_end_mb,
                "used_mb": self.metrics.memory_used_mb,
                "tracemalloc_peak_mb": self.metrics.tracemalloc_peak_mb,
                "memory_threshold_77mb_pass": self.metrics.memory_end_mb < 77,
            },
            "cpu": {
                "avg_percent": self.metrics.avg_cpu_percent,
                "samples_collected": len(self.metrics.cpu_samples),
            },
            "status_codes": self.metrics.requests_by_status,
            "endpoints": {
                "counts": self.metrics.requests_by_endpoint,
                "avg_response_times_ms": self.metrics.avg_response_time_by_endpoint,
            },
        }
        
        output_file = Path(output_path)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 JSON report saved to: {output_file.absolute()}")
        
        return report
