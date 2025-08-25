#!/usr/bin/env python
"""
Memory profiling script for PolicyEngine test files.
Identifies which test files consume the most memory.
"""

import os
import sys
import subprocess
import tracemalloc
import gc
import json
import psutil
import time
from pathlib import Path
from typing import Dict, List, Tuple
import argparse

def get_memory_usage() -> float:
    """Get current memory usage in MB."""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024

def run_single_test(test_path: str, verbose: bool = False) -> Dict:
    """Run a single test file and measure memory usage."""
    gc.collect()
    start_memory = get_memory_usage()
    start_time = time.time()
    
    # Run the test
    cmd = ["policyengine-core", "test", test_path, "-c", "policyengine_us"]
    if verbose:
        print(f"Running: {test_path}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout per test
        )
        success = result.returncode == 0
        error = result.stderr if not success else None
    except subprocess.TimeoutExpired:
        success = False
        error = "Timeout after 60 seconds"
    except Exception as e:
        success = False
        error = str(e)
    
    gc.collect()
    end_memory = get_memory_usage()
    end_time = time.time()
    
    memory_used = end_memory - start_memory
    duration = end_time - start_time
    
    return {
        "path": test_path,
        "memory_mb": round(memory_used, 2),
        "peak_memory_mb": round(end_memory, 2),
        "duration_sec": round(duration, 2),
        "success": success,
        "error": error
    }

def find_yaml_test_files(base_path: str, pattern: str = None) -> List[str]:
    """Find all YAML test files in the given path."""
    test_files = []
    base = Path(base_path)
    
    # Look for YAML files in the test directories
    for yaml_file in base.rglob("*.yaml"):
        file_path = str(yaml_file)
        # Skip non-test files
        if "/parameters/" in file_path or "/variables/" in file_path:
            continue
        if pattern and pattern not in file_path:
            continue
        test_files.append(file_path)
    
    return sorted(test_files)

def find_test_directories(base_path: str) -> List[str]:
    """Find all test directories that contain YAML files."""
    directories = set()
    base = Path(base_path)
    
    for yaml_file in base.rglob("*.yaml"):
        file_path = str(yaml_file)
        # Skip non-test files
        if "/parameters/" in file_path or "/variables/" in file_path:
            continue
        # Add the parent directory
        directories.add(str(yaml_file.parent))
    
    return sorted(directories)

def profile_tests(test_paths: List[str], verbose: bool = False) -> List[Dict]:
    """Profile memory usage for multiple test files."""
    results = []
    total = len(test_paths)
    
    print(f"Profiling {total} test files/directories...")
    print("-" * 60)
    
    for i, test_path in enumerate(test_paths, 1):
        if verbose:
            print(f"[{i}/{total}] Testing: {test_path}")
        
        result = run_single_test(test_path, verbose)
        results.append(result)
        
        # Print progress for high memory usage
        if result["memory_mb"] > 100:
            print(f"⚠️  High memory: {test_path}: {result['memory_mb']} MB")
        
        # Force garbage collection between tests
        gc.collect()
        time.sleep(0.1)  # Brief pause to let system recover
    
    return results

def analyze_results(results: List[Dict]) -> None:
    """Analyze and print test profiling results."""
    print("\n" + "=" * 80)
    print("MEMORY PROFILING RESULTS")
    print("=" * 80)
    
    # Sort by memory usage
    by_memory = sorted(results, key=lambda x: x["memory_mb"], reverse=True)
    
    print("\n📊 TOP 20 MEMORY CONSUMERS:")
    print("-" * 60)
    print(f"{'Test Path':<50} {'Memory (MB)':>12} {'Time (s)':>10}")
    print("-" * 60)
    
    for result in by_memory[:20]:
        path = result["path"]
        if len(path) > 50:
            path = "..." + path[-47:]
        status = "✓" if result["success"] else "✗"
        print(f"{status} {path:<48} {result['memory_mb']:>11.1f} {result['duration_sec']:>9.1f}")
    
    # Statistics
    total_memory = sum(r["memory_mb"] for r in results)
    avg_memory = total_memory / len(results) if results else 0
    max_memory = max(r["memory_mb"] for r in results) if results else 0
    failed = [r for r in results if not r["success"]]
    
    print("\n📈 STATISTICS:")
    print("-" * 60)
    print(f"Total tests profiled: {len(results)}")
    print(f"Failed tests: {len(failed)}")
    print(f"Total memory used: {total_memory:.1f} MB")
    print(f"Average memory per test: {avg_memory:.1f} MB")
    print(f"Maximum memory used: {max_memory:.1f} MB")
    
    # Find problematic tests
    high_memory = [r for r in results if r["memory_mb"] > 200]
    if high_memory:
        print("\n⚠️  HIGH MEMORY TESTS (>200 MB):")
        print("-" * 60)
        for result in high_memory:
            print(f"  {result['path']}: {result['memory_mb']:.1f} MB")
    
    # Group by directory to find problematic modules
    by_directory = {}
    for result in results:
        dir_path = os.path.dirname(result["path"])
        if dir_path not in by_directory:
            by_directory[dir_path] = []
        by_directory[dir_path].append(result["memory_mb"])
    
    dir_totals = {
        dir_path: sum(memories) 
        for dir_path, memories in by_directory.items()
    }
    top_dirs = sorted(dir_totals.items(), key=lambda x: x[1], reverse=True)[:10]
    
    print("\n📁 TOP 10 DIRECTORIES BY TOTAL MEMORY:")
    print("-" * 60)
    for dir_path, total in top_dirs:
        if len(dir_path) > 50:
            dir_path = "..." + dir_path[-47:]
        count = len(by_directory[list(by_directory.keys())[list(dir_totals.values()).index(total)]])
        avg = total / count
        print(f"{dir_path:<50} {total:>8.1f} MB ({count} tests, avg: {avg:.1f} MB)")

