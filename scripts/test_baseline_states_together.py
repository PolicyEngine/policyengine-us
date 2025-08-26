#!/usr/bin/env python3
"""
Test all states together instead of individually.
This is much faster but uses more memory.
"""

import os
import sys
import subprocess
import gc
from pathlib import Path
import time
import json


def run_all_states_together():
    """Run all state tests in one batch."""
    baseline = "policyengine_us/tests/policy/baseline"
    states_path = Path(f"{baseline}/gov/states")

    # Collect all state test files
    all_state_files = []
    state_counts = {}

    for state_dir in states_path.iterdir():
        if state_dir.is_dir():
            state_name = state_dir.name
            yaml_files = list(state_dir.rglob("*.yaml"))
            if yaml_files:
                state_counts[state_name] = len(yaml_files)
                all_state_files.extend(yaml_files)

    print(
        f"Found {len(state_counts)} states with {len(all_state_files)} total test files"
    )
    print(f"Testing all states together in ONE batch...")

    # Convert to string paths
    test_files = [str(f) for f in all_state_files]

    # Use the correct Python environment
    python_exe = "/opt/miniconda3/envs/policyengine/bin/python"
    if not os.path.exists(python_exe):
        python_exe = sys.executable

    # Run the tests
    cmd = [
        python_exe,
        "-m",
        "policyengine_core.scripts.policyengine_command",
        "test",
        *test_files,
        "-c",
        "policyengine_us",
    ]

    start_time = time.time()
    print(f"\nStarting tests at {time.strftime('%H:%M:%S')}")
    print("Expected duration: 30-40 minutes")
    print("-" * 60)

    result = subprocess.run(cmd, capture_output=True, text=True)

    elapsed_time = time.time() - start_time

    print(f"\nCompleted in {elapsed_time/60:.1f} minutes")
    print(f"Status: {'✅ PASSED' if result.returncode == 0 else '❌ FAILED'}")

    # Parse output to count passed/failed
    if result.stdout:
        lines = result.stdout.split("\n")
        for line in lines[-20:]:  # Check last 20 lines for summary
            if "passed" in line.lower() or "failed" in line.lower():
                print(line)

    return result.returncode == 0, elapsed_time, len(all_state_files)


def run_other_baseline_tests():
    """Run non-state baseline tests."""
    baseline = "policyengine_us/tests/policy/baseline"

    # Define test batches for non-state directories
    batches = [
        (f"{baseline}/gov/irs", "IRS tests"),
        (f"{baseline}/gov/usda", "USDA tests"),
        (f"{baseline}/gov/hhs", "HHS tests"),
        (f"{baseline}/gov/local", "Local tests"),
        (f"{baseline}/gov/ssa", "SSA tests"),
        (f"{baseline}/gov/aca", "ACA tests"),
        (f"{baseline}/gov/hud", "HUD tests"),
        (f"{baseline}/gov/territories", "Territories tests"),
        (f"{baseline}/gov/ed", "Education tests"),
        (f"{baseline}/gov/doe", "DOE tests"),
        (f"{baseline}/gov/fcc", "FCC tests"),
        (f"{baseline}/household", "Household tests"),
    ]

    python_exe = "/opt/miniconda3/envs/policyengine/bin/python"
    if not os.path.exists(python_exe):
        python_exe = sys.executable

    results = []
    for test_path, description in batches:
        path = Path(test_path)
        if not path.exists():
            continue

        if path.is_file():
            test_files = [str(path)]
        else:
            test_files = [str(f) for f in path.rglob("*.yaml")]

        if not test_files:
            continue

        print(f"\nTesting {description} ({len(test_files)} files)...")

        cmd = [
            python_exe,
            "-m",
            "policyengine_core.scripts.policyengine_command",
            "test",
            *test_files,
            "-c",
            "policyengine_us",
        ]

        start = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        elapsed = time.time() - start

        success = result.returncode == 0
        print(f"  {'✅' if success else '❌'} {description}: {elapsed:.1f}s")

        results.append(
            {
                "batch": description,
                "files": len(test_files),
                "success": success,
                "time": elapsed,
            }
        )

        # Cleanup
        gc.collect()

    return results


def main():
    """Main function to run all baseline tests with states together."""
    print("=" * 60)
    print("BASELINE TEST RUNNER - ALL STATES TOGETHER")
    print("=" * 60)
    print("This approach tests all states in one batch for speed.")
    print("Use individual state testing if memory is limited.")
    print("-" * 60)

    overall_start = time.time()

    # Step 1: Run all states together
    print("\n📍 STEP 1: Testing all states together")
    print("=" * 60)
    states_success, states_time, states_count = run_all_states_together()

    # Step 2: Run other baseline tests
    print("\n📍 STEP 2: Testing other baseline directories")
    print("=" * 60)
    other_results = run_other_baseline_tests()

    # Summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)

    total_time = time.time() - overall_start
    print(f"Total execution time: {total_time/60:.1f} minutes")
    print(
        f"\nStates: {states_count} tests - {'✅ PASSED' if states_success else '❌ FAILED'} ({states_time/60:.1f} min)"
    )

    for result in other_results:
        status = "✅" if result["success"] else "❌"
        print(
            f"{result['batch']}: {result['files']} tests - {status} ({result['time']:.1f}s)"
        )

    all_passed = states_success and all(r["success"] for r in other_results)

    print(
        f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}"
    )

    # Save results
    with open("baseline_test_results_all_states.json", "w") as f:
        json.dump(
            {
                "states": {
                    "count": states_count,
                    "success": states_success,
                    "time": states_time,
                },
                "other": other_results,
                "total_time": total_time,
                "all_passed": all_passed,
            },
            f,
            indent=2,
        )

    print("\nResults saved to baseline_test_results_all_states.json")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
