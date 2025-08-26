#!/usr/bin/env python
"""
Run baseline tests with complete process isolation.
Each test runs in a separate process that is completely terminated after completion.
This ensures all memory is released between tests.

Optimized for baseline tests where most run fast but a few (e.g., NY state) are memory-intensive.
"""

import subprocess
import sys
import os
import gc
import time
import psutil
from pathlib import Path
import json
import argparse
from collections import defaultdict

def get_memory_usage():
    """Get current memory usage in MB."""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024

def force_cleanup():
    """Force aggressive memory cleanup."""
    gc.collect()
    gc.collect()
    gc.collect()
    # Give OS time to reclaim memory
    time.sleep(1)

def run_single_test_isolated(test_file, timeout_seconds=120):
    """
    Run a single test file in complete isolation.
    The subprocess is guaranteed to be terminated and memory released.
    
    Args:
        test_file: Path to the test file
        timeout_seconds: Timeout in seconds (default: 120 for baseline tests)
    """
    # Use sys.executable to ensure we use the same Python as the runner
    cmd = [
        sys.executable,
        "-m",
        "policyengine_core.scripts.policyengine_command",
        "test",
        str(test_file),
        "-c",
        "policyengine_us"
    ]
    
    start_time = time.time()
    start_memory = get_memory_usage()
    
    try:
        # Run test in subprocess - this ensures complete isolation
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for completion with timeout
        stdout, stderr = process.communicate(timeout=timeout_seconds)
        elapsed = time.time() - start_time
        
        result = {
            "status": "passed" if process.returncode == 0 else "failed",
            "returncode": process.returncode,
            "elapsed": round(elapsed, 2),
            "memory_before": round(start_memory, 2),
            "memory_after": round(get_memory_usage(), 2),
            "error": stderr[:500] if stderr and process.returncode != 0 else None
        }
        
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        process.kill()
        stdout, stderr = process.communicate()
        result = {
            "status": "timeout",
            "returncode": -1,
            "elapsed": round(elapsed, 2),
            "memory_before": round(start_memory, 2),
            "memory_after": round(get_memory_usage(), 2),
            "error": f"Test timed out after {timeout_seconds} seconds"
        }
    except Exception as e:
        elapsed = time.time() - start_time
        result = {
            "status": "error",
            "returncode": -1,
            "elapsed": round(elapsed, 2),
            "memory_before": round(start_memory, 2),
            "memory_after": round(get_memory_usage(), 2),
            "error": str(e)
        }
    
    finally:
        # Ensure process is terminated
        try:
            process.terminate()
            time.sleep(0.5)
            process.kill()
        except:
            pass
    
    return result

def get_test_category(test_path):
    """Extract the category (e.g., state name) from test path."""
    path_parts = str(test_path).split('/')
    # Look for states pattern
    if 'states' in path_parts:
        state_idx = path_parts.index('states')
        if state_idx + 1 < len(path_parts):
            return f"states/{path_parts[state_idx + 1]}"
    # Otherwise use the first meaningful directory after baseline
    for i, part in enumerate(path_parts):
        if part == 'baseline' and i + 2 < len(path_parts):
            return f"{path_parts[i+1]}/{path_parts[i+2]}"
    return "other"

