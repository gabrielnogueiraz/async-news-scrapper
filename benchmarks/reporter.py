"""
Professional benchmark report generator.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from benchmarks.metrics import BenchmarkMetrics


class BenchmarkReporter:
    """Generate professional benchmark reports."""
    
    def __init__(self, metrics: BenchmarkMetrics):
        self.metrics = metrics
    
    def print_console_report(self):
        """Print a formatted console report."""
        print("\n" + "="*80)
        print("ASYNC NEWS SCRAPER - PERFORMANCE BENCHMARK REPORT".center(80))
        print("="*80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Execution Summary
        print("\n📊 EXECUTION SUMMARY")
        print("-" * 80)
        print(f"Total Duration:           {self.metrics.total_duration:.4f} seconds")
        print(f"News Scraped:             {self.metrics.news_scraped}")
        print(f"News Saved (New):         {self.metrics.news_saved}")
        print(f"Success Rate:             {self.metrics.success_rate:.2f}%")
        
        # Request Metrics
        print("\n🌐 HTTP REQUEST METRICS")
        print("-" * 80)
        print(f"Total Requests:           {self.metrics.total_requests}")
        print(f"Successful Requests:      {self.metrics.successful_requests}")
        print(f"Failed Requests:          {self.metrics.failed_requests}")
        print(f"Average Request Time:     {self.metrics.avg_request_duration*1000:.2f} ms")
        print(f"Min Request Time:         {self.metrics.min_request_duration*1000:.2f} ms")
        print(f"Max Request Time:         {self.metrics.max_request_duration*1000:.2f} ms")
        print(f"Throughput:               {self.metrics.throughput:.2f} req/s")
        
        # Memory Metrics
        print("\n💾 MEMORY METRICS")
        print("-" * 80)
        print(f"Memory Used (RSS):        {self.metrics.memory_used_mb:.2f} MB")
        print(f"Peak Memory (tracemalloc):{self.metrics.tracemalloc_peak_mb:.2f} MB")
        print(f"Memory Start:             {self.metrics.memory_start / (1024*1024):.2f} MB")
        print(f"Memory End:               {self.metrics.memory_end / (1024*1024):.2f} MB")
        
        # CPU Metrics
        print("\n⚡ CPU METRICS")
        print("-" * 80)
        print(f"Average CPU Usage:        {self.metrics.avg_cpu_percent:.2f}%")
        print(f"CPU Time Used:            {self.metrics.cpu_time_used:.4f} seconds")
        print(f"CPU Samples Collected:    {len(self.metrics.cpu_percent_samples)}")
        if self.metrics.cpu_times_start and self.metrics.cpu_times_end:
            user_time = self.metrics.cpu_times_end.user - self.metrics.cpu_times_start.user
            system_time = self.metrics.cpu_times_end.system - self.metrics.cpu_times_start.system
            print(f"User CPU Time:            {user_time:.4f} seconds")
            print(f"System CPU Time:          {system_time:.4f} seconds")
        
        # Network Metrics
        if self.metrics.network_start and self.metrics.network_end:
            print("\n🌍 NETWORK METRICS")
            print("-" * 80)
            print(f"Data Sent:                {self.metrics.network_sent_mb:.4f} MB")
            print(f"Data Received:            {self.metrics.network_recv_mb:.4f} MB")
            print(f"Total Network I/O:        {self.metrics.network_sent_mb + self.metrics.network_recv_mb:.4f} MB")
        
        # Performance Analysis
        print("\n📈 PERFORMANCE ANALYSIS")
        print("-" * 80)
        
        # I/O vs CPU bound analysis
        cpu_efficiency = (self.metrics.cpu_time_used / self.metrics.total_duration) * 100 if self.metrics.total_duration > 0 else 0
        print(f"CPU Efficiency:           {cpu_efficiency:.2f}%")
        
        if cpu_efficiency < 30:
            bottleneck = "I/O Bound (Good for async operations)"
        elif cpu_efficiency < 70:
            bottleneck = "Balanced I/O and CPU"
        else:
            bottleneck = "CPU Bound (Consider multiprocessing)"
        print(f"Bottleneck Analysis:      {bottleneck}")
        
        # Memory efficiency
        if self.metrics.news_scraped > 0:
            memory_per_news = self.metrics.memory_used_mb / self.metrics.news_scraped
            print(f"Memory per News Item:     {memory_per_news:.4f} MB")
        
        # Request Details
        if self.metrics.requests:
            print("\n🔍 REQUEST DETAILS")
            print("-" * 80)
            for i, req in enumerate(self.metrics.requests, 1):
                status = "✓" if req.success else "✗"
                print(f"{status} Request {i}: {req.url[:60]}... ({req.duration*1000:.2f}ms)")
                if req.error:
                    print(f"  Error: {req.error}")
        
        print("\n" + "="*80)
        print("END OF REPORT".center(80))
        print("="*80 + "\n")
    
    def generate_json_report(self, output_path: str = "benchmark_results.json") -> Dict[str, Any]:
        """Generate a JSON report for programmatic analysis."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_duration_seconds": self.metrics.total_duration,
                "news_scraped": self.metrics.news_scraped,
                "news_saved": self.metrics.news_saved,
                "success_rate_percent": self.metrics.success_rate,
            },
            "requests": {
                "total": self.metrics.total_requests,
                "successful": self.metrics.successful_requests,
                "failed": self.metrics.failed_requests,
                "avg_duration_ms": self.metrics.avg_request_duration * 1000,
                "min_duration_ms": self.metrics.min_request_duration * 1000,
                "max_duration_ms": self.metrics.max_request_duration * 1000,
                "throughput_req_per_sec": self.metrics.throughput,
            },
            "memory": {
                "used_mb": self.metrics.memory_used_mb,
                "peak_mb": self.metrics.tracemalloc_peak_mb,
                "start_mb": self.metrics.memory_start / (1024 * 1024),
                "end_mb": self.metrics.memory_end / (1024 * 1024),
            },
            "cpu": {
                "avg_percent": self.metrics.avg_cpu_percent,
                "time_used_seconds": self.metrics.cpu_time_used,
                "samples_collected": len(self.metrics.cpu_percent_samples),
            },
            "network": {
                "sent_mb": self.metrics.network_sent_mb,
                "received_mb": self.metrics.network_recv_mb,
                "total_mb": self.metrics.network_sent_mb + self.metrics.network_recv_mb,
            } if self.metrics.network_start and self.metrics.network_end else None,
            "request_details": [
                {
                    "url": req.url,
                    "duration_ms": req.duration * 1000,
                    "success": req.success,
                    "error": req.error,
                }
                for req in self.metrics.requests
            ],
        }
        
        # Save to file
        output_file = Path(output_path)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 JSON report saved to: {output_file.absolute()}")
        
        return report
    
    def generate_markdown_report(self, output_path: str = "benchmark_results.md"):
        """Generate a Markdown report for documentation."""
        md_content = f"""# Async News Scraper - Benchmark Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 Execution Summary

| Metric | Value |
|--------|-------|
| Total Duration | {self.metrics.total_duration:.4f} seconds |
| News Scraped | {self.metrics.news_scraped} |
| News Saved (New) | {self.metrics.news_saved} |
| Success Rate | {self.metrics.success_rate:.2f}% |

---

## 🌐 HTTP Request Metrics

| Metric | Value |
|--------|-------|
| Total Requests | {self.metrics.total_requests} |
| Successful Requests | {self.metrics.successful_requests} |
| Failed Requests | {self.metrics.failed_requests} |
| Average Request Time | {self.metrics.avg_request_duration*1000:.2f} ms |
| Min Request Time | {self.metrics.min_request_duration*1000:.2f} ms |
| Max Request Time | {self.metrics.max_request_duration*1000:.2f} ms |
| Throughput | {self.metrics.throughput:.2f} req/s |

---

## 💾 Memory Metrics

| Metric | Value |
|--------|-------|
| Memory Used (RSS) | {self.metrics.memory_used_mb:.2f} MB |
| Peak Memory (tracemalloc) | {self.metrics.tracemalloc_peak_mb:.2f} MB |
| Memory Start | {self.metrics.memory_start / (1024*1024):.2f} MB |
| Memory End | {self.metrics.memory_end / (1024*1024):.2f} MB |

---

## ⚡ CPU Metrics

| Metric | Value |
|--------|-------|
| Average CPU Usage | {self.metrics.avg_cpu_percent:.2f}% |
| CPU Time Used | {self.metrics.cpu_time_used:.4f} seconds |
| CPU Samples Collected | {len(self.metrics.cpu_percent_samples)} |
"""

        if self.metrics.network_start and self.metrics.network_end:
            md_content += f"""
---

## 🌍 Network Metrics

| Metric | Value |
|--------|-------|
| Data Sent | {self.metrics.network_sent_mb:.4f} MB |
| Data Received | {self.metrics.network_recv_mb:.4f} MB |
| Total Network I/O | {self.metrics.network_sent_mb + self.metrics.network_recv_mb:.4f} MB |
"""

        cpu_efficiency = (self.metrics.cpu_time_used / self.metrics.total_duration) * 100 if self.metrics.total_duration > 0 else 0
        if cpu_efficiency < 30:
            bottleneck = "I/O Bound (Good for async operations)"
        elif cpu_efficiency < 70:
            bottleneck = "Balanced I/O and CPU"
        else:
            bottleneck = "CPU Bound (Consider multiprocessing)"

        md_content += f"""
---

## 📈 Performance Analysis

- **CPU Efficiency:** {cpu_efficiency:.2f}%
- **Bottleneck Analysis:** {bottleneck}
"""

        if self.metrics.news_scraped > 0:
            memory_per_news = self.metrics.memory_used_mb / self.metrics.news_scraped
            md_content += f"- **Memory per News Item:** {memory_per_news:.4f} MB\n"

        md_content += "\n---\n\n*Report generated by Async News Scraper Benchmark Suite*\n"
        
        # Save to file
        output_file = Path(output_path)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"📄 Markdown report saved to: {output_file.absolute()}")
