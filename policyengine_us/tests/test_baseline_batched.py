#!/usr/bin/env python
"""
Run baseline tests in two batches with memory cleanup.
Batch 1: All state tests (gov/states)
Batch 2: Everything else in baseline
"""

import subprocess
import sys
import os
import gc
import time
from pathlib import Path


def run_batch_isolated(test_dirs, batch_name, timeout_seconds):
    """
    Run a batch of test directories in an isolated subprocess.
    Shows real-time output while also capturing it for analysis.
    """
    # Use the current Python executable (works with uv run, conda, etc.)
    python_exe = sys.executable

    # Convert to list of directory strings
    test_dirs_list = [str(d) for d in test_dirs]

    try:
        start_time = time.time()

        # Run all directories in one command
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

        print(f"    Running {batch_name}...")
        print("    " + "-" * 60)

        # Use Popen to show real-time output while capturing
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

        # Read output line by line and display it
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

            # Extract test counts from output
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

        # Wait for process to complete
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
    Run baseline tests in two batches:
    1. All state tests (gov/states)
    2. Everything else in baseline
    """
    print("PolicyEngine Baseline Test Runner - Two Batch Strategy", flush=True)
    print("=" * 80, flush=True)
    print("Batch 1: All state tests (gov/states)", flush=True)
    print("Batch 2: Everything else in baseline", flush=True)
    print("=" * 80, flush=True)

    baseline_path = Path("policyengine_us/tests/policy/baseline")

    # Define the two batches
    states_path = baseline_path / "gov" / "states"

    # Batch 1: All states
    print("\n[Batch 1/2] Running all state tests")
    print(f"  Directory: {states_path}")

    batch1_results = run_batch_isolated(
        [states_path], "State tests", timeout_seconds=1200  # 20 minutes
    )

    # Clean up memory after batch 1
    gc.collect()

    # Batch 2: Everything else (collect all other directories)
    print("\n[Batch 2/2] Running all other baseline tests")

    # Find all test directories except gov/states
    other_dirs = []

    # Add all top-level directories in baseline except those we already ran
    for item in baseline_path.iterdir():
        if item.is_dir():
            if item.name == "gov":
                # Add gov subdirectories except states
                gov_path = baseline_path / "gov"
                for gov_item in gov_path.iterdir():
                    if gov_item.is_dir() and gov_item.name != "states":
                        other_dirs.append(str(gov_item))
                # Also add any yaml files directly in gov/
                gov_yamls = list(gov_path.glob("*.yaml"))
                if gov_yamls:
                    # Run the gov directory itself to catch direct yaml files
                    other_dirs.append(str(gov_path))
            else:
                # Add non-gov directories
                other_dirs.append(str(item))

    if not other_dirs:
        print("  No other directories found")
        batch2_results = {
            "batch_name": "Other tests",
            "passed": 0,
            "failed": 0,
            "elapsed": 0,
            "status": "passed",
        }
    else:
        print(
            f"  Directories: {', '.join([Path(d).name for d in other_dirs])}"
        )
        batch2_results = run_batch_isolated(
            other_dirs,
            "Other baseline tests",
            timeout_seconds=1200,  # 20 minutes
        )

    # Collect all failed tests
    all_failed_tests = []

    # Extract failed tests from batch 1
    if batch1_results["status"] == "failed" and batch1_results.get("stdout"):
        import re

        failed_tests = re.findall(
            r"FAILED (.*\.yaml.*?) -", batch1_results["stdout"]
        )
        all_failed_tests.extend(failed_tests)

    # Extract failed tests from batch 2
    if batch2_results["status"] == "failed" and batch2_results.get("stdout"):
        import re

        failed_tests = re.findall(
            r"FAILED (.*\.yaml.*?) -", batch2_results["stdout"]
        )
        all_failed_tests.extend(failed_tests)

    # Final summary
    print("\n" + "=" * 80)
    print("FINAL TEST SUMMARY")
    print("=" * 80)

    total_passed = batch1_results["passed"] + batch2_results["passed"]
    total_failed = batch1_results["failed"] + batch2_results["failed"]

    print(f"✓ Passed: {total_passed} tests")
    print(f"✗ Failed: {total_failed} tests")

    # Show all failed tests at the end
    if all_failed_tests:
        print(f"\n❌ FAILED TEST FILES ({len(all_failed_tests)} total):")
        for test in all_failed_tests:
            print(f"  - {test}")

    # Return success if all tests passed
    return len(all_failed_tests) == 0


if __name__ == "__main__":
    if not os.path.exists("policyengine_us"):
        print("Error: Must run from PolicyEngine US root directory")
        sys.exit(1)

    success = main()
    sys.exit(0 if success else 1)
