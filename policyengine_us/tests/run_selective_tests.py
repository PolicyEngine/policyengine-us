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
import re
import argparse


class SelectiveTestRunner:
    def __init__(self, base_branch: str = "master"):
        self.base_branch = base_branch
        self.repo_root = Path.cwd()

        # Define regex patterns for matching files to tests
        self.test_patterns = [
            # Rule 1: Match gov folders (excluding states) to their test directories
            {
                "file_pattern": r"policyengine_us/(parameters|variables)/gov/(?!states/)([^/]+)",
                "test_pattern": r"policyengine_us/tests/policy/baseline/gov/\2",
            },
            # Rule 2: Match state-specific changes to state tests
            {
                "file_pattern": r"policyengine_us/(parameters|variables)/gov/states/([^/]+)",
                "test_pattern": r"policyengine_us/tests/policy/baseline/gov/states/\2",
            },
            # Also match state changes in local directories
            {
                "file_pattern": r"policyengine_us/(parameters|variables)/gov/local/([^/]+)",
                "test_pattern": r"policyengine_us/tests/policy/baseline/gov/local/\2",
            },
            # Match reforms to reform tests
            {
                "file_pattern": r"policyengine_us/reforms/",
                "test_pattern": r"policyengine_us/tests/policy/reform",
            },
            # Match contrib parameters to contrib tests
            {
                "file_pattern": r"policyengine_us/parameters/contrib/",
                "test_pattern": r"policyengine_us/tests/policy/contrib",
            },
            # Match household variables to household tests
            {
                "file_pattern": r"policyengine_us/variables/household/",
                "test_pattern": r"policyengine_us/tests/policy/baseline/household",
            },
            # Match reforms in specific states
            {
                "file_pattern": r"policyengine_us/reforms/states/([^/]+)",
                "test_pattern": r"policyengine_us/tests/policy/contrib/states/\1",
            },
        ]

        # Additional patterns for specific components within gov
        self.component_patterns = [
            # IRS components
            {
                "file_pattern": r"gov/irs/credits/ctc",
                "test_pattern": r"policyengine_us/tests/policy/baseline/gov/irs/credits/ctc",
            },
            {
                "file_pattern": r"gov/irs/credits/earned_income",
                "test_pattern": r"policyengine_us/tests/policy/baseline/gov/irs/credits/earned_income",
            },
            # USDA components
            {
                "file_pattern": r"gov/usda/snap",
                "test_pattern": r"policyengine_us/tests/policy/baseline/gov/usda/snap",
            },
            {
                "file_pattern": r"gov/usda/wic",
                "test_pattern": r"policyengine_us/tests/policy/baseline/gov/usda/wic",
            },
            # HHS components
            {
                "file_pattern": r"gov/hhs/medicaid",
                "test_pattern": r"policyengine_us/tests/policy/baseline/gov/hhs/medicaid",
            },
            {
                "file_pattern": r"gov/hhs/tanf",
                "test_pattern": r"policyengine_us/tests/policy/baseline/gov/hhs/tanf",
            },
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

            # Check if we're in GitHub Actions
            github_event_name = os.environ.get("GITHUB_EVENT_NAME")
            github_base_ref = os.environ.get("GITHUB_BASE_REF")

            if github_event_name == "pull_request" and github_base_ref:
                # We're in a GitHub Actions PR build
                print(
                    f"Detected GitHub Actions PR build against {github_base_ref}"
                )

                # GitHub Actions already has the base branch fetched
                result = subprocess.run(
                    [
                        "git",
                        "diff",
                        f"origin/{github_base_ref}...HEAD",
                        "--name-only",
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    files = result.stdout.strip().split("\n")
                    changed_files = set(f for f in files if f)
                    return changed_files
                else:
                    print(
                        f"Failed to diff against origin/{github_base_ref}: {result.stderr}"
                    )

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
                    if result.returncode == 0 and result.stdout.strip():
                        files = result.stdout.strip().split("\n")
                        staged = [f for f in files if f]
                        changed_files.update(staged)
                        if staged:
                            print(f"  Found {len(staged)} staged changes")

                    # Unstaged changes
                    result = subprocess.run(
                        ["git", "diff", "--name-only"],
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        files = result.stdout.strip().split("\n")
                        unstaged = [f for f in files if f]
                        changed_files.update(unstaged)
                        if unstaged:
                            print(f"  Found {len(unstaged)} unstaged changes")

                    # Untracked files
                    result = subprocess.run(
                        ["git", "ls-files", "--others", "--exclude-standard"],
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        files = result.stdout.strip().split("\n")
                        # Only include Python and YAML files
                        untracked = [
                            f
                            for f in files
                            if f
                            and (
                                f.endswith(".py")
                                or f.endswith(".yaml")
                                or f.endswith(".yml")
                            )
                        ]
                        changed_files.update(untracked)
                        if untracked:
                            print(
                                f"  Found {len(untracked)} untracked Python/YAML files"
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

    def map_files_to_tests(self, changed_files: Set[str]) -> Set[str]:
        """Map changed files to relevant test paths using regex patterns."""
        test_paths = set()

        for file in changed_files:
            # Skip non-Python and non-YAML files unless they're critical
            if not (
                file.endswith(".py")
                or file.endswith(".yaml")
                or file.endswith(".yml")
            ):
                if not any(
                    critical in file
                    for critical in [
                        "pyproject.toml",
                        "requirements",
                        "Makefile",
                    ]
                ):
                    continue

            # Check against regex patterns
            for pattern in self.test_patterns:
                match = re.search(pattern["file_pattern"], file)
                if match:
                    # Substitute captured groups into test pattern
                    test_path = re.sub(
                        pattern["file_pattern"], pattern["test_pattern"], file
                    )
                    # Extract just the matched portion
                    test_path = match.expand(pattern["test_pattern"])
                    test_paths.add(test_path)

                    # Also check for more specific component patterns
                    for comp_pattern in self.component_patterns:
                        if re.search(comp_pattern["file_pattern"], file):
                            test_paths.add(comp_pattern["test_pattern"])

            # Special handling for test files themselves
            if "tests" in file and file.endswith(".py"):
                # Add the directory containing the test file
                test_dir = os.path.dirname(file)
                if test_dir:
                    test_paths.add(test_dir)

        # Filter out non-existent paths and return
        existing_test_paths = set()
        for path in test_paths:
            if Path(path).exists():
                existing_test_paths.add(path)
            else:
                # Try to find the closest existing parent directory
                path_obj = Path(path)
                while path_obj.parent != path_obj:
                    if path_obj.exists() and path_obj.is_dir():
                        # Check if this directory contains test files
                        if any(path_obj.glob("**/test_*.py")) or any(
                            path_obj.glob("**/*_test.py")
                        ):
                            existing_test_paths.add(str(path_obj))
                            break
                    path_obj = path_obj.parent

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
        pytest_args = ["policyengine-core", "test", "-c", "policyengine_us"]

        # Add test paths
        pytest_args.extend(sorted(test_paths))

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

            # Check against regex patterns
            for pattern in self.test_patterns:
                match = re.search(pattern["file_pattern"], file)
                if match:
                    test_path = match.expand(pattern["test_pattern"])
                    file_tests.append(test_path)

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
        help="Base branch to compare against (default: master)",
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
