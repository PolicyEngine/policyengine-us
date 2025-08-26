#!/usr/bin/env python
"""
Run contrib tests with complete process isolation.
Each test runs in a separate process that is completely terminated after completion.
This ensures all memory is released between tests.
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
    time.sleep(2)

def run_single_test_isolated(test_file, timeout_seconds=None):
    """
    Run a single test file in complete isolation.
    The subprocess is guaranteed to be terminated and memory released.
    
    Args:
        test_file: Path to the test file
        timeout_seconds: Timeout in seconds, or None for no timeout
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
        
        # Wait for completion with optional timeout
        stdout, stderr = process.communicate(timeout=timeout_seconds)  # None means no timeout
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

def main(timeout_seconds=None):
    print("PolicyEngine Contrib Test Runner - Isolated Process Mode")
    print("=" * 80)
    print("This will run each test in complete isolation.")
    print("Memory will be fully released between tests.")
    if timeout_seconds:
        print(f"Timeout per test: {timeout_seconds} seconds")
    else:
        print("Timeout: DISABLED (tests can run indefinitely)")
    print("=" * 80)
    
    # Find all contrib test files
    contrib_path = Path("policyengine_us/tests/policy/contrib")
    test_files = sorted(contrib_path.rglob("*.yaml"))
    
    print(f"\nFound {len(test_files)} test files in contrib folder")
    print("-" * 80)
    
    results = {}
    passed = 0
    failed = 0
    errors = 0
    timeouts = 0
    
    initial_memory = get_memory_usage()
    print(f"Initial memory usage: {initial_memory:.1f} MB\n")
    
    for i, test_file in enumerate(test_files, 1):
        rel_path = str(test_file).replace("policyengine_us/tests/policy/contrib/", "")
        print(f"[{i}/{len(test_files)}] Testing: {rel_path}", end="", flush=True)
        
        # Run test in complete isolation
        result = run_single_test_isolated(test_file, timeout_seconds)
        results[str(test_file)] = result
        
        # Print result on same line
        if result["status"] == "passed":
            passed += 1
            print(f" ✓ PASSED ({result['elapsed']}s)")
        elif result["status"] == "failed":
            failed += 1
            print(f" ✗ FAILED ({result['elapsed']}s)")
            if result.get("error"):
                print(f"    Error: {result['error'][:100]}...")
        elif result["status"] == "timeout":
            timeouts += 1
            print(f" ⏱ TIMEOUT (exceeded {timeout_seconds}s)")
        else:
            errors += 1
            print(f" ❌ ERROR ({result['elapsed']}s)")
            if result.get("error"):
                print(f"    Error: {result['error'][:100]}...")
        
        # Force memory cleanup after each test (but don't print unless there's an issue)
        force_cleanup()
        current_memory = get_memory_usage()
        
        # If memory is growing too much, do extra cleanup and report it
        if current_memory > initial_memory + 500:  # If we've grown by 500MB
            print(f"  ⚠️  Memory at {current_memory:.1f} MB. Performing cleanup...")
            for _ in range(5):
                gc.collect()
                time.sleep(1)
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total tests: {len(test_files)}")
    print(f"✓ Passed: {passed}")
    print(f"✗ Failed: {failed}")
    print(f"⏱ Timeouts: {timeouts}")
    print(f"❌ Errors: {errors}")
    print(f"\nFinal memory usage: {get_memory_usage():.1f} MB")
    print(f"Initial memory usage: {initial_memory:.1f} MB")
    print(f"Memory growth: {get_memory_usage() - initial_memory:.1f} MB")
    
    # Save results
    with open("contrib_test_results_isolated.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved to: contrib_test_results_isolated.json")
    
    # List failed tests
    if failed > 0 or errors > 0:
        print("\n" + "=" * 80)
        print("FAILED/ERROR TESTS:")
        print("-" * 80)
        for file, result in results.items():
            if result["status"] in ["failed", "error"]:
                rel_file = file.replace("policyengine_us/tests/policy/contrib/", "")
                print(f"  {rel_file}: {result['status']}")
    
    return passed == len(test_files)

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Run contrib tests in isolated processes with memory management"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=None,
        help="Timeout in seconds per test (default: no timeout, tests run indefinitely)"
    )
    parser.add_argument(
        "--timeout-minutes",
        type=int,
        help="Timeout in minutes per test (alternative to --timeout)"
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
    
    success = main(timeout_seconds=timeout)
    sys.exit(0 if success else 1)