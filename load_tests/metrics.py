"""
Load testing metrics collection for API endpoints.
"""
import time
import tracemalloc
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import psutil


@dataclass
class RequestResult:
    """Result of a single API request."""
    endpoint: str
    method: str
    status_code: int
    duration: float  # seconds
    timestamp: float
    success: bool
    error: Optional[str] = None
    response_size: int = 0  # bytes


@dataclass
class LoadTestMetrics:
    """Comprehensive load test metrics."""
    
    # Test configuration
    total_users: int = 0
    requests_per_user: int = 0
    
    # Timing
    start_time: float = 0.0
    end_time: float = 0.0
    
    # Requests
    requests: List[RequestResult] = field(default_factory=list)
    
    # Memory
    memory_start: int = 0
    memory_peak: int = 0
    memory_end: int = 0
    tracemalloc_peak: int = 0
    
    # CPU
    cpu_samples: List[float] = field(default_factory=list)
    cpu_times_start: Optional[psutil._common.pcputimes] = None
    cpu_times_end: Optional[psutil._common.pcputimes] = None
    
    # Network
    network_start: Optional[psutil._common.snetio] = None
    network_end: Optional[psutil._common.snetio] = None
    
    @property
    def total_duration(self) -> float:
        """Total test duration in seconds."""
        return self.end_time - self.start_time
    
    @property
    def total_requests(self) -> int:
        """Total number of requests made."""
        return len(self.requests)
    
    @property
    def successful_requests(self) -> int:
        """Number of successful requests."""
        return sum(1 for r in self.requests if r.success)
    
    @property
    def failed_requests(self) -> int:
        """Number of failed requests."""
        return sum(1 for r in self.requests if not r.success)
    
    @property
    def success_rate(self) -> float:
        """Success rate as percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def avg_response_time(self) -> float:
        """Average response time in milliseconds."""
        if not self.requests:
            return 0.0
        return (sum(r.duration for r in self.requests) / len(self.requests)) * 1000
    
    @property
    def min_response_time(self) -> float:
        """Minimum response time in milliseconds."""
        if not self.requests:
            return 0.0
        return min(r.duration for r in self.requests) * 1000
    
    @property
    def max_response_time(self) -> float:
        """Maximum response time in milliseconds."""
        if not self.requests:
            return 0.0
        return max(r.duration for r in self.requests) * 1000
    
    @property
    def p50_response_time(self) -> float:
        """50th percentile (median) response time in milliseconds."""
        if not self.requests:
            return 0.0
        sorted_durations = sorted(r.duration for r in self.requests)
        idx = len(sorted_durations) // 2
        return sorted_durations[idx] * 1000
    
    @property
    def p95_response_time(self) -> float:
        """95th percentile response time in milliseconds."""
        if not self.requests:
            return 0.0
        sorted_durations = sorted(r.duration for r in self.requests)
        idx = int(len(sorted_durations) * 0.95)
        return sorted_durations[idx] * 1000
    
    @property
    def p99_response_time(self) -> float:
        """99th percentile response time in milliseconds."""
        if not self.requests:
            return 0.0
        sorted_durations = sorted(r.duration for r in self.requests)
        idx = int(len(sorted_durations) * 0.99)
        return sorted_durations[idx] * 1000
    
    @property
    def throughput(self) -> float:
        """Requests per second."""
        if self.total_duration == 0:
            return 0.0
        return self.total_requests / self.total_duration
    
    @property
    def memory_used_mb(self) -> float:
        """Memory used during test in MB."""
        return (self.memory_peak - self.memory_start) / (1024 * 1024)
    
    @property
    def memory_end_mb(self) -> float:
        """Final memory usage in MB."""
        return self.memory_end / (1024 * 1024)
    
    @property
    def tracemalloc_peak_mb(self) -> float:
        """Peak memory from tracemalloc in MB."""
        return self.tracemalloc_peak / (1024 * 1024)
    
    @property
    def avg_cpu_percent(self) -> float:
        """Average CPU usage percentage."""
        if not self.cpu_samples:
            return 0.0
        return sum(self.cpu_samples) / len(self.cpu_samples)
    
    @property
    def requests_by_status(self) -> Dict[int, int]:
        """Count of requests by status code."""
        status_counts = {}
        for req in self.requests:
            status_counts[req.status_code] = status_counts.get(req.status_code, 0) + 1
        return status_counts
    
    @property
    def requests_by_endpoint(self) -> Dict[str, int]:
        """Count of requests by endpoint."""
        endpoint_counts = {}
        for req in self.requests:
            endpoint_counts[req.endpoint] = endpoint_counts.get(req.endpoint, 0) + 1
        return endpoint_counts
    
    @property
    def avg_response_time_by_endpoint(self) -> Dict[str, float]:
        """Average response time by endpoint in milliseconds."""
        endpoint_times = {}
        endpoint_counts = {}
        
        for req in self.requests:
            if req.endpoint not in endpoint_times:
                endpoint_times[req.endpoint] = 0.0
                endpoint_counts[req.endpoint] = 0
            endpoint_times[req.endpoint] += req.duration
            endpoint_counts[req.endpoint] += 1
        
        return {
            endpoint: (endpoint_times[endpoint] / endpoint_counts[endpoint]) * 1000
            for endpoint in endpoint_times
        }
