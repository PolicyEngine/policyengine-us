#!/usr/bin/env python3
"""
Batch test runner for contrib tests with memory management.

Runs tests in smaller batches to prevent memory issues.
Tests are organized by subdirectory for better organization.
"""

import os
import sys
import subprocess
import gc
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


def find_test_files(base_path: str) -> Dict[str, List[str]]:
    """Find all YAML test files organized by subdirectory."""
    test_files = {}
    base_dir = Path(base_path)

    for yaml_file in base_dir.rglob("*.yaml"):
        # Get relative path from contrib folder
        rel_path = yaml_file.relative_to(base_dir)
        # Use first directory level as category (or 'root' for top-level files)
        parts = rel_path.parts
        category = parts[0] if len(parts) > 1 else "root"

        if category not in test_files:
            test_files[category] = []
        test_files[category].append(str(yaml_file))

    # Sort files within each category
    for category in test_files:
        test_files[category].sort()

    return test_files


def run_test_batch(test_files: List[str], batch_name: str) -> Dict[str, Any]:
    """Run a batch of tests and return results."""
    print(f"\n{'='*60}")
    print(f"Running batch: {batch_name} ({len(test_files)} tests)")
    print(f"{'='*60}")

    start_time = datetime.now()

    # Create temporary test list file
    test_list_file = (
        f"/tmp/contrib_test_batch_{batch_name.replace('/', '_')}.txt"
    )
    with open(test_list_file, "w") as f:
        for test_file in test_files:
            f.write(f"{test_file}\n")

    # Use the current Python executable (works with uv run, conda, etc.)
    python_exe = sys.executable

    # Run tests
    cmd = [
        python_exe,
        "-m",
        "policyengine_core.scripts.policyengine_command",
        "test",
        *test_files,
        "-c",
        "policyengine_us",
    ]

    # Set timeout to 40 minutes per folder
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=2400
        )
        elapsed_time = (datetime.now() - start_time).total_seconds()
        success = result.returncode == 0
        stdout = result.stdout
        stderr = result.stderr
    except subprocess.TimeoutExpired:
        elapsed_time = 2400
        success = False
        stdout = ""
        stderr = f"Tests timed out after 40 minutes"
        print(f"⏱️  Timeout: {batch_name} exceeded 40-minute limit")

    # Clean up
    if os.path.exists(test_list_file):
        os.remove(test_list_file)

    return {
        "batch_name": batch_name,
        "num_tests": len(test_files),
        "elapsed_time": elapsed_time,
        "success": success,
        "stdout": stdout,
        "stderr": stderr,
    }


def get_batch_size(category: str) -> int:
    """Get batch size based on category."""
    # Run all files in a folder together as one batch
    # Return a very large number so we never split folders
    return 999999  # Effectively unlimited - run entire folder at once


def main():
    """Main function to run all contrib tests in batches."""
    base_path = "policyengine_us/tests/policy/contrib"

    print("Finding contrib test files...")
    test_categories = find_test_files(base_path)

    total_files = sum(len(files) for files in test_categories.values())
    print(
        f"Found {total_files} test files in {len(test_categories)} categories"
    )

    for category, test_files in sorted(test_categories.items()):
        print(f"  {category}: {len(test_files)} tests")

    all_results = []
    failed_tests = []

    # Process each category (folder) as a single batch
    for category in sorted(test_categories.keys()):
        test_files = test_categories[category]
        batch_name = category

        # Run entire folder as one batch
        result = run_test_batch(test_files, batch_name)
        all_results.append(result)

        if not result["success"]:
            failed_tests.extend([(batch_name, f) for f in test_files])
            print(f"❌ Folder {batch_name} FAILED")
            print("STDERR:", result["stderr"][:500])
        else:
            print(
                f"✅ Folder {batch_name} passed in {result['elapsed_time']:.2f}s"
            )

        # Clean up memory after each batch
        gc.collect()

    # Summary
    print("\n" + "=" * 60)
    print("CONTRIB TEST SUMMARY")
    print("=" * 60)

    total_batches = len(all_results)
    successful_batches = sum(1 for r in all_results if r["success"])
    total_time = sum(r["elapsed_time"] for r in all_results)

    print(f"Total batches: {total_batches}")
    print(f"Successful: {successful_batches}")
    print(f"Failed: {total_batches - successful_batches}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Average time per batch: {total_time/total_batches:.2f}s")

    if failed_tests:
        print(f"\n❌ {len(failed_tests)} test files in failed batches:")
        for batch, test in failed_tests[:10]:  # Show first 10
            print(f"  - {batch}: {test}")
        if len(failed_tests) > 10:
            print(f"  ... and {len(failed_tests) - 10} more")

    # No longer saving results to JSON file

    # Exit with appropriate code
    sys.exit(0 if successful_batches == total_batches else 1)


if __name__ == "__main__":
    main()
