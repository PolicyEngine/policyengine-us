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
    # Multiple collections to ensure cleanup
    gc.collect()
    gc.collect()
    gc.collect()
    # No sleep needed - just cleanup


def run_batch_isolated(test_dirs, timeout_seconds):
    """
    Run a batch of test directories in an isolated subprocess.
    Runs entire directories together to avoid repeat initialization.
    """
    # Detect the right Python executable
    import os

    if os.path.exists("/opt/miniconda3/envs/policyengine/bin/python"):
        python_exe = "/opt/miniconda3/envs/policyengine/bin/python"
    else:
        python_exe = sys.executable

    # Convert to list of directory strings
    test_dirs_list = [str(d) for d in test_dirs]

    try:
        import time

        start_time = time.time()

        # Run all directories in one command - policyengine-core will handle them efficiently
        cmd = (
            [
                python_exe,
                "-m",
                "policyengine_core.scripts.policyengine_command",
                "test",
            ]
            + test_dirs_list
            + ["-c", "policyengine_us"]
        )

        print(f"    Running {len(test_dirs_list)} directories together...")

        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout_seconds
        )

        elapsed = time.time() - start_time

        # Parse output to count tests
        output = result.stdout
        passed_count = output.count(" passed")
        failed_count = output.count(" failed")

        # Extract test count from pytest summary if possible
        import re

        summary_match = re.search(r"(\d+) passed", output)
        if summary_match:
            passed_count = int(summary_match.group(1))
        summary_match = re.search(r"(\d+) failed", output)
        if summary_match:
            failed_count = int(summary_match.group(1))

        print(
            f"    Completed in {elapsed:.1f}s: {passed_count} passed, {failed_count} failed"
        )

        # Return summary for all directories
        return {
            "dirs": test_dirs_list,
            "passed": passed_count,
            "failed": failed_count,
            "elapsed": elapsed,
            "status": "passed" if result.returncode == 0 else "failed",
        }

    except subprocess.TimeoutExpired:
        print(f"    Timeout after {timeout_seconds}s")
        return {
            "dirs": test_dirs_list,
            "passed": 0,
            "failed": 0,
            "elapsed": timeout_seconds,
            "status": "timeout",
        }
    except Exception as e:
        print(f"    Error: {str(e)[:100]}")
        return {
            "dirs": test_dirs_list,
            "passed": 0,
            "failed": 0,
            "elapsed": 0,
            "status": "error",
        }


def get_all_state_directories():
    """Get all state directories that exist and have tests."""
    from pathlib import Path

    states_path = Path("policyengine_us/tests/policy/baseline/gov/states")
    state_dirs = []

    if states_path.exists():
        for state_dir in sorted(states_path.iterdir()):
            if state_dir.is_dir():
                # Check if it has yaml files
                if list(state_dir.glob("*.yaml")) or list(
                    state_dir.rglob("*.yaml")
                ):
                    state_dirs.append(str(state_dir))

    return state_dirs


