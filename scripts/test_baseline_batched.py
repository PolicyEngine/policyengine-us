#!/usr/bin/env python
"""
Run baseline tests in batches with periodic memory cleanup.
Instead of isolating every test, run batches in subprocesses.
This balances speed and memory safety.
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
    time.sleep(1)

def run_batch_isolated(test_files, timeout_seconds):
    """
    Run a batch of test files in an isolated subprocess.
    Returns results for all tests in the batch.
    """
    # Create a temporary Python script to run the batch
    batch_script = """
import sys
import json
from pathlib import Path

results = {}
for test_file in {test_files}:
    try:
        # Import here to ensure fresh start
        from policyengine_core.scripts.policyengine_command import main as test_main
        import time
        
        start = time.time()
        # Capture the test result
        try:
            # Run the test (this is internal, not subprocess)
            import subprocess
            result = subprocess.run(
                [sys.executable, "-m", "policyengine_core.scripts.policyengine_command", 
                 "test", test_file, "-c", "policyengine_us"],
                capture_output=True,
                text=True,
                timeout=30  # Individual test timeout
            )
            status = "passed" if result.returncode == 0 else "failed"
            error = result.stderr[:500] if result.returncode != 0 else None
        except subprocess.TimeoutExpired:
            status = "timeout"
            error = "Individual test timeout"
        except Exception as e:
            status = "error"
            error = str(e)[:500]
        
        elapsed = time.time() - start
        results[test_file] = {{
            "status": status,
            "elapsed": round(elapsed, 2),
            "error": error
        }}
    except Exception as e:
        results[test_file] = {{
            "status": "error",
            "elapsed": 0,
            "error": str(e)[:500]
        }}

