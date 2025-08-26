#!/usr/bin/env python3
"""
Batch test runner for contrib tests with memory management.

Runs tests in smaller batches to prevent memory issues.
Tests are organized by subdirectory for better organization.
"""

import os
import sys
import json
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

    # Use the correct Python environment
    python_exe = "/opt/miniconda3/envs/policyengine/bin/python"
    if not os.path.exists(python_exe):
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

    result = subprocess.run(cmd, capture_output=True, text=True)

    elapsed_time = (datetime.now() - start_time).total_seconds()

    # Clean up
    if os.path.exists(test_list_file):
        os.remove(test_list_file)

    # Force garbage collection
    gc.collect()

    return {
        "batch_name": batch_name,
        "num_tests": len(test_files),
        "elapsed_time": elapsed_time,
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def get_batch_size(category: str) -> int:
    """Get batch size based on category."""
    # Categories with complex/slow tests get smaller batches
    BATCH_SIZES = {
        "congress": 3,  # Golden tests are very complex
        "taxsim": 3,  # Tax simulation comparisons are intensive
        "harris": 5,  # Complex policy reforms
        "states": 5,  # State-specific calculations
        "crfb": 5,  # Complex fiscal reforms
        "treasury": 5,  # Treasury analysis tests
        "federal": 8,  # Federal policy tests
        "reconciliation": 8,  # Budget reconciliation tests
        "snap": 10,  # SNAP policy tests
        "snap_ea": 10,  # SNAP EA tests
        "eitc": 10,  # EITC tests
        "ctc": 10,  # CTC tests
        "deductions": 10,  # Deduction tests
        "local": 10,  # Local policy tests
        "ubi_center": 10,  # UBI tests
    }

    # Default batch size for unknown categories
    return BATCH_SIZES.get(category, 10)


def main():
    """Main function to run all contrib tests in batches."""
    base_path = "policyengine_us/tests/policy/contrib"

    print("Finding contrib test files...")
    test_categories = find_test_files(base_path)

    total_files = sum(len(files) for files in test_categories.values())
    print(
        f"Found {total_files} test files in {len(test_categories)} categories"
    )

    for category, count in sorted(test_categories.items()):
        batch_size = get_batch_size(category)
        print(f"  {category}: {len(count)} tests (batch size: {batch_size})")

    all_results = []
    failed_tests = []

    # Process each category
    for category in sorted(test_categories.keys()):
        test_files = test_categories[category]
        batch_size = get_batch_size(category)

        # Split category into batches if needed
        for i in range(0, len(test_files), batch_size):
            batch_files = test_files[i : i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(test_files) + batch_size - 1) // batch_size

            if total_batches > 1:
                batch_name = f"{category}_batch_{batch_num}_of_{total_batches}"
            else:
                batch_name = category

            result = run_test_batch(batch_files, batch_name)
            all_results.append(result)

            if not result["success"]:
                failed_tests.extend([(batch_name, f) for f in batch_files])
                print(f"❌ Batch {batch_name} FAILED")
                print("STDERR:", result["stderr"][:500])
            else:
                print(
                    f"✅ Batch {batch_name} passed in {result['elapsed_time']:.2f}s"
                )

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

    # Save results to JSON
    results_file = "contrib_test_results_batched.json"
    with open(results_file, "w") as f:
        json.dump(
            {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_files": total_files,
                    "total_batches": total_batches,
                    "successful_batches": successful_batches,
                    "failed_batches": total_batches - successful_batches,
                    "total_time": total_time,
                    "categories": {
                        k: len(v) for k, v in test_categories.items()
                    },
                },
                "batch_results": all_results,
            },
            f,
            indent=2,
        )

    print(f"\nDetailed results saved to {results_file}")

    # Exit with appropriate code
    sys.exit(0 if successful_batches == total_batches else 1)


if __name__ == "__main__":
    main()