def save_results(results: List[Dict], output_file: str) -> None:
    """Save profiling results to a JSON file."""
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Results saved to: {output_file}")

def create_optimized_chunks(results: List[Dict], max_memory_per_chunk: float = 1000) -> List[List[str]]:
    """Create optimized test chunks based on memory usage."""
    # Sort by memory usage (largest first)
    sorted_results = sorted(results, key=lambda x: x["memory_mb"], reverse=True)
    
    chunks = []
    current_chunk = []
    current_memory = 0
    
    for result in sorted_results:
        if current_memory + result["memory_mb"] > max_memory_per_chunk and current_chunk:
            chunks.append(current_chunk)
            current_chunk = []
            current_memory = 0
        
        current_chunk.append(result["path"])
        current_memory += result["memory_mb"]
    
    if current_chunk:
        chunks.append(current_chunk)
    
    print(f"\n📦 OPTIMIZED TEST CHUNKS ({len(chunks)} chunks):")
    print("-" * 60)
    for i, chunk in enumerate(chunks, 1):
        chunk_memory = sum(r["memory_mb"] for r in results if r["path"] in chunk)
        print(f"Chunk {i}: {len(chunk)} tests, ~{chunk_memory:.1f} MB")
    
    return chunks

def main():
    parser = argparse.ArgumentParser(description="Profile memory usage of PolicyEngine tests")
    parser.add_argument(
        "--path",
        default="policyengine_us/tests/policy/baseline",
        help="Base path to search for tests"
    )
    parser.add_argument(
        "--pattern",
        help="Pattern to filter test files (e.g., 'snap', 'tax')"
    )
    parser.add_argument(
        "--by-directory",
        action="store_true",
        help="Profile by directory instead of individual files"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show verbose output"
    )
    parser.add_argument(
        "--output",
        default="test_memory_profile.json",
        help="Output JSON file for results"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of tests to profile"
    )
    parser.add_argument(
        "--create-chunks",
        action="store_true",
        help="Create optimized test chunks for CI"
    )
    parser.add_argument(
        "--max-memory",
        type=float,
        default=1000,
        help="Maximum memory per chunk in MB (default: 1000)"
    )
    
    args = parser.parse_args()
    
    # Find test files or directories
    if args.by_directory:
        test_paths = find_test_directories(args.path)
        print(f"Found {len(test_paths)} test directories")
    else:
        test_paths = find_yaml_test_files(args.path, args.pattern)
        print(f"Found {len(test_paths)} test files")
    
    if args.limit:
        test_paths = test_paths[:args.limit]
        print(f"Limiting to {args.limit} tests")
    
    if not test_paths:
        print("No test files found!")
        sys.exit(1)
    
    # Profile tests
    results = profile_tests(test_paths, args.verbose)
    
    # Analyze results
    analyze_results(results)
    
    # Save results
    save_results(results, args.output)
    
    # Create optimized chunks if requested
    if args.create_chunks:
        chunks = create_optimized_chunks(results, args.max_memory)
        
        # Save chunks to file
        chunks_file = "test_chunks.json"
        with open(chunks_file, 'w') as f:
            json.dump(chunks, f, indent=2)
        print(f"\n💾 Test chunks saved to: {chunks_file}")

if __name__ == "__main__":
    main()