print(json.dumps(results))
    """.format(test_files=repr([str(f) for f in test_files]))
    
    try:
        # Run the batch script in a subprocess
        result = subprocess.run(
            [sys.executable, "-c", batch_script],
            capture_output=True,
            text=True,
            timeout=timeout_seconds
        )
        
        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout)
        else:
            # If batch failed, return error for all tests
            return {
                str(f): {
                    "status": "error",
                    "elapsed": 0,
                    "error": f"Batch execution failed: {result.stderr[:200]}"
                }
                for f in test_files
            }
            
    except subprocess.TimeoutExpired:
        # If batch timed out, mark all remaining tests as timeout
        return {
            str(f): {
                "status": "timeout",
                "elapsed": 0,
                "error": f"Batch timeout after {timeout_seconds}s"
            }
            for f in test_files
        }
    except Exception as e:
        return {
            str(f): {
                "status": "error",
                "elapsed": 0,
                "error": str(e)[:200]
            }
            for f in test_files
        }

def run_tests_in_batches(test_files, batch_size=50, timeout_per_batch=300):
    """
    Run tests in batches for better performance while maintaining memory safety.
    """
    results = {}
    passed = 0
    failed = 0
    errors = 0
    timeouts = 0
    
    total_tests = len(test_files)
    total_batches = (total_tests + batch_size - 1) // batch_size
    
    initial_memory = get_memory_usage()
    print(f"Initial memory usage: {initial_memory:.1f} MB")
    print(f"Running {total_tests} tests in {total_batches} batches of {batch_size}")
    print("-" * 80)
    
    for batch_num in range(0, total_tests, batch_size):
        batch = test_files[batch_num:batch_num + batch_size]
        batch_idx = batch_num // batch_size + 1
        
        print(f"\n[Batch {batch_idx}/{total_batches}] Running tests {batch_num+1} to {min(batch_num+len(batch), total_tests)}")
        print(f"  Memory before batch: {get_memory_usage():.1f} MB")
        
        # Run batch in isolated subprocess
        batch_results = run_batch_isolated(batch, timeout_per_batch)
        
        # Process results
        for test_file in batch:
            test_str = str(test_file)
            rel_path = test_str.replace("policyengine_us/tests/policy/baseline/", "")
            
            if test_str in batch_results:
                result = batch_results[test_str]
            else:
                result = {"status": "error", "elapsed": 0, "error": "Not in batch results"}
            
            results[test_str] = result
            
            # Show progress for each test
            test_num = batch_num + batch.index(test_file) + 1
            print(f"  [{test_num}/{total_tests}] {rel_path[:60]}", end="")
            
            # Update counters and show result
            if result["status"] == "passed":
                passed += 1
                print(f" ✓ ({result['elapsed']}s)")
            elif result["status"] == "failed":
                failed += 1
                print(f" ✗ ({result['elapsed']}s)")
                if result.get("error"):
                    print(f"      Error: {result['error'][:100]}...")
            elif result["status"] == "timeout":
                timeouts += 1
                print(f" ⏱ timeout")
            else:
                errors += 1
                print(f" ❌ error")
                if result.get("error"):
                    print(f"      Error: {result['error'][:100]}...")
        
        # Memory cleanup after each batch
        print(f"\n  Batch complete. Memory: {get_memory_usage():.1f} MB")
        print(f"  Status so far: ✓ {passed} | ✗ {failed} | ⏱ {timeouts} | ❌ {errors}")
        print(f"  Cleaning memory...")
        force_cleanup()
        print(f"  Memory after cleanup: {get_memory_usage():.1f} MB")
        
        # Extra cleanup if memory is growing
        current_memory = get_memory_usage()
        if current_memory > initial_memory + 500:
            print(f"  ⚠️  High memory usage detected. Performing aggressive cleanup...")
            for _ in range(5):
                gc.collect()
                time.sleep(0.5)
            print(f"  Memory after aggressive cleanup: {get_memory_usage():.1f} MB")
    
    return results, {"passed": passed, "failed": failed, "timeouts": timeouts, "errors": errors}


def main(batch_size=50):
    """
    Run baseline tests in batches with periodic memory cleanup.
    All tests run in uniform batches for simplicity and speed.
    """
    print("PolicyEngine Baseline Test Runner - Batched Execution")
    print("=" * 80)
    print("Strategy: Run tests in batches with memory cleanup between batches")
    print(f"Batch size: {batch_size} tests")
    print("Memory is cleared after each batch, not after each test")
    print("=" * 80)
    
    # Find all baseline test files
    baseline_path = Path("policyengine_us/tests/policy/baseline")
    all_test_files = sorted(baseline_path.rglob("*.yaml"))
    
    print(f"\nFound {len(all_test_files)} total test files")
    print(f"Will run in {(len(all_test_files) + batch_size - 1) // batch_size} batches")
    print("-" * 80)
    
    # Run all tests in uniform batches
    all_results, all_stats = run_tests_in_batches(
        all_test_files, 
        batch_size=batch_size,
        timeout_per_batch=180  # 3 minutes per batch of 50 tests
    )
    
    # Final summary
    print("\n" + "=" * 80)
    print("FINAL TEST SUMMARY")
    print("=" * 80)
    print(f"Total tests: {len(all_test_files)}")
    print(f"✓ Passed: {all_stats['passed']}")
    print(f"✗ Failed: {all_stats['failed']}")
    print(f"⏱ Timeouts: {all_stats['timeouts']}")
    print(f"❌ Errors: {all_stats['errors']}")
    
    success_rate = (all_stats['passed'] / len(all_test_files) * 100) if all_test_files else 0
    print(f"\nSuccess rate: {success_rate:.1f}%")
    
    # Save results
    output_file = "baseline_test_results_batched.json"
    with open(output_file, "w") as f:
        json.dump({
            "results": all_results,
            "stats": all_stats,
            "success_rate": success_rate
        }, f, indent=2)
    print(f"\nDetailed results saved to: {output_file}")
    
    return all_stats['passed'] == len(all_test_files)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run baseline tests in batches with periodic memory cleanup"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Number of tests per batch (default: 50)"
    )
    
    args = parser.parse_args()
    
    if not os.path.exists("policyengine_us"):
        print("Error: Must run from PolicyEngine US root directory")
        sys.exit(1)
    
    success = main(batch_size=args.batch_size)
    sys.exit(0 if success else 1)