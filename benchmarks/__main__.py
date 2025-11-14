"""
Allow running benchmarks as a module: python -m benchmarks
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import and run the main benchmark
from run_benchmark import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