def get_parent_directory_batches(conservative=False):
    """
    Define optimal parent directory batches for testing.
    Returns a list of directory paths to run as separate batches.

    Lists specific directories to avoid overlap - no parent directories
    that would re-run tests from subdirectories.
    """
    baseline = "policyengine_us/tests/policy/baseline"

    if conservative:
        # More batches, less memory per batch
        # Each directory listed explicitly to avoid overlap
        return [
            # Slow/complex states run separately
            f"{baseline}/gov/states/ny",  # ~43 tests, complex
            f"{baseline}/gov/states/nc",  # ~30 tests, complex
            f"{baseline}/gov/states/ca",  # ~89 tests, many files
            f"{baseline}/gov/states/ma",  # ~72 tests, complex
            # Other states grouped by size/complexity
            f"{baseline}/gov/states/il",  # ~60 tests
            f"{baseline}/gov/states/pa",  # Medium state
            f"{baseline}/gov/states/tx",  # Large state
            f"{baseline}/gov/states",  # All remaining states
            # Federal agencies (each separately for memory safety)
            f"{baseline}/gov/irs",  # ~162 tests
            f"{baseline}/gov/usda",  # ~63 tests
            f"{baseline}/gov/hhs",  # ~57 tests
            f"{baseline}/gov/local",  # ~60 tests
            f"{baseline}/gov/ssa",  # ~24 tests
            f"{baseline}/gov/aca",  # ~20 tests
            f"{baseline}/gov/hud",  # ~19 tests
            f"{baseline}/gov/territories",  # ~16 tests
            f"{baseline}/gov/ed",  # ~15 tests
            f"{baseline}/gov/doe",  # ~10 tests
            f"{baseline}/gov/fcc",  # ~11 tests
            f"{baseline}/gov",  # Any remaining gov subdirectories
            # Other top-level directories
            f"{baseline}/household",  # ~81 tests
            f"{baseline}/contrib",  # ~7 tests (slow)
            f"{baseline}/calcfunctions",  # ~1 test
            f"{baseline}/income",  # ~1 test
        ]
    else:
        # Aggressive mode - run all states alphabetically
        # Since we're running states individually, no need to separate slow ones
        batches = []

        # Get all state directories and run them alphabetically
        all_states = get_all_state_directories()
        batches.extend(sorted(all_states))  # Alphabetical order

        # Federal agencies
        batches.extend(
            [
                f"{baseline}/gov/irs",  # ~162 tests
                f"{baseline}/gov/usda",  # ~63 tests
                f"{baseline}/gov/local",  # ~60 tests
                f"{baseline}/gov/hhs",  # ~57 tests
                f"{baseline}/gov/ssa",  # ~24 tests
                f"{baseline}/gov/aca",  # ~20 tests
                f"{baseline}/gov/hud",  # ~19 tests
                f"{baseline}/gov/territories",  # ~16 tests
                f"{baseline}/gov/ed",  # ~15 tests
                f"{baseline}/gov/doe",  # ~10 tests
                f"{baseline}/gov/fcc",  # ~11 tests
                f"{baseline}/gov/simulation",  # ~4 tests
                f"{baseline}/gov/tax",  # ~1 test
                # Individual files that are directly in parent directories
                f"{baseline}/gov/abolitions.yaml",  # Single file directly in gov/
                f"{baseline}/gov/states/state_filing_status_if_married_filing_separately_on_same_return.yaml",  # Single file in states/
            ]
        )

        # Other baseline directories
        batches.extend(
            [
                f"{baseline}/household",  # ~81 tests
                f"{baseline}/contrib",  # ~7 tests
                f"{baseline}/calcfunctions",  # ~1 test
                f"{baseline}/income",  # ~1 test
            ]
        )

        return batches


def count_tests_in_directory(directory):
    """Count the number of yaml test files in a directory."""
    from pathlib import Path

    dir_path = Path(directory)
    if not dir_path.exists():
        return 0
    return len(list(dir_path.rglob("*.yaml")))


