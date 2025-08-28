#!/usr/bin/env python
"""
Generic test runner that can split tests into batches for memory management.
Can be used for any test folder with configurable batch count.
"""

import subprocess
import sys
import os
import gc
import time
import argparse
from pathlib import Path
from typing import List, Dict


def count_yaml_files(directory: Path) -> int:
    """Count YAML files in a directory recursively."""
    if not directory.exists():
        return 0
    return len(list(directory.rglob("*.yaml")))


def get_test_directories(base_path: Path) -> Dict[str, int]:
    """Get all subdirectories and their test counts."""
    dir_counts = {}

    # Check for yaml files directly in base directory
    root_count = len(list(base_path.glob("*.yaml")))
    if root_count > 0:
        dir_counts["."] = root_count

    # Get all subdirectories with their test counts
    for item in base_path.iterdir():
        if item.is_dir():
            yaml_count = count_yaml_files(item)
            if yaml_count > 0:
                dir_counts[item.name] = yaml_count

    return dir_counts


def split_into_batches(base_path: Path, num_batches: int) -> List[List[str]]:
    """
    Split test directories into specified number of batches.
    Special handling for baseline tests to separate states.
    """
    # Special handling for baseline tests with 2 batches
    if "baseline" in str(base_path) and num_batches == 2:
        states_path = base_path / "gov" / "states"
        if states_path.exists() and count_yaml_files(states_path) > 0:
            # Batch 1: Only states
            batch1 = [str(states_path)]

            # Batch 2: Everything else (excluding states)
            batch2 = []

            # Add root level files if any
            for yaml_file in base_path.glob("*.yaml"):
                batch2.append(str(yaml_file))

            # Add all directories except gov/states
            for item in base_path.iterdir():
                if item.is_dir():
                    if item.name == "gov":
                        # Add gov subdirectories except states
                        for gov_item in item.iterdir():
                            if gov_item.is_dir() and gov_item.name != "states":
                                batch2.append(str(gov_item))
                            elif gov_item.suffix == ".yaml":
                                batch2.append(str(gov_item))
                    else:
                        # Non-gov directories
                        batch2.append(str(item))

            return [batch1, batch2] if batch2 else [batch1]

    # Default behavior for non-baseline or different batch counts
    dir_counts = get_test_directories(base_path)

    if num_batches <= 0:
        num_batches = 1

    # If only 1 batch, return everything
    if num_batches == 1:
        return [[str(base_path)]]

    # Sort directories by test count (largest first)
    sorted_dirs = sorted(dir_counts.items(), key=lambda x: x[1], reverse=True)

    # Initialize batches
    batches = [[] for _ in range(num_batches)]
    batch_counts = [0] * num_batches

    # Distribute directories to batches (greedy algorithm - add to smallest batch)
    for dir_name, count in sorted_dirs:
        # Find batch with fewest tests
        min_batch_idx = batch_counts.index(min(batch_counts))

        # Add directory to that batch
        if dir_name == ".":
            # Root level files - add individually
            for yaml_file in base_path.glob("*.yaml"):
                batches[min_batch_idx].append(str(yaml_file))
        else:
            batches[min_batch_idx].append(str(base_path / dir_name))

        batch_counts[min_batch_idx] += count

    # Filter out empty batches
    return [batch for batch in batches if batch]


def run_batch(test_paths: List[str], batch_name: str) -> Dict:
    """Run a batch of tests in an isolated subprocess."""

    python_exe = sys.executable

    start_time = time.time()

    # Build command
    cmd = (
        [
            python_exe,
            "-m",
            "policyengine_core.scripts.policyengine_command",
            "test",
        ]
        + test_paths
        + ["-c", "policyengine_us"]
    )

    print(f"    Running {batch_name}...")
    print(f"    Paths: {len(test_paths)} items")
    print()

    try:
        # Run and let pytest output show through
        result = subprocess.run(
            cmd,
            timeout=2400,  # 40 minute timeout (increased for safety)
            capture_output=False,  # Let output show in real-time
            text=True,
        )

        elapsed = time.time() - start_time

        # Only show completion message if we actually completed
        if result is not None:
            print(f"\n    Batch completed in {elapsed:.1f}s")
            return {
                "elapsed": elapsed,
                "status": "passed" if result.returncode == 0 else "failed",
            }

    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        print(f"\n    ⏱️ Timeout after {elapsed:.1f}s")
        return {
            "elapsed": elapsed,
            "status": "timeout",
        }
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n    ❌ Error: {str(e)[:100]}")
        return {
            "elapsed": elapsed,
            "status": "error",
        }


def main():
    """Main entry point for the generic test runner."""

    parser = argparse.ArgumentParser(
        description="Run tests in batches with memory cleanup between batches"
    )
    parser.add_argument("test_path", help="Path to the test directory")
    parser.add_argument(
        "--batches",
        type=int,
        default=2,
        help="Number of batches to split tests into (default: 2)",
    )

    args = parser.parse_args()

    if not os.path.exists("policyengine_us"):
        print("Error: Must run from PolicyEngine US root directory")
        sys.exit(1)

    test_path = Path(args.test_path)
    if not test_path.exists():
        print(f"Error: Test path does not exist: {args.test_path}")
        sys.exit(1)

    print(f"PolicyEngine Test Runner")
    print("=" * 60)
    print(f"Test path: {test_path}")
    print(f"Number of batches: {args.batches}")

    # Count total tests
    total_tests = count_yaml_files(test_path)
    print(f"Total test files: {total_tests}")

    # Split into batches
    batches = split_into_batches(test_path, args.batches)
    print(f"Created {len(batches)} batch(es)")
    print("=" * 60)

    # Run batches
    all_failed = False
    total_elapsed = 0

    for i, batch_paths in enumerate(batches, 1):
        print(f"\n[Batch {i}/{len(batches)}]")

        # Show what's in this batch
        batch_test_count = sum(
            count_yaml_files(Path(p)) if Path(p).is_dir() else 1
            for p in batch_paths
        )
        print(f"  Test files: ~{batch_test_count}")
        print("-" * 60)

        result = run_batch(batch_paths, f"Batch {i}")
        total_elapsed += result["elapsed"]

        if result["status"] != "passed":
            all_failed = True

        # Memory cleanup between batches (except after last batch)
        if i < len(batches):
            print("  Cleaning up memory...")
            gc.collect()

    # Final summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total test files: {total_tests}")
    print(f"Total time: {total_elapsed:.1f}s")

    # Exit code
    sys.exit(1 if all_failed else 0)


if __name__ == "__main__":
    main()
