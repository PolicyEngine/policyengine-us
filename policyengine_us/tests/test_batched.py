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


def split_into_batches(
    base_path: Path, num_batches: int, exclude: List[str] = None
) -> List[List[str]]:
    """
    Split test directories into specified number of batches.
    Special handling for baseline tests to separate states.
    Special handling for contrib tests to divide by folder count.

    Args:
        base_path: Path to the test directory
        num_batches: Number of batches to split into
        exclude: List of directory names to exclude (for contrib tests)
    """
    if exclude is None:
        exclude = []

    # Special handling for contrib tests - split into 7 batches by memory usage
    # Only apply to policy/contrib (structural tests), not baseline/contrib
    if str(base_path).endswith("policy/contrib"):
        # Define batches by memory usage (measured empirically)
        BATCH_1 = ["federal", "harris", "treasury"]  # ~9.0 GB
        BATCH_2 = ["ctc", "snap_ea", "ubi_center"]  # ~8.6 GB
        BATCH_3 = ["deductions", "aca", "snap"]  # ~8.1 GB
        BATCH_4 = [
            "tax_exempt",
            "eitc",
            "state_dependent_exemptions",
            "additional_tax_bracket",
        ]  # ~8.0 GB
        # Batch 5 is the catch-all for unknown/new folders (~7.8 GB + headroom)
        BATCH_5_DEFINED = [
            "local",
            "dc_single_joint_threshold_ratio.yaml",
            "reconciliation",
            "dc_kccatc.yaml",
            "reported_state_income_tax.yaml",
        ]
        BATCH_6 = ["crfb"]  # ~8.9 GB, always alone
        BATCH_7 = ["congress"]  # ~6.3 GB

        # Get all subdirectories (excluding states which is in Heavy job)
        subdirs = sorted(
            [
                item
                for item in base_path.iterdir()
                if item.is_dir() and item.name not in exclude
            ]
        )

        # Get root level YAML files
        root_files = sorted(list(base_path.glob("*.yaml")))

        # Build batches
        def get_batch_paths(batch_names, subdirs, root_files):
            paths = []
            for name in batch_names:
                # Check if it's a directory
                for subdir in subdirs:
                    if subdir.name == name:
                        paths.append(str(subdir))
                        break
                # Check if it's a root file
                for f in root_files:
                    if f.name == name:
                        paths.append(str(f))
                        break
            return paths

        # Collect known folders/files
        all_known = set(
            BATCH_1
            + BATCH_2
            + BATCH_3
            + BATCH_4
            + BATCH_5_DEFINED
            + BATCH_6
            + BATCH_7
        )

        # Find unknown folders/files (new additions go to Batch 5)
        unknown = []
        for subdir in subdirs:
            if subdir.name not in all_known:
                unknown.append(str(subdir))
        for f in root_files:
            if f.name not in all_known:
                unknown.append(str(f))

        # Build all batches
        batch1 = get_batch_paths(BATCH_1, subdirs, root_files)
        batch2 = get_batch_paths(BATCH_2, subdirs, root_files)
        batch3 = get_batch_paths(BATCH_3, subdirs, root_files)
        batch4 = get_batch_paths(BATCH_4, subdirs, root_files)
        batch5 = (
            get_batch_paths(BATCH_5_DEFINED, subdirs, root_files) + unknown
        )
        batch6 = get_batch_paths(BATCH_6, subdirs, root_files)
        batch7 = get_batch_paths(BATCH_7, subdirs, root_files)

        # Return non-empty batches in order
        batches = []
        for batch in [batch1, batch2, batch3, batch4, batch5, batch6, batch7]:
            if batch:
                batches.append(batch)

        return batches

    # Special handling for contrib/states - each subfolder is its own batch
    # to allow garbage collection between state tests
    # Memory usage per state varies significantly (1.3 GB - 5.2 GB measured)
    # Note: contrib/congress runs all together (~6.3 GB total, under 7 GB limit)
    if str(base_path).endswith("contrib/states"):
        subdirs = sorted(
            [item for item in base_path.iterdir() if item.is_dir()]
        )
        # Each state folder becomes its own batch
        batches = [[str(subdir)] for subdir in subdirs]

        # Also include any root-level YAML files as a separate batch
        root_files = sorted(list(base_path.glob("*.yaml")))
        if root_files:
            batches.append([str(file) for file in root_files])

        return batches if batches else [[str(base_path)]]

    # Special handling for reform tests - run all together in one batch
    if "reform" in str(base_path):
        return [[str(base_path)]]

    # Special handling for states directory - support excluding specific states
    if str(base_path).endswith("gov/states"):
        subdirs = sorted(
            [
                item
                for item in base_path.iterdir()
                if item.is_dir() and item.name not in exclude
            ]
        )
        # Return all non-excluded state directories as a single batch
        if subdirs:
            return [[str(subdir) for subdir in subdirs]]
        return []

    # Special handling for baseline tests
    if "baseline" in str(base_path) and str(base_path).endswith("baseline"):
        states_path = base_path / "gov" / "states"

        # If --exclude states, skip states and run everything else
        if "states" in exclude:
            batch = []

            # Add root level files if any
            for yaml_file in base_path.glob("*.yaml"):
                batch.append(str(yaml_file))

            # Add all directories except gov/states, household, and contrib
            for item in base_path.iterdir():
                if item.is_dir():
                    # Skip household and contrib directories (they'll be run separately)
                    if item.name in ["household", "contrib"]:
                        continue
                    elif item.name == "gov":
                        # Add gov subdirectories except states
                        for gov_item in item.iterdir():
                            if gov_item.is_dir() and gov_item.name != "states":
                                batch.append(str(gov_item))
                            elif gov_item.suffix == ".yaml":
                                batch.append(str(gov_item))
                    else:
                        # Other non-gov directories
                        batch.append(str(item))

            return [batch] if batch else []

    # Default: return the entire path as a single batch
    return [[str(base_path)]]


