"""
Professional load testing system for the Async News Scraper API.
"""
import asyncio
import time
import tracemalloc
from typing import List, Optional
import psutil
import httpx

from load_tests.metrics import LoadTestMetrics, RequestResult


class APILoadTester:
    """Load tester for API endpoints with concurrency support."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.metrics = LoadTestMetrics()
        self.process = psutil.Process()
        self._monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
    
    def start_monitoring(self):
        """Start system metrics monitoring."""
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
        
        self._monitoring = True
    
    async def start_cpu_monitoring(self):
        """Start async CPU monitoring."""
        self._monitor_task = asyncio.create_task(self._monitor_cpu())
    
    async def _monitor_cpu(self):
        """Monitor CPU usage periodically."""
        while self._monitoring:
            try:
                cpu_percent = self.process.cpu_percent(interval=0.1)
                self.metrics.cpu_samples.append(cpu_percent)
                await asyncio.sleep(0.1)
            except Exception:
                break
    
    async def stop_monitoring(self):
        """Stop system metrics monitoring."""
        self._monitoring = False
        if self._monitor_task:
            await self._monitor_task
        
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
    
    async def make_request(
        self,
        client: httpx.AsyncClient,
        method: str,
        endpoint: str,
        **kwargs
    ) -> RequestResult:
        """Make a single HTTP request and record metrics."""
        url = f"{self.base_url}{endpoint}"
        start_time = time.perf_counter()
        timestamp = start_time
        
        try:
            response = await client.request(method, url, **kwargs)
            end_time = time.perf_counter()
            
            return RequestResult(
                endpoint=endpoint,
                method=method,
                status_code=response.status_code,
                duration=end_time - start_time,
                timestamp=timestamp,
                success=200 <= response.status_code < 300,
                response_size=len(response.content),
            )
        except Exception as e:
            end_time = time.perf_counter()
            return RequestResult(
                endpoint=endpoint,
                method=method,
                status_code=0,
                duration=end_time - start_time,
                timestamp=timestamp,
                success=False,
                error=str(e),
            )
    
    async def simulate_user(
        self,
        user_id: int,
        requests_per_user: int,
        endpoints: List[dict]
    ) -> List[RequestResult]:
        """Simulate a single user making multiple requests."""
        results = []
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for i in range(requests_per_user):
                # Cycle through endpoints
                endpoint_config = endpoints[i % len(endpoints)]
                
                result = await self.make_request(
                    client,
                    endpoint_config['method'],
                    endpoint_config['path'],
                    **endpoint_config.get('kwargs', {})
                )
                results.append(result)
                
                # Small delay between requests from same user
                if i < requests_per_user - 1:
                    await asyncio.sleep(0.1)
        
        return results
    
    async def run_load_test(
        self,
        concurrent_users: int,
        requests_per_user: int,
        endpoints: List[dict]
    ) -> LoadTestMetrics:
        """
        Run load test with concurrent users.
        
        Args:
            concurrent_users: Number of concurrent users to simulate
            requests_per_user: Number of requests each user makes
            endpoints: List of endpoint configurations
                      [{'method': 'GET', 'path': '/news', 'kwargs': {...}}]
        
        Returns:
            LoadTestMetrics with all collected metrics
        """
        self.metrics.total_users = concurrent_users
        self.metrics.requests_per_user = requests_per_user
        
        print(f"\n🚀 Starting load test:")
        print(f"   Concurrent Users: {concurrent_users}")
        print(f"   Requests per User: {requests_per_user}")
        print(f"   Total Requests: {concurrent_users * requests_per_user}")
        print(f"   Endpoints: {len(endpoints)}")
        
        # Start monitoring
        self.start_monitoring()
        await self.start_cpu_monitoring()
        
        try:
            # Create tasks for all users
            tasks = [
                self.simulate_user(user_id, requests_per_user, endpoints)
                for user_id in range(concurrent_users)
            ]
            
            # Run all users concurrently
            print(f"\n⚡ Executing concurrent requests...")
            all_results = await asyncio.gather(*tasks)
            
            # Flatten results
            for user_results in all_results:
                self.metrics.requests.extend(user_results)
            
        finally:
            await self.stop_monitoring()
        
        print(f"✅ Load test completed!")
        
        return self.metrics
