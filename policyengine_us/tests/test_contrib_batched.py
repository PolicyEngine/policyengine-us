#!/usr/bin/env python
"""
Run contrib tests in two batches with memory cleanup.
Batch 1: First half of contrib tests
Batch 2: Second half of contrib tests
"""

import subprocess
import sys
import os
import gc
import time
from pathlib import Path


def run_batch_isolated(test_files, batch_name, timeout_seconds):
    """
    Run a batch of test files in an isolated subprocess.
    Shows real-time output while also capturing it for analysis.
    """
    python_exe = sys.executable

    try:
        start_time = time.time()

        cmd = (
            [
                python_exe,
                "-m",
                "policyengine_core.scripts.policyengine_command",
                "test",
            ]
            + test_files
            + ["-c", "policyengine_us"]
        )

        print(f"    Running {batch_name} ({len(test_files)} test files)...")
        print("    " + "-" * 60)

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        output_lines = []
        passed_count = 0
        failed_count = 0
        current_test = None

        for line in process.stdout:
            output_lines.append(line)

            # Show which test file is being run
            if ".yaml" in line and ("test" in line or "Testing" in line):
                # Extract test file name
                import re

                match = re.search(r"(policyengine_us/tests/.*?\.yaml)", line)
                if match and match.group(1) != current_test:
                    current_test = match.group(1)
                    # Show just the file name being tested
                    short_name = current_test.split("/")[-1]
                    print(f"    Testing {short_name}...")

            # Only show the final summary lines
            if "passed" in line and "==" in line:
                print(f"    {line}", end="")

            if " passed" in line and "==" in line:
                import re

                match = re.search(r"(\d+) passed", line)
                if match:
                    passed_count = int(match.group(1))
            if " failed" in line and "==" in line:
                import re

                match = re.search(r"(\d+) failed", line)
                if match:
                    failed_count = int(match.group(1))

        process.wait(timeout=timeout_seconds)

        elapsed = time.time() - start_time
        output = "".join(output_lines)

        print("    " + "-" * 60)
        print(
            f"    Completed in {elapsed:.1f}s: {passed_count} passed, {failed_count} failed"
        )

        return {
            "batch_name": batch_name,
            "passed": passed_count,
            "failed": failed_count,
            "elapsed": elapsed,
            "status": "passed" if process.returncode == 0 else "failed",
            "stdout": output,
            "stderr": "",
        }

    except subprocess.TimeoutExpired:
        print(f"    Timeout after {timeout_seconds}s")
        process.kill()
        return {
            "batch_name": batch_name,
            "passed": 0,
            "failed": 0,
            "elapsed": timeout_seconds,
            "status": "timeout",
        }
    except Exception as e:
        print(f"    Error: {str(e)[:100]}")
        return {
            "batch_name": batch_name,
            "passed": 0,
            "failed": 0,
            "elapsed": 0,
            "status": "error",
        }


def main():
    """
    Run contrib tests in two batches:
    1. First half of test files
    2. Second half of test files
    """
    print("PolicyEngine Contrib Test Runner - Two Batch Strategy", flush=True)
    print("=" * 80, flush=True)
    print("Batch 1: First half of contrib tests", flush=True)
    print("Batch 2: Second half of contrib tests", flush=True)
    print("=" * 80, flush=True)

    contrib_path = Path("policyengine_us/tests/policy/contrib")

    # Group all test files by folder
    folder_files = {}
    for yaml_file in contrib_path.rglob("*.yaml"):
        parts = str(yaml_file).split("/")
        if len(parts) > 5:  # Has a subfolder under contrib
            folder_name = parts[4]
            if folder_name not in folder_files:
                folder_files[folder_name] = []
            folder_files[folder_name].append(str(yaml_file))

    if not folder_files:
        print("No contrib test files found")
        sys.exit(0)

    # Sort folders and files within each folder
    sorted_folders = sorted(folder_files.keys())
    for folder in sorted_folders:
        folder_files[folder].sort()

    # Show folder breakdown
    total_files = sum(len(files) for files in folder_files.values())
    print(
        f"\nFound {total_files} test files in {len(sorted_folders)} folders:"
    )
    for folder in sorted_folders:
        print(f"  {folder}: {len(folder_files[folder])} files")

    # Split folders into two batches (keeping all files from same folder together)
    midpoint = len(sorted_folders) // 2
    batch1_folders = sorted_folders[:midpoint]
    batch2_folders = sorted_folders[midpoint:]

    # Collect all files for each batch
    batch1_files = []
    for folder in batch1_folders:
        batch1_files.extend(folder_files[folder])

    batch2_files = []
    for folder in batch2_folders:
        batch2_files.extend(folder_files[folder])

    print(
        f"\n[Batch 1/2] Running {len(batch1_files)} test files from folders:"
    )
    print(f"  {', '.join(batch1_folders)}")
    batch1_results = run_batch_isolated(
        batch1_files, "Batch 1", timeout_seconds=2400
    )

    gc.collect()

    print(
        f"\n[Batch 2/2] Running {len(batch2_files)} test files from folders:"
    )
    print(f"  {', '.join(batch2_folders)}")
    batch2_results = run_batch_isolated(
        batch2_files, "Batch 2", timeout_seconds=2400
    )

    all_failed_tests = []

    if batch1_results["status"] == "failed" and batch1_results.get("stdout"):
        import re

        failed_tests = re.findall(
            r"FAILED (.*\.yaml.*?) -", batch1_results["stdout"]
        )
        all_failed_tests.extend(failed_tests)

    if batch2_results["status"] == "failed" and batch2_results.get("stdout"):
        import re

        failed_tests = re.findall(
            r"FAILED (.*\.yaml.*?) -", batch2_results["stdout"]
        )
        all_failed_tests.extend(failed_tests)

    print("\n" + "=" * 80)
    print("FINAL TEST SUMMARY")
    print("=" * 80)

    total_passed = batch1_results["passed"] + batch2_results["passed"]
    total_failed = batch1_results["failed"] + batch2_results["failed"]

    print(f"✓ Passed: {total_passed} tests")
    print(f"✗ Failed: {total_failed} tests")

    if all_failed_tests:
        print(f"\n❌ FAILED TEST FILES ({len(all_failed_tests)} total):")
        for test in all_failed_tests:
            print(f"  - {test}")

    return len(all_failed_tests) == 0


if __name__ == "__main__":
    if not os.path.exists("policyengine_us"):
        print("Error: Must run from PolicyEngine US root directory")
        sys.exit(1)

    success = main()
    sys.exit(0 if success else 1)