def run_batch(test_paths: List[str], batch_name: str) -> Dict:
    """Run a batch of tests in an isolated subprocess."""

    python_exe = sys.executable

    start_time = time.time()

    # Build command - direct policyengine-core with timeout protection
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

    # Use Popen for more control over process lifecycle
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,  # Line buffered
    )

    try:
        test_completed = False
        test_passed = False
        output_lines = []

        # Monitor output line by line
        while True:
            line = process.stdout.readline()
            if not line:
                # No more output, check if process is done
                poll_result = process.poll()
                if poll_result is not None:
                    # Process terminated
                    break
                # Process still running but no output
                time.sleep(0.1)
                continue

            # Print line in real-time
            print(line, end="")
            output_lines.append(line)

            # Detect pytest completion
            # Look for patterns like "====== 5638 passed in 491.24s ======"
            # or "====== 2 failed, 5636 passed in 500s ======"
            import re

            if re.search(r"=+.*\d+\s+(passed|failed).*in\s+[\d.]+s.*=+", line):
                test_completed = True
                # Check if tests passed (no failures mentioned or 0 failed)
                if "failed" not in line or "0 failed" in line:
                    test_passed = True
                else:
                    test_passed = False

                print(f"\n    Tests completed, terminating process...")

                # Give 5 seconds grace period for cleanup
                time.sleep(5)

                # Terminate the process
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if it won't terminate
                    print(f"    Force killing process...")
                    process.kill()
                    process.wait()
                break

        # If we didn't detect completion, wait for process with timeout
        if not test_completed:
            try:
                # Wait up to 30 minutes total
                elapsed = time.time() - start_time
                remaining_timeout = max(1800 - elapsed, 1)
                process.wait(timeout=remaining_timeout)
            except subprocess.TimeoutExpired:
                print(f"\n    ⏱️ Timeout - terminating process...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()

                elapsed = time.time() - start_time
                return {
                    "elapsed": elapsed,
                    "status": "timeout",
                }

        elapsed = time.time() - start_time

        if test_completed:
            print(f"\n    Batch completed in {elapsed:.1f}s")
            return {
                "elapsed": elapsed,
                "status": "passed" if test_passed else "failed",
            }
        else:
            # Process ended without detecting test completion
            returncode = process.poll()
            print(f"\n    Batch completed in {elapsed:.1f}s")
            return {
                "elapsed": elapsed,
                "status": "passed" if returncode == 0 else "failed",
            }

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n    ❌ Error: {str(e)[:100]}")

        # Clean up process if still running
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            try:
                process.kill()
                process.wait()
            except:
                pass

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
    parser.add_argument(
        "--exclude",
        type=str,
        default="",
        help="Comma-separated list of directory names to exclude (for contrib tests)",
    )

    args = parser.parse_args()
    exclude_list = [x.strip() for x in args.exclude.split(",") if x.strip()]

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
    print(f"Requested batches: {args.batches}")
    if exclude_list:
        print(f"Excluding: {', '.join(exclude_list)}")

    # Count total tests
    total_tests = count_yaml_files(test_path)
    print(f"Total test files: {total_tests}")

    # Split into batches
    batches = split_into_batches(test_path, args.batches, exclude_list)
    if len(batches) != args.batches:
        print(
            f"Actual batches: {len(batches)} (optimized for {total_tests} files)"
        )
    else:
        print(f"Actual batches: {len(batches)}")
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

        # Memory cleanup after each batch
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