def run_tests_in_batches(test_files, batch_size=None, timeout_per_batch=1200):
    """
    Run tests using optimal parent directory batching.
    batch_size parameter is ignored - we use parent directories instead.
    """
    passed = 0
    failed = 0
    errors = 0
    timeouts = 0

    initial_memory = get_memory_usage()
    print(f"Initial memory usage: {initial_memory:.1f} MB")

    # Choose strategy based on initial memory
    conservative = (
        initial_memory > 500
    )  # Use conservative if already using >500MB

    if conservative:
        print(
            "Using conservative batching strategy (more batches, less memory)"
        )
    else:
        print("Using aggressive batching strategy (fewer batches, faster)")

    parent_dirs = get_parent_directory_batches(conservative)

    # Process directories, avoiding overlaps
    valid_batches = []
    already_covered_paths = set()

    for dir_path in parent_dirs:
        from pathlib import Path

        dir_p = Path(dir_path)

        if not dir_p.exists():
            continue

        # Special handling for parent directories that should only test direct files
        if dir_path.endswith("/gov") or dir_path.endswith("/gov/states"):
            # Only get files directly in this directory, not subdirectories
            test_files = set(str(f) for f in dir_p.glob("*.yaml"))
        else:
            # Get all files recursively
            test_files = set(str(f) for f in dir_p.rglob("*.yaml"))

        # Remove files already covered by previous batches
        uncovered_files = test_files - already_covered_paths

        if uncovered_files:
            # This batch will cover new tests
            valid_batches.append((dir_path, len(uncovered_files)))
            already_covered_paths.update(
                test_files
            )  # Mark all files in this dir as covered

    total_tests = sum(count for _, count in valid_batches)
    print(
        f"Running {total_tests} tests in {len(valid_batches)} parent directory batches"
    )
    print("-" * 80)

    detailed_results = {}
    memory_stats = []  # Track memory usage per batch

    for batch_idx, (dir_path, test_count) in enumerate(valid_batches, 1):
        dir_name = dir_path.split("/")[-1] if "/" in dir_path else dir_path

        print(
            f"\n[Batch {batch_idx}/{len(valid_batches)}] Running {dir_name}/ ({test_count} test files)"
        )
        print(f"  Directory: {dir_path}")
        print(f"  Memory before: {get_memory_usage():.1f} MB")

        # Run single parent directory - ensures single initialization
        batch_results = run_batch_isolated([dir_path], timeout_per_batch)

        # Update counters
        if batch_results["status"] == "passed":
            passed += batch_results["passed"]
        elif batch_results["status"] == "failed":
            passed += batch_results["passed"]
            failed += batch_results["failed"]
        elif batch_results["status"] == "timeout":
            timeouts += test_count
        else:
            errors += test_count

        # Store results
        detailed_results[dir_path] = batch_results

        # Report completion and memory
        current_memory = get_memory_usage()
        memory_growth = current_memory - initial_memory

        print(f"\n  Batch complete in {batch_results.get('elapsed', 0):.1f}s")
        print(
            f"  Memory: {current_memory:.1f} MB (growth: +{memory_growth:.1f} MB from start)"
        )
        print(
            f"  Running total: ✓ {passed} | ✗ {failed} | ⏱ {timeouts} | ❌ {errors}"
        )

        # Always perform cleanup after each batch to maintain low memory
        print(f"  Performing memory cleanup...")
        force_cleanup()
        cleaned_memory = get_memory_usage()
        memory_freed = current_memory - cleaned_memory
        print(
            f"  Memory after cleanup: {cleaned_memory:.1f} MB (freed: {memory_freed:.1f} MB)"
        )

        # Store memory stats for summary
        memory_stats.append(
            {
                "batch": dir_name,
                "peak_memory": current_memory,
                "memory_freed": memory_freed,
            }
        )

    # Print memory summary
    if memory_stats:
        print("\n" + "=" * 80)
        print("MEMORY USAGE SUMMARY")
        print("=" * 80)
        for stat in memory_stats:
            print(
                f"{stat['batch']:30} Peak: {stat['peak_memory']:6.1f} MB, Freed: {stat['memory_freed']:5.1f} MB"
            )

    return detailed_results, {
        "passed": passed,
        "failed": failed,
        "timeouts": timeouts,
        "errors": errors,
    }


def main(batch_size=None):
    """
    Run baseline tests using optimal parent directory batching.
    This approach runs entire parent directories to minimize initialization overhead.
    """
    print(
        "PolicyEngine Baseline Test Runner - Optimized Parent Directory Batching"
    )
    print("=" * 80)
    print(
        "Strategy: Run parent directories to ensure single initialization per batch"
    )
    print("Memory management: Automatic cleanup when usage exceeds thresholds")
    print("=" * 80)

    # Find all baseline test files
    baseline_path = Path("policyengine_us/tests/policy/baseline")
    all_test_files = sorted(baseline_path.rglob("*.yaml"))

    print(f"\nFound {len(all_test_files)} total test files")
    print("-" * 80)

    # Run all tests using parent directory batching
    all_results, all_stats = run_tests_in_batches(
        all_test_files,
        timeout_per_batch=1200,  # 20 minutes per batch for large directories
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

    success_rate = (
        (all_stats["passed"] / len(all_test_files) * 100)
        if all_test_files
        else 0
    )
    print(f"\nSuccess rate: {success_rate:.1f}%")

    # Save results
    output_file = "baseline_test_results_batched.json"
    with open(output_file, "w") as f:
        json.dump(
            {
                "directory_results": all_results,
                "stats": all_stats,
                "success_rate": success_rate,
                "total_directories": len(all_results),
            },
            f,
            indent=2,
        )
    print(f"\nDetailed results saved to: {output_file}")

    return all_stats["passed"] == len(all_test_files)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run baseline tests in batches with periodic memory cleanup"
    )
    parser.add_argument(
        "--conservative",
        action="store_true",
        help="Use conservative batching (more batches, less memory)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Deprecated - ignored, using parent directory batching instead",
    )

    args = parser.parse_args()

    if not os.path.exists("policyengine_us"):
        print("Error: Must run from PolicyEngine US root directory")
        sys.exit(1)

    if args.batch_size is not None:
        print("Warning: --batch-size is deprecated and ignored.")
        print("Using optimal parent directory batching instead.\n")

    success = main()
    sys.exit(0 if success else 1)