def main(timeout_seconds=120, batch_size=50):
    print("PolicyEngine Baseline Test Runner - Isolated Process Mode")
    print("=" * 80)
    print("This will run each test in complete isolation.")
    print("Memory will be fully released between tests.")
    print(f"Default timeout per test: {timeout_seconds} seconds")
    print(f"Batch size for progress updates: {batch_size}")
    print("=" * 80)
    
    # Find all baseline test files
    baseline_path = Path("policyengine_us/tests/policy/baseline")
    test_files = sorted(baseline_path.rglob("*.yaml"))
    
    print(f"\nFound {len(test_files)} test files in baseline folder")
    
    # Group tests by category for better reporting
    test_categories = defaultdict(list)
    for test_file in test_files:
        category = get_test_category(test_file)
        test_categories[category].append(test_file)
    
    print(f"Test distribution across {len(test_categories)} categories:")
    for category in sorted(test_categories.keys())[:10]:
        print(f"  {category}: {len(test_categories[category])} tests")
    if len(test_categories) > 10:
        print(f"  ... and {len(test_categories) - 10} more categories")
    print("-" * 80)
    
    results = {}
    passed = 0
    failed = 0
    errors = 0
    timeouts = 0
    slow_tests = []  # Tests taking >5 seconds
    
    initial_memory = get_memory_usage()
    print(f"Initial memory usage: {initial_memory:.1f} MB\n")
    
    # Track problem categories
    problem_categories = defaultdict(lambda: {"failed": 0, "timeout": 0, "slow": 0})
    
    for i, test_file in enumerate(test_files, 1):
        rel_path = str(test_file).replace("policyengine_us/tests/policy/baseline/", "")
        category = get_test_category(test_file)
        
        # Print progress at batch boundaries or for slow categories
        if i == 1 or i % batch_size == 0 or i == len(test_files):
            print(f"\n[Batch {(i-1)//batch_size + 1}] Processing tests {i} to {min(i+batch_size-1, len(test_files))}")
            print(f"  Current memory usage: {get_memory_usage():.1f} MB")
            print(f"  Running totals - ✓ {passed} | ✗ {failed} | ⏱ {timeouts} | ❌ {errors}")
        
        # Run test in complete isolation
        result = run_single_test_isolated(test_file, timeout_seconds)
        results[str(test_file)] = result
        result["category"] = category  # Store category for analysis
        
        # Update counters
        if result["status"] == "passed":
            passed += 1
            # Track slow but passing tests
            if result["elapsed"] > 5:
                slow_tests.append((rel_path, result["elapsed"]))
                problem_categories[category]["slow"] += 1
        elif result["status"] == "failed":
            failed += 1
            problem_categories[category]["failed"] += 1
        elif result["status"] == "timeout":
            timeouts += 1
            problem_categories[category]["timeout"] += 1
        else:
            errors += 1
            problem_categories[category]["failed"] += 1
        
        # Always print output for problematic tests
        if result["status"] != "passed" or result["elapsed"] > 10:
            status_symbols = {
                "passed": "✓",
                "failed": "✗", 
                "timeout": "⏱",
                "error": "❌"
            }
            symbol = status_symbols.get(result["status"], "?")
            
            # Truncate long paths for readability
            display_path = rel_path if len(rel_path) <= 60 else "..." + rel_path[-57:]
            print(f"  [{i}/{len(test_files)}] {display_path}: {symbol} {result['status'].upper()} ({result['elapsed']}s)")
            
            if result["status"] == "failed" and result.get("error"):
                print(f"    Error: {result['error'][:100]}...")
            elif result["status"] == "timeout":
                print(f"    ⚠️  Test in '{category}' timed out after {timeout_seconds}s")
            elif result["elapsed"] > 10:
                print(f"    ⚠️  Slow test in '{category}' took {result['elapsed']}s")
        
        # Immediate cleanup after slow/problematic tests
        if result["elapsed"] > 10 or result["status"] in ["timeout", "error"]:
            print(f"    Performing immediate cleanup after problematic test...")
            force_cleanup()
            print(f"    Memory after cleanup: {get_memory_usage():.1f} MB")
        
        # Periodic memory cleanup at batch boundaries
        elif i % batch_size == 0:
            force_cleanup()
            current_memory = get_memory_usage()
            
            # Extra cleanup if memory is growing
            if current_memory > initial_memory + 500:  # 500MB growth threshold
                print(f"  ⚠️  Memory growth detected ({current_memory:.1f} MB). Performing aggressive cleanup...")
                for _ in range(3):
                    gc.collect()
                    time.sleep(0.5)
                print(f"  Memory after aggressive cleanup: {get_memory_usage():.1f} MB")
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total tests: {len(test_files)}")
    print(f"✓ Passed: {passed}")
    print(f"✗ Failed: {failed}")
    print(f"⏱ Timeouts: {timeouts}")
    print(f"❌ Errors: {errors}")
    
    success_rate = (passed / len(test_files) * 100) if test_files else 0
    print(f"\nSuccess rate: {success_rate:.1f}%")
    print(f"Final memory usage: {get_memory_usage():.1f} MB")
    print(f"Memory growth: {get_memory_usage() - initial_memory:.1f} MB")
    
    # Report slow tests
    if slow_tests:
        print("\n" + "=" * 80)
        print(f"SLOW TESTS (>{5}s): {len(slow_tests)} tests")
        print("-" * 80)
        for test_path, elapsed in sorted(slow_tests, key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {elapsed:6.1f}s - {test_path}")
        if len(slow_tests) > 10:
            print(f"  ... and {len(slow_tests) - 10} more slow tests")
    
    # Report problem categories
    if problem_categories:
        print("\n" + "=" * 80)
        print("PROBLEM CATEGORIES")
        print("-" * 80)
        sorted_categories = sorted(
            problem_categories.items(),
            key=lambda x: x[1]["failed"] + x[1]["timeout"],
            reverse=True
        )
        for category, stats in sorted_categories[:10]:
            issues = []
            if stats["failed"]:
                issues.append(f"{stats['failed']} failed")
            if stats["timeout"]:
                issues.append(f"{stats['timeout']} timeouts")
            if stats["slow"]:
                issues.append(f"{stats['slow']} slow")
            print(f"  {category}: {', '.join(issues)}")
    
    # Save results
    output_file = "baseline_test_results_isolated.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved to: {output_file}")
    
    # List some failed tests (limited output)
    if failed > 0 or errors > 0 or timeouts > 0:
        print("\n" + "=" * 80)
        print("SAMPLE FAILED/ERROR/TIMEOUT TESTS (max 20):")
        print("-" * 80)
        count = 0
        for file, result in results.items():
            if result["status"] in ["failed", "error", "timeout"]:
                rel_file = file.replace("policyengine_us/tests/policy/baseline/", "")
                display_file = rel_file if len(rel_file) <= 70 else "..." + rel_file[-67:]
                print(f"  [{result['status']}] {display_file}")
                count += 1
                if count >= 20:
                    remaining = sum(1 for r in results.values() 
                                   if r["status"] in ["failed", "error", "timeout"]) - 20
                    if remaining > 0:
                        print(f"  ... and {remaining} more")
                    break
    
    return passed == len(test_files)

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Run baseline tests in isolated processes with memory management"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Timeout in seconds per test (default: 120s for baseline tests)"
    )
    parser.add_argument(
        "--timeout-minutes",
        type=int,
        help="Timeout in minutes per test (alternative to --timeout)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Number of tests between progress updates (default: 50)"
    )
    args = parser.parse_args()
    
    # Handle timeout arguments
    timeout = args.timeout
    if args.timeout_minutes:
        timeout = args.timeout_minutes * 60
    
    # Ensure we're in the right directory
    if not os.path.exists("policyengine_us"):
        print("Error: Must run from PolicyEngine US root directory")
        sys.exit(1)
    
    success = main(timeout_seconds=timeout, batch_size=args.batch_size)
    sys.exit(0 if success else 1)