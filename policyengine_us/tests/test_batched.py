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
import re
from pathlib import Path
from typing import List, Dict


def count_yaml_files(directory: Path) -> int:
    """Count YAML files in a directory recursively."""
    if not directory.exists():
        return 0
    return len(list(directory.rglob("*.yaml")))


def split_into_batches(
    base_path: Path,
    num_batches: int,
    exclude: List[str] = None,
    mode: str = "auto",
) -> List[List[str]]:
    """
    Split test directories into specified number of batches.
    Special handling for baseline tests to separate states.
    Special handling for contrib tests to divide by folder count.

    Args:
        base_path: Path to the test directory
        num_batches: Number of batches to split into
        exclude: List of directory names to exclude (for contrib tests)
        mode: Batching mode. "auto" (default) uses the per-path heuristics
            below. "per-subdir" runs each immediate subdir as its own batch
            with loose yamls collected into a trailing batch. "per-file"
            runs every yaml (recursively) as its own batch.
    """
    if exclude is None:
        exclude = []

    # Explicit modes — bypass the per-path auto heuristics so new files
    # added to the target auto-route without a Makefile edit.
    if mode == "per-file":
        return [[str(f)] for f in sorted(base_path.rglob("*.yaml"))]

    if mode == "per-subdir":
        subdirs = sorted(
            item
            for item in base_path.iterdir()
            if item.is_dir() and item.name not in exclude
        )
        root_files = sorted(base_path.glob("*.yaml"))
        batches = [[str(s)] for s in subdirs]
        if root_files:
            batches.append([str(f) for f in root_files])
        return batches

    # Special handling for contrib tests - one batch per heavy folder.
    # Only apply to policy/contrib (structural tests), not baseline/contrib.
    #
    # Prior grouping (3 folders per batch) pushed peak memory to ~8-9 GB
    # per subprocess, which OOMs the 16 GB ubuntu-latest runner once
    # policyengine-core 3.24+ overhead is added, surfacing as
    # "The runner has received a shutdown signal" mid-batch. Giving each
    # heavy folder its own batch keeps peaks under ~5 GB and eliminates
    # the intermittent failures without reducing total coverage.
    if str(base_path).endswith("policy/contrib"):
        # Heavy folders each get their own batch (~3-5 GB peak each) so
        # a single subprocess doesn't exceed the 16 GB runner cap.
        HEAVY = {
            "federal",
            "harris",
            "treasury",
            "ctc",
            "snap_ea",
            "ubi_center",
            "deductions",
            "aca",
            "snap",
            "tax_exempt",
            "eitc",
            "crfb",
            "congress",
        }

        subdirs = sorted(
            item
            for item in base_path.iterdir()
            if item.is_dir() and item.name not in exclude
        )
        root_files = sorted(base_path.glob("*.yaml"))

        # One batch per heavy subdir (if present).
        batches = [[str(subdir)] for subdir in subdirs if subdir.name in HEAVY]

        # Catch-all batch for everything else — light subdirs and root
        # yaml files. Auto-collects any newly added folders/files so
        # they're exercised without extra config.
        light_paths = [
            str(subdir) for subdir in subdirs if subdir.name not in HEAVY
        ] + [str(f) for f in root_files]
        if light_paths:
            batches.append(light_paths)

        return batches

    # Special handling for contrib/states - each subfolder is its own batch
    # to allow garbage collection between state tests
    # Memory usage per state varies significantly (1.3 GB - 5.2 GB measured)
    # Note: contrib/congress runs all together (~6.3 GB total, under 7 GB limit)
    if str(base_path).endswith("contrib/states"):
        subdirs = sorted([item for item in base_path.iterdir() if item.is_dir()])
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
    # and splitting into multiple sequential batches for memory management
    if str(base_path).endswith("gov/states"):
        subdirs = sorted(
            [
                item
                for item in base_path.iterdir()
                if item.is_dir() and item.name not in exclude
            ]
        )
        # Root-level YAML files (e.g. cross-state filing-status test) are
        # state-agnostic and would be invisible to subdir-based batching
        # otherwise — collect them into a dedicated trailing batch.
        root_files = sorted(base_path.glob("*.yaml"))

        if not subdirs and not root_files:
            return []
        # Split into num_batches sequential groups
        if num_batches > 1:
            chunk_size = len(subdirs) // num_batches
            remainder = len(subdirs) % num_batches
            batches = []
            start = 0
            for i in range(num_batches):
                end = start + chunk_size + (1 if i < remainder else 0)
                batch = [str(s) for s in subdirs[start:end]]
                if batch:
                    batches.append(batch)
                start = end
            if root_files:
                batches.append([str(f) for f in root_files])
            return batches
        batches = []
        if subdirs:
            batches.append([str(subdir) for subdir in subdirs])
        if root_files:
            batches.append([str(f) for f in root_files])
        return batches

    # Special handling for baseline tests
    if "baseline" in str(base_path) and str(base_path).endswith("baseline"):
        states_path = base_path / "gov" / "states"

        # If --exclude states, skip states and run everything else
        # Split into memory-aware batches to prevent OOM on CI (~7 GB limit)
        # Measured peak memory per gov/ subfolder (individual runs):
        #   irs: 4.4 GB, ssa: 4.0 GB, simulation: 4.0 GB,
        #   usda: 3.0 GB, hhs: 2.7 GB, local: 2.3 GB,
        #   others: ~1.3-1.7 GB each
        if "states" in exclude:
            gov_path = base_path / "gov"

            # One batch per heavy gov/ folder (~3-4 GB peak each) so no
            # subprocess exceeds ~5 GB. Grouping previously-paired folders
            # (usda+hhs) pushed peak memory past the 16 GB runner cap once
            # policyengine-core 3.24+ overhead landed.
            HEAVY = ["irs", "ssa", "simulation", "usda", "hhs"]

            def collect_gov_paths(folder_names):
                """Collect paths for specific gov/ subfolders."""
                paths = []
                for name in folder_names:
                    p = gov_path / name
                    if p.exists():
                        paths.append(str(p))
                return paths

            # Collect remaining gov/ subfolders and files
            remaining = []
            heavy_set = set(HEAVY)
            for gov_item in gov_path.iterdir():
                if gov_item.is_dir():
                    if gov_item.name not in heavy_set and gov_item.name != "states":
                        remaining.append(str(gov_item))
                elif gov_item.suffix == ".yaml":
                    remaining.append(str(gov_item))

            # Add non-gov directories and root YAML files
            for item in base_path.iterdir():
                if item.is_dir():
                    if item.name in ["household", "contrib", "gov"]:
                        continue
                    remaining.append(str(item))
                elif item.suffix == ".yaml":
                    remaining.append(str(item))

            # Build batches (only include non-empty ones)
            batches = []
            for folder_name in HEAVY:
                paths = collect_gov_paths([folder_name])
                if paths:
                    batches.append(paths)
            if remaining:
                batches.append(remaining)

            return batches

    # Default: honor num_batches and exclude generically. The cheapest
    # common case (no chunking, no exclusion) returns the base_path as a
    # single batch so policyengine-core walks the tree once. Otherwise we
    # enumerate explicit paths — necessary because the test runner has no
    # way to skip excluded subpaths on its own, and because splitting into
    # multiple subprocesses requires discrete path lists.
    if num_batches <= 1 and not exclude:
        return [[str(base_path)]]

    if exclude:
        # Exclude applies to immediate children by name (same semantics as
        # the special-branch excludes above). Previously, `--exclude` in
        # the default branch was silently ignored, causing duplicated
        # work — e.g. `ny --exclude tax` still re-ran every `tax/*` test.
        paths = sorted(
            str(item)
            for item in base_path.iterdir()
            if (item.is_dir() or item.suffix == ".yaml") and item.name not in exclude
        )
    else:
        paths = sorted(str(f) for f in base_path.rglob("*.yaml"))

    if not paths:
        return []

    if num_batches <= 1:
        return [paths]

    chunk_size = len(paths) // num_batches
    remainder = len(paths) % num_batches
    batches = []
    start = 0
    for i in range(num_batches):
        end = start + chunk_size + (1 if i < remainder else 0)
        chunk = paths[start:end]
        if chunk:
            batches.append(chunk)
        start = end
    return batches


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
            if re.search(r"=+.*\d+\s+(passed|failed).*in\s+[\d.]+s.*=+", line):
                test_completed = True
                # Check if tests passed by parsing actual failure count
                failed_match = re.search(r"(\d+) failed", line)
                if failed_match:
                    failed_count = int(failed_match.group(1))
                    test_passed = failed_count == 0
                else:
                    # No "X failed" in line means all passed
                    test_passed = True

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
    parser.add_argument(
        "--shard",
        type=str,
        default=None,
        help="Run a shard of the batches across parallel CI runners (format: 'I/N'; 1-indexed)",
    )
    parser.add_argument(
        "--mode",
        choices=["auto", "per-subdir", "per-file"],
        default="auto",
        help="Batching mode. 'per-subdir' = each immediate subdir is its own batch; 'per-file' = each yaml is its own batch.",
    )

    args = parser.parse_args()
    exclude_list = [x.strip() for x in args.exclude.split(",") if x.strip()]

    shard_idx = shard_count = None
    if args.shard:
        try:
            shard_idx, shard_count = (int(x) for x in args.shard.split("/"))
        except ValueError:
            print(f"Error: --shard must be in format 'I/N' (got {args.shard!r})")
            sys.exit(1)
        if not (1 <= shard_idx <= shard_count):
            print(f"Error: --shard I must satisfy 1 <= I <= N (got {args.shard!r})")
            sys.exit(1)

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
    batches = split_into_batches(test_path, args.batches, exclude_list, args.mode)

    # Apply sharding: slice every Nth batch starting from the shard index.
    # Alphabetical subfolder ordering means new folders auto-distribute by
    # position rather than requiring manual re-assignment per runner.
    if shard_count is not None:
        all_batch_count = len(batches)
        batches = batches[shard_idx - 1 :: shard_count]
        print(
            f"Sharding: running shard {shard_idx}/{shard_count} "
            f"({len(batches)} of {all_batch_count} batches)"
        )

    if len(batches) != args.batches:
        print(f"Actual batches: {len(batches)} (optimized for {total_tests} files)")
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
            count_yaml_files(Path(p)) if Path(p).is_dir() else 1 for p in batch_paths
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
