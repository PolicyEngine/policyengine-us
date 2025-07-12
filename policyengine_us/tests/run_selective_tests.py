#!/usr/bin/env python3
"""
Selective test runner for PolicyEngine US.
Runs only tests relevant to changed files to reduce test execution time.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Set, List, Dict
import json
import argparse


class SelectiveTestRunner:
    def __init__(self, base_branch: str = "main"):
        self.base_branch = base_branch
        self.repo_root = Path.cwd()

        # Define mappings between source directories and test directories
        self.test_mappings = {
            # State-specific mappings
            "policyengine_us/parameters/gov/states": "policyengine_us/tests/policy/baseline/gov/states",
            "policyengine_us/variables/gov/states": "policyengine_us/tests/policy/baseline/gov/states",
            "policyengine_us/reforms/states": "policyengine_us/tests/policy/contrib/states",
            # Federal mappings
            "policyengine_us/parameters/gov/irs": "policyengine_us/tests/policy/baseline/gov/irs",
            "policyengine_us/variables/gov/irs": "policyengine_us/tests/policy/baseline/gov/irs",
            # Benefits programs
            "policyengine_us/parameters/gov/usda/snap": "policyengine_us/tests/policy/baseline/gov/usda/snap",
            "policyengine_us/variables/gov/usda/snap": "policyengine_us/tests/policy/baseline/gov/usda/snap",
            "policyengine_us/parameters/gov/hhs": "policyengine_us/tests/policy/baseline/gov/hhs",
            "policyengine_us/variables/gov/hhs": "policyengine_us/tests/policy/baseline/gov/hhs",
            # Local government
            "policyengine_us/parameters/gov/local": "policyengine_us/tests/policy/baseline/gov/local",
            "policyengine_us/variables/gov/local": "policyengine_us/tests/policy/baseline/gov/local",
            # Contributions/reforms
            "policyengine_us/parameters/contrib": "policyengine_us/tests/policy/contrib",
            "policyengine_us/reforms": "policyengine_us/tests/policy/reform",
            # Core functionality
            "policyengine_us/variables/household": "policyengine_us/tests/policy/baseline/household",
            "policyengine_us/system.py": "policyengine_us/tests",
            "policyengine_us/entities.py": "policyengine_us/tests",
        }

        # Define test categories that should always run
        self.core_tests = [
            "policyengine_us/tests/code_health",
            "policyengine_us/tests/test_variables.py",
        ]

        # State abbreviations for more granular state testing
        self.state_abbrevs = [
            "al",
            "ak",
            "az",
            "ar",
            "ca",
            "co",
            "ct",
            "de",
            "dc",
            "fl",
            "ga",
            "hi",
            "id",
            "il",
            "in",
            "ia",
            "ks",
            "ky",
            "la",
            "me",
            "md",
            "ma",
            "mi",
            "mn",
            "ms",
            "mo",
            "mt",
            "ne",
            "nv",
            "nh",
            "nj",
            "nm",
            "ny",
            "nc",
            "nd",
            "oh",
            "ok",
            "or",
            "pa",
            "ri",
            "sc",
            "sd",
            "tn",
            "tx",
            "ut",
            "vt",
            "va",
            "wa",
            "wv",
            "wi",
            "wy",
        ]

    def get_changed_files(self) -> Set[str]:
        """Get list of changed files compared to base branch."""
        try:
            # Check if we're in a git repository
            git_dir_result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                text=True,
            )

            if git_dir_result.returncode != 0:
                print(
                    f"Error: Not in a git repository. Error: {git_dir_result.stderr}"
                )
                return set()

            # Try to fetch the base branch (but don't fail if offline)
            fetch_result = subprocess.run(
                ["git", "fetch", "origin", self.base_branch],
                capture_output=True,
                text=True,
            )

            if fetch_result.returncode != 0:
                print(
                    f"Warning: Could not fetch from origin (working offline?)"
                )

            # Try different methods to get changed files
            changed_files = set()

            # Method 1: Compare with origin/base_branch
            result = subprocess.run(
                [
                    "git",
                    "diff",
                    f"origin/{self.base_branch}...HEAD",
                    "--name-only",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                files = result.stdout.strip().split("\n")
                changed_files.update(f for f in files if f)
            else:
                print(f"Could not diff against origin/{self.base_branch}")

                # Method 2: Try without origin/ prefix (local branch)
                result = subprocess.run(
                    [
                        "git",
                        "diff",
                        f"{self.base_branch}...HEAD",
                        "--name-only",
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    files = result.stdout.strip().split("\n")
                    changed_files.update(f for f in files if f)
                else:
                    # Method 3: Get uncommitted changes
                    print("Falling back to uncommitted changes...")

                    # Staged changes
                    result = subprocess.run(
                        ["git", "diff", "--cached", "--name-only"],
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0:
                        files = result.stdout.strip().split("\n")
                        changed_files.update(f for f in files if f)

                    # Unstaged changes
                    result = subprocess.run(
                        ["git", "diff", "--name-only"],
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0:
                        files = result.stdout.strip().split("\n")
                        changed_files.update(f for f in files if f)

                    # Untracked files
                    result = subprocess.run(
                        ["git", "ls-files", "--others", "--exclude-standard"],
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0:
                        files = result.stdout.strip().split("\n")
                        # Only include Python and YAML files
                        changed_files.update(
                            f
                            for f in files
                            if f
                            and (
                                f.endswith(".py")
                                or f.endswith(".yaml")
                                or f.endswith(".yml")
                            )
                        )

            return changed_files

        except subprocess.CalledProcessError as e:
            print(f"Error running git command: {e}")
            print(f"Command: {e.cmd}")
            print(f"Output: {e.output if hasattr(e, 'output') else 'N/A'}")
            return set()
        except Exception as e:
            print(f"Unexpected error: {e}")
            return set()

    def get_affected_states(self, changed_files: Set[str]) -> Set[str]:
        """Extract affected state abbreviations from changed files."""
        affected_states = set()

        for file in changed_files:
            # Check state directories
            for state in self.state_abbrevs:
                if f"/states/{state}/" in file or f"/states/{state}." in file:
                    affected_states.add(state)
                # Also check for state-specific local directories
                if f"/local/{state}/" in file:
                    affected_states.add(state)

        return affected_states

    def map_files_to_tests(self, changed_files: Set[str]) -> Set[str]:
        """Map changed files to relevant test paths."""
        test_paths = set()
        affected_states = self.get_affected_states(changed_files)

        for file in changed_files:
            # Skip non-Python and non-YAML files unless they're critical
            if not (
                file.endswith(".py")
                or file.endswith(".yaml")
                or file.endswith(".yml")
            ):
                if not any(
                    critical in file
                    for critical in ["setup.py", "requirements", "Makefile"]
                ):
                    continue

            # Check each mapping rule
            mapped = False
            for source_pattern, test_pattern in self.test_mappings.items():
                if source_pattern in file:
                    test_paths.add(test_pattern)
                    mapped = True

                    # If this is a state-specific change, add more specific test path
                    if "states" in source_pattern and affected_states:
                        for state in affected_states:
                            state_test_path = f"{test_pattern}/{state}"
                            test_paths.add(state_test_path)

            # Special cases
            if not mapped:
                # Reform files
                if "reforms" in file and file.endswith(".py"):
                    test_paths.add("policyengine_us/tests/policy/reform")
                    # Also test baseline if reform affects specific component
                    if "/ctc/" in file:
                        test_paths.add(
                            "policyengine_us/tests/policy/baseline/gov/irs/credits/ctc"
                        )
                    elif "/eitc/" in file:
                        test_paths.add(
                            "policyengine_us/tests/policy/baseline/gov/irs/credits/earned_income"
                        )

                # Variable files not caught by mappings
                elif "variables" in file and file.endswith(".py"):
                    # Try to infer test location from variable path
                    variable_path = file.replace(
                        "policyengine_us/variables/", ""
                    )
                    test_path = f"policyengine_us/tests/policy/baseline/{variable_path.rsplit('/', 1)[0]}"
                    test_paths.add(test_path)

                # Parameter files not caught by mappings
                elif "parameters" in file and file.endswith(".yaml"):
                    param_path = file.replace(
                        "policyengine_us/parameters/", ""
                    )
                    test_path = f"policyengine_us/tests/policy/baseline/{param_path.rsplit('/', 1)[0]}"
                    test_paths.add(test_path)

                # Changes to test files themselves
                elif "tests" in file:
                    test_paths.add(file.rsplit("/", 1)[0])

        # Always include core tests
        test_paths.update(self.core_tests)

        # Filter out non-existent paths
        existing_test_paths = set()
        for path in test_paths:
            if Path(path).exists():
                existing_test_paths.add(path)
            else:
                # Try without the full path prefix
                simplified_path = path.replace(
                    "policyengine_us/tests/policy/baseline/", ""
                )
                if Path(
                    f"policyengine_us/tests/policy/baseline/{simplified_path}"
                ).exists():
                    existing_test_paths.add(
                        f"policyengine_us/tests/policy/baseline/{simplified_path}"
                    )

        return existing_test_paths

    def run_tests(self, test_paths: Set[str], verbose: bool = False) -> int:
        """Run pytest on specified test paths."""
        if not test_paths:
            print("No relevant tests found for changed files.")
            return 0

        print(f"Running tests for {len(test_paths)} test locations:")
        for path in sorted(test_paths):
            print(f"  - {path}")

        # Construct pytest command
        pytest_args = ["pytest"]

        if verbose:
            pytest_args.append("-v")
        else:
            pytest_args.append("-q")

        # Add test paths
        pytest_args.extend(sorted(test_paths))

        # Add any additional pytest arguments
        pytest_args.extend(
            [
                "--tb=short",  # Shorter traceback format
                "-x",  # Stop on first failure
                "--disable-warnings",  # Reduce output noise
            ]
        )

        print(f"\nRunning command: {' '.join(pytest_args)}")

        # Run pytest
        result = subprocess.run(pytest_args)

        return result.returncode

    def run_all_tests(self) -> int:
        """Run all tests (fallback option)."""
        print("Running all tests...")
        result = subprocess.run(["pytest", "policyengine_us/tests"])
        return result.returncode

    def generate_test_plan(
        self, changed_files: Set[str]
    ) -> Dict[str, List[str]]:
        """Generate a detailed test plan showing which tests will run for which files."""
        test_plan = {}

        for file in changed_files:
            if not (
                file.endswith(".py")
                or file.endswith(".yaml")
                or file.endswith(".yml")
            ):
                continue

            file_tests = []

            # Check each mapping
            for source_pattern, test_pattern in self.test_mappings.items():
                if source_pattern in file:
                    file_tests.append(test_pattern)

            # Add special case tests
            if "reforms" in file and file.endswith(".py"):
                file_tests.append("policyengine_us/tests/policy/reform")

            if file_tests:
                test_plan[file] = file_tests

        return test_plan


def main():
    parser = argparse.ArgumentParser(
        description="Run only relevant tests based on changed files"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all tests regardless of changes",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )
    parser.add_argument(
        "--base-branch",
        default="master",
        help="Base branch to compare against (default: main)",
    )
    parser.add_argument(
        "--plan",
        action="store_true",
        help="Show test plan without running tests",
    )
    parser.add_argument(
        "--files",
        nargs="+",
        help="Manually specify changed files instead of using git diff",
    )
    parser.add_argument(
        "--uncommitted",
        action="store_true",
        help="Test only uncommitted changes (staged and unstaged)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show debug information about git state",
    )

    args = parser.parse_args()

    runner = SelectiveTestRunner(base_branch=args.base_branch)

    # Debug mode - show git status
    if args.debug:
        print("Git repository information:")
        subprocess.run(["git", "status"])
        print("\nCurrent branch:")
        result = subprocess.run(
            ["git", "branch", "--show-current"], capture_output=True, text=True
        )
        print(result.stdout.strip())
        print("\nBase branch exists?")
        result = subprocess.run(
            ["git", "rev-parse", "--verify", f"origin/{args.base_branch}"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"  origin/{args.base_branch}: exists")
        else:
            print(f"  origin/{args.base_branch}: NOT FOUND")
            # Check for master
            result = subprocess.run(
                ["git", "rev-parse", "--verify", "origin/master"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print(f"  origin/master: exists (use --base-branch master)")
        print()

    if args.all:
        sys.exit(runner.run_all_tests())

    # Get changed files
    if args.files:
        changed_files = set(args.files)
    else:
        # Check if we should override the comparison method
        if args.uncommitted:
            # Get only uncommitted changes
            changed_files = set()

            # Staged changes
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                files = result.stdout.strip().split("\n")
                changed_files.update(f for f in files if f)

            # Unstaged changes
            result = subprocess.run(
                ["git", "diff", "--name-only"], capture_output=True, text=True
            )
            if result.returncode == 0:
                files = result.stdout.strip().split("\n")
                changed_files.update(f for f in files if f)

            print(f"Testing uncommitted changes only...")
        else:
            changed_files = runner.get_changed_files()

    if not changed_files:
        print("No changed files detected.")
        print("\nTry one of these options:")
        print("  --uncommitted    Test only uncommitted changes")
        print("  --all            Run all tests")
        print("  --debug          Show git repository information")
        print("  --files FILE...  Manually specify files to test")
        sys.exit(0)

    print(f"Detected {len(changed_files)} changed files:")
    for file in sorted(changed_files):
        print(f"  - {file}")

    if args.plan:
        # Show test plan
        test_plan = runner.generate_test_plan(changed_files)
        print("\nTest execution plan:")
        for file, tests in test_plan.items():
            print(f"\n{file}:")
            for test in tests:
                print(f"  → {test}")
        sys.exit(0)

    # Map to test paths and run tests
    test_paths = runner.map_files_to_tests(changed_files)

    if not test_paths:
        print("\nNo relevant tests found for changed files.")
        print("Consider running all tests with --all flag.")
        sys.exit(0)

    sys.exit(runner.run_tests(test_paths, verbose=args.verbose))


if __name__ == "__main__":
    main()
