"""
Performance metrics collection module for async news scraper benchmarks.
"""
import asyncio
import time
import tracemalloc
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import psutil


@dataclass
class RequestMetrics:
    """Metrics for individual HTTP requests."""
    url: str
    start_time: float
    end_time: float
    success: bool
    error: Optional[str] = None
    
    @property
    def duration(self) -> float:
        """Request duration in seconds."""
        return self.end_time - self.start_time


@dataclass
class BenchmarkMetrics:
    """Comprehensive benchmark metrics for the scraper."""
    
    # Timing metrics
    start_time: float = 0.0
    end_time: float = 0.0
    
    # Request metrics
    requests: List[RequestMetrics] = field(default_factory=list)
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # Memory metrics
    memory_start: int = 0
    memory_peak: int = 0
    memory_end: int = 0
    tracemalloc_peak: int = 0
    
    # CPU metrics
    cpu_percent_samples: List[float] = field(default_factory=list)
    cpu_times_start: Optional[psutil._common.pcputimes] = None
    cpu_times_end: Optional[psutil._common.pcputimes] = None
    
    # Network metrics
    network_start: Optional[psutil._common.snetio] = None
    network_end: Optional[psutil._common.snetio] = None
    
    # Database metrics
    news_scraped: int = 0
    news_saved: int = 0
    
    @property
    def total_duration(self) -> float:
        """Total execution time in seconds."""
        return self.end_time - self.start_time
    
    @property
    def avg_request_duration(self) -> float:
        """Average request duration in seconds."""
        if not self.requests:
            return 0.0
        return sum(r.duration for r in self.requests) / len(self.requests)
    
    @property
    def min_request_duration(self) -> float:
        """Minimum request duration in seconds."""
        if not self.requests:
            return 0.0
        return min(r.duration for r in self.requests)
    
    @property
    def max_request_duration(self) -> float:
        """Maximum request duration in seconds."""
        if not self.requests:
            return 0.0
        return max(r.duration for r in self.requests)
    
    @property
    def throughput(self) -> float:
        """Requests per second."""
        if self.total_duration == 0:
            return 0.0
        return self.total_requests / self.total_duration
    
    @property
    def success_rate(self) -> float:
        """Success rate as percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def memory_used_mb(self) -> float:
        """Memory used during execution in MB."""
        return (self.memory_peak - self.memory_start) / (1024 * 1024)
    
    @property
    def tracemalloc_peak_mb(self) -> float:
        """Peak memory from tracemalloc in MB."""
        return self.tracemalloc_peak / (1024 * 1024)
    
    @property
    def avg_cpu_percent(self) -> float:
        """Average CPU usage percentage."""
        if not self.cpu_percent_samples:
            return 0.0
        return sum(self.cpu_percent_samples) / len(self.cpu_percent_samples)
    
    @property
    def cpu_time_used(self) -> float:
        """Total CPU time used in seconds."""
        if not self.cpu_times_start or not self.cpu_times_end:
            return 0.0
        user_time = self.cpu_times_end.user - self.cpu_times_start.user
        system_time = self.cpu_times_end.system - self.cpu_times_start.system
        return user_time + system_time
    
    @property
    def network_sent_mb(self) -> float:
        """Network data sent in MB."""
        if not self.network_start or not self.network_end:
            return 0.0
        return (self.network_end.bytes_sent - self.network_start.bytes_sent) / (1024 * 1024)
    
    @property
    def network_recv_mb(self) -> float:
        """Network data received in MB."""
        if not self.network_start or not self.network_end:
            return 0.0
        return (self.network_end.bytes_recv - self.network_start.bytes_recv) / (1024 * 1024)


class MetricsCollector:
    """Collects performance metrics during benchmark execution."""
    
    def __init__(self):
        self.metrics = BenchmarkMetrics()
        self.process = psutil.Process()
        self._cpu_monitor_task: Optional[asyncio.Task] = None
        self._monitoring = False
    
    def start(self):
        """Start metrics collection."""
        # Start timing
        self.metrics.start_time = time.perf_counter()
        
        # Start memory tracking
        tracemalloc.start()
        self.metrics.memory_start = self.process.memory_info().rss
        
        # Start CPU tracking
        self.metrics.cpu_times_start = self.process.cpu_times()
        
        # Start network tracking
        try:
            self.metrics.network_start = psutil.net_io_counters()
        except Exception:
            self.metrics.network_start = None
        
        # Start CPU monitoring
        self._monitoring = True
    
    async def start_cpu_monitoring(self):
        """Start async CPU monitoring task."""
        self._cpu_monitor_task = asyncio.create_task(self._monitor_cpu())
    
    async def _monitor_cpu(self):
        """Monitor CPU usage periodically."""
        while self._monitoring:
            try:
                cpu_percent = self.process.cpu_percent(interval=0.1)
                self.metrics.cpu_percent_samples.append(cpu_percent)
                await asyncio.sleep(0.1)
            except Exception:
                break
    
    def record_request(self, url: str, start_time: float, end_time: float, 
                      success: bool, error: Optional[str] = None):
        """Record metrics for a single request."""
        request_metric = RequestMetrics(
            url=url,
            start_time=start_time,
            end_time=end_time,
            success=success,
            error=error
        )
        self.metrics.requests.append(request_metric)
        self.metrics.total_requests += 1
        if success:
            self.metrics.successful_requests += 1
        else:
            self.metrics.failed_requests += 1
    
    async def stop(self):
        """Stop metrics collection."""
        # Stop CPU monitoring
        self._monitoring = False
        if self._cpu_monitor_task:
            await self._cpu_monitor_task
        
        # End timing
        self.metrics.end_time = time.perf_counter()
        
        # End memory tracking
        current, peak = tracemalloc.get_traced_memory()
        self.metrics.tracemalloc_peak = peak
        tracemalloc.stop()
        self.metrics.memory_end = self.process.memory_info().rss
        self.metrics.memory_peak = max(self.metrics.memory_end, self.metrics.memory_start)
        
        # End CPU tracking
        self.metrics.cpu_times_end = self.process.cpu_times()
        
        # End network tracking
        try:
            self.metrics.network_end = psutil.net_io_counters()
        except Exception:
            self.metrics.network_end = None
    
    def get_metrics(self) -> BenchmarkMetrics:
        """Get collected metrics."""
        return self.metrics
