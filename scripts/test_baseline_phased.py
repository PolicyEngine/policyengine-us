#!/usr/bin/env python
"""
Run baseline tests in phases: fast tests first, then slow tests.
This provides quick feedback while ensuring all tests complete.
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
    time.sleep(1)

def run_single_test_isolated(test_file, timeout_seconds):
    """
    Run a single test file in complete isolation.
    """
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
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
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
        try:
            process.terminate()
            time.sleep(0.5)
            process.kill()
        except:
            pass
    
    return result

def categorize_tests(test_files):
    """
    Categorize tests into fast and slow based on known patterns.
    Returns (fast_tests, slow_tests)
    """
    slow_patterns = [
        "states/ny",  # New York tests are confirmed to be slow/memory-intensive
        # Add more patterns only after confirming they're actually slow
        # For now, being conservative - only NY is confirmed slow
    ]
    
    fast_tests = []
    slow_tests = []
    
    for test_file in test_files:
        test_path_str = str(test_file).lower()
        is_slow = any(pattern in test_path_str for pattern in slow_patterns)
        
        if is_slow:
            slow_tests.append(test_file)
        else:
            fast_tests.append(test_file)
    
    return fast_tests, slow_tests

def run_test_phase(test_files, phase_name, timeout_seconds, batch_size=50):
    """
    Run a phase of tests with given timeout.
    """
    print(f"\n{'=' * 80}")
    print(f"PHASE: {phase_name}")
    print(f"Tests: {len(test_files)}, Timeout: {timeout_seconds}s per test")
    print('=' * 80)
    
    results = {}
    passed = 0
    failed = 0
    errors = 0
    timeouts = 0
    
    initial_memory = get_memory_usage()
    
    for i, test_file in enumerate(test_files, 1):
        rel_path = str(test_file).replace("policyengine_us/tests/policy/baseline/", "")
        
        # Print progress at batch boundaries
        if i == 1 or i % batch_size == 0 or i == len(test_files):
            print(f"\n[{phase_name}] Processing tests {i} to {min(i+batch_size-1, len(test_files))}")
            print(f"  Memory: {get_memory_usage():.1f} MB")
            print(f"  Status: ✓ {passed} | ✗ {failed} | ⏱ {timeouts} | ❌ {errors}")
        
        # Run test
        result = run_single_test_isolated(test_file, timeout_seconds)
        results[str(test_file)] = result
        
        # Update counters
        if result["status"] == "passed":
            passed += 1
        elif result["status"] == "failed":
            failed += 1
        elif result["status"] == "timeout":
            timeouts += 1
        else:
            errors += 1
        
        # Print details for problematic tests
        if result["status"] != "passed":
            status_symbols = {
                "failed": "✗",
                "timeout": "⏱",
                "error": "❌"
            }
            symbol = status_symbols.get(result["status"], "?")
            
            display_path = rel_path if len(rel_path) <= 60 else "..." + rel_path[-57:]
            print(f"  [{i}/{len(test_files)}] {display_path}: {symbol} ({result['elapsed']}s)")
            
            if result["status"] == "timeout":
                print(f"    Note: Test exceeded {timeout_seconds}s timeout")
        
        # Cleanup after slow or problematic tests
        if result["elapsed"] > 10 or result["status"] in ["timeout", "error"]:
            force_cleanup()
        
        # Periodic cleanup
        if i % batch_size == 0:
            force_cleanup()
            current_memory = get_memory_usage()
            if current_memory > initial_memory + 500:
                print(f"  ⚠️  Memory growth detected. Aggressive cleanup...")
                for _ in range(3):
                    gc.collect()
                    time.sleep(0.5)
    
    print(f"\n{phase_name} Summary:")
    print(f"  ✓ Passed: {passed}")
    print(f"  ✗ Failed: {failed}")
    print(f"  ⏱ Timeouts: {timeouts}")
    print(f"  ❌ Errors: {errors}")
    
    return results, {"passed": passed, "failed": failed, "timeouts": timeouts, "errors": errors}

def main(fast_timeout=60, slow_timeout=600, batch_size=50):
    """
    Run baseline tests in two phases:
    1. Fast tests with shorter timeout
    2. Slow/problematic tests with longer timeout
    """
    print("PolicyEngine Baseline Test Runner - Phased Execution")
    print("=" * 80)
    print("Strategy: Run fast tests first, then slow tests")
    print(f"Fast test timeout: {fast_timeout}s")
    print(f"Slow test timeout: {slow_timeout}s (10 minutes)")
    print("=" * 80)
    
    # Find all baseline test files
    baseline_path = Path("policyengine_us/tests/policy/baseline")
    all_test_files = sorted(baseline_path.rglob("*.yaml"))
    
    print(f"\nFound {len(all_test_files)} total test files")
    
    # Categorize tests
    fast_tests, slow_tests = categorize_tests(all_test_files)
    
    print(f"Categorization:")
    print(f"  Fast tests: {len(fast_tests)}")
    print(f"  Slow tests: {len(slow_tests)}")
    
    if slow_tests:
        print(f"\nSlow test categories:")
        slow_categories = defaultdict(int)
        for test in slow_tests:
            if "states/" in str(test):
                parts = str(test).split("states/")
                if len(parts) > 1:
                    state = parts[1].split("/")[0]
                    slow_categories[f"states/{state}"] += 1
        
        for category, count in sorted(slow_categories.items())[:10]:
            print(f"  {category}: {count} tests")
    
    all_results = {}
    phase_stats = {}
    
    # Phase 1: Fast tests
    if fast_tests:
        fast_results, fast_stats = run_test_phase(
            fast_tests, 
            "FAST TESTS", 
            fast_timeout, 
            batch_size
        )
        all_results.update(fast_results)
        phase_stats["fast"] = fast_stats
    
    # Phase 2: Slow tests (if any)
    if slow_tests:
        print(f"\n{'=' * 80}")
        print("Preparing for SLOW TESTS phase...")
        print("These tests are known to be memory-intensive or slow.")
        print("Using extended timeout to allow them to complete.")
        print('=' * 80)
        
        force_cleanup()  # Extra cleanup before slow tests
        time.sleep(2)
        
        slow_results, slow_stats = run_test_phase(
            slow_tests,
            "SLOW TESTS",
            slow_timeout,
            batch_size=10  # Smaller batches for slow tests
        )
        all_results.update(slow_results)
        phase_stats["slow"] = slow_stats
    
    # Final summary
    print("\n" + "=" * 80)
    print("FINAL TEST SUMMARY")
    print("=" * 80)
    
    total_passed = sum(stats["passed"] for stats in phase_stats.values())
    total_failed = sum(stats["failed"] for stats in phase_stats.values())
    total_timeouts = sum(stats["timeouts"] for stats in phase_stats.values())
    total_errors = sum(stats["errors"] for stats in phase_stats.values())
    
    print(f"Total tests: {len(all_test_files)}")
    print(f"✓ Passed: {total_passed}")
    print(f"✗ Failed: {total_failed}")
    print(f"⏱ Timeouts: {total_timeouts}")
    print(f"❌ Errors: {total_errors}")
    
    success_rate = (total_passed / len(all_test_files) * 100) if all_test_files else 0
    print(f"\nSuccess rate: {success_rate:.1f}%")
    
    # Save results
    output_file = "baseline_test_results_phased.json"
    with open(output_file, "w") as f:
        json.dump({
            "results": all_results,
            "phase_stats": phase_stats,
            "total_stats": {
                "total": len(all_test_files),
                "passed": total_passed,
                "failed": total_failed,
                "timeouts": total_timeouts,
                "errors": total_errors,
                "success_rate": success_rate
            }
        }, f, indent=2)
    print(f"\nDetailed results saved to: {output_file}")
    
    # List timeouts specifically
    if total_timeouts > 0:
        print("\n" + "=" * 80)
        print("TIMEOUT TESTS (may need investigation):")
        print("-" * 80)
        timeout_count = 0
        for file, result in all_results.items():
            if result["status"] == "timeout":
                rel_file = file.replace("policyengine_us/tests/policy/baseline/", "")
                print(f"  {rel_file} (ran for {result['elapsed']}s)")
                timeout_count += 1
                if timeout_count >= 10:
                    remaining = total_timeouts - 10
                    if remaining > 0:
                        print(f"  ... and {remaining} more")
                    break
    
    return total_passed == len(all_test_files)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run baseline tests in phases with different timeouts"
    )
    parser.add_argument(
        "--fast-timeout",
        type=int,
        default=60,
        help="Timeout for fast tests in seconds (default: 60s)"
    )
    parser.add_argument(
        "--slow-timeout",
        type=int,
        default=600,
        help="Timeout for slow tests in seconds (default: 600s/10 min)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Batch size for progress updates (default: 50)"
    )
    
    args = parser.parse_args()
    
    # Ensure we're in the right directory
    if not os.path.exists("policyengine_us"):
        print("Error: Must run from PolicyEngine US root directory")
        sys.exit(1)
    
    success = main(
        fast_timeout=args.fast_timeout,
        slow_timeout=args.slow_timeout,
        batch_size=args.batch_size
    )
    sys.exit(0 if success else 1)