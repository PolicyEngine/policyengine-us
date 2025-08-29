#!/usr/bin/env python
"""
Coverage-compatible test runner that runs tests in-process for proper coverage tracking.
Unlike test_batched.py, this doesn't use subprocesses so coverage can track the actual code.
"""

import sys
import gc
import time
import argparse
from pathlib import Path
from typing import List


def count_yaml_files(directory: Path) -> int:
    """Count YAML files in a directory recursively."""
    if not directory.exists():
        return 0
    return len(list(directory.rglob("*.yaml")))


def split_into_batches(base_path: Path, num_batches: int) -> List[List[str]]:
    """
    Split test directories into specified number of batches.
    Reuses logic from test_batched.py for consistency.
    """
    # Special handling for contrib tests - each folder is its own batch
    if "contrib" in str(base_path):
        subdirs = sorted(
            [item for item in base_path.iterdir() if item.is_dir()]
        )
        root_files = sorted(list(base_path.glob("*.yaml")))

        batches = []
        for subdir in subdirs:
            batches.append([str(subdir)])

        if root_files:
            root_batch = [str(file) for file in root_files]
            batches.append(root_batch)

        return batches

    # Special handling for reform tests - run all together in one batch
    if "reform" in str(base_path):
        return [[str(base_path)]]

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

    # Default: divide files evenly
    all_items = []

    # Collect all test files and directories
    def collect_items(path: Path):
        items = []
        for item in path.rglob("*.yaml"):
            items.append(str(item))
        return items

    all_items = collect_items(base_path)

    if not all_items:
        return [[str(base_path)]]

    # Divide items into batches
    batch_size = len(all_items) // num_batches + (
        1 if len(all_items) % num_batches else 0
    )
    batches = []

    for i in range(0, len(all_items), batch_size):
        batch = all_items[i : i + batch_size]
        if batch:
            batches.append(batch)

    return batches


def run_batch_in_process(test_paths: List[str], batch_name: str) -> bool:
    """
    Run tests directly in current process so coverage can track them.
    Returns True if tests passed, False otherwise.
    """
    print(f"\n[{batch_name}]")
    print(f"  Test paths: {len(test_paths)} items")
    print("-" * 60)

    start_time = time.time()

    # Import here to avoid issues if not installed
    try:
        from policyengine_core.scripts.policyengine_command import (
            main as policyengine_main,
        )
    except ImportError:
        print("Error: policyengine-core not installed")
        return False

    # Save original argv
    original_argv = sys.argv

    try:
        # Set up argv for policyengine-core test command
        sys.argv = (
            ["policyengine-core", "test"]
            + test_paths
            + ["-c", "policyengine_us"]
        )

        print(f"    Running {batch_name}...")
        print(
            f"    Command: policyengine-core test [paths] -c policyengine_us"
        )
        print()

        # Run tests in current process
        # This allows coverage to track the actual code being tested
        result = policyengine_main()

        elapsed = time.time() - start_time
        print(f"\n    Batch completed in {elapsed:.1f}s")

        # Clean up memory after batch
        print("  Cleaning up memory...")
        gc.collect()

        # policyengine_main returns 0 for success, non-zero for failure
        return result == 0

    except SystemExit as e:
        # policyengine_main might call sys.exit()
        elapsed = time.time() - start_time
        print(f"\n    Batch completed in {elapsed:.1f}s")
        print("  Cleaning up memory...")
        gc.collect()
        return e.code == 0

    except Exception as e:
        print(f"\n    Error running batch: {e}")
        return False

    finally:
        # Restore original argv
        sys.argv = original_argv


def main():
    parser = argparse.ArgumentParser(
        description="Run tests in batches for memory management (coverage-compatible)"
    )
    parser.add_argument("test_path", help="Path to test directory")
    parser.add_argument(
        "--batches",
        type=int,
        default=1,
        help="Number of batches to split tests into (default: 1)",
    )

    args = parser.parse_args()

    test_path = Path(args.test_path)
    if not test_path.exists():
        print(f"Error: Test path {test_path} does not exist")
        sys.exit(1)

    # Print header
    print("\nPolicyEngine Test Runner (Coverage-Compatible)")
    print("=" * 60)
    print(f"Test path: {test_path}")
    print(f"Requested batches: {args.batches}")

    # Count total test files
    total_tests = count_yaml_files(test_path)
    print(f"Total test files: {total_tests}")

    # Split into batches
    batches = split_into_batches(test_path, args.batches)
    actual_batches = len(batches)
    print(f"Actual batches: {actual_batches}")
    print("=" * 60)

    # Run each batch
    all_passed = True
    total_elapsed = 0

    for i, batch_paths in enumerate(batches, 1):
        batch_name = f"Batch {i}/{actual_batches}"

        # Count files in this batch
        batch_file_count = sum(
            count_yaml_files(Path(p)) if Path(p).is_dir() else 1
            for p in batch_paths
        )

        print(f"\n[Batch {i}/{actual_batches}]")
        print(f"  Test files: ~{batch_file_count}")
        print("-" * 60)

        start_time = time.time()
        passed = run_batch_in_process(batch_paths, batch_name)
        elapsed = time.time() - start_time
        total_elapsed += elapsed

        if not passed:
            all_passed = False
            print(f"  ❌ Batch {i} failed")
        else:
            print(f"  ✅ Batch {i} passed")

    # Final summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total test files: {total_tests}")
    print(f"Total time: {total_elapsed:.1f}s")
    print(f"Result: {'✅ PASSED' if all_passed else '❌ FAILED'}")
    print("=" * 60)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
