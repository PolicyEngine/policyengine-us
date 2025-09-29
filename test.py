#!/usr/bin/env python3
"""
Script to fetch all PRs to master branch for policyengine/policyengine-us
and pull the latest master branch.
"""

import subprocess
import sys
import json
from urllib.request import urlopen, Request
from urllib.error import HTTPError


def get_all_prs_to_master(
    owner="policyengine", repo="policyengine-us", branch="master"
):
    """Fetch all PRs (open and closed) targeting the master branch."""
    prs = []
    page = 1
    per_page = 100

    print(f"Fetching PRs for {owner}/{repo} targeting {branch} branch...")
    i = 0
    while i < 2:
        i += 1
        # GitHub API endpoint for PRs
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        params = f"?state=all&base={branch}&per_page={per_page}&page={page}"

        try:
            # Create request with headers
            req = Request(url + params)
            req.add_header("Accept", "application/vnd.github.v3+json")
            # Add User-Agent header to avoid rate limiting
            req.add_header("User-Agent", "PR-Fetcher-Script")

            # If you have a GitHub token, uncomment and add it here:
            # req.add_header('Authorization', 'token YOUR_GITHUB_TOKEN')

            response = urlopen(req)
            data = json.loads(response.read().decode())

            if not data:
                break

            prs.extend(data)
            print(f"  Fetched page {page} ({len(data)} PRs)")
            page += 1

        except HTTPError as e:
            print(f"Error fetching PRs: {e}")
            print(
                "Note: GitHub API has rate limits. Consider using a personal access token."
            )
            break

    return prs


def pull_latest_master():
    """Pull the latest master branch from origin."""
    print("\nPulling latest master branch...")

    try:
        # Ensure we're on master branch
        subprocess.run(
            ["git", "checkout", "master"],
            check=True,
            capture_output=True,
            text=True,
        )

        # Pull latest changes
        result = subprocess.run(
            ["git", "pull", "origin", "master"],
            check=True,
            capture_output=True,
            text=True,
        )
        print("Successfully pulled latest master:")
        print(result.stdout)

    except subprocess.CalledProcessError as e:
        print(f"Error pulling master: {e}")
        print(f"Error output: {e.stderr}")
        return False

    return True


def display_pr_summary(prs):
    """Display a summary of the PRs."""
    print(f"\nTotal PRs to master: {len(prs)}")

    open_prs = [pr for pr in prs if pr["state"] == "open"]
    closed_prs = [pr for pr in prs if pr["state"] == "closed"]
    merged_prs = [pr for pr in closed_prs if pr.get("merged_at")]

    print(f"  Open PRs: {len(open_prs)}")
    print(f"  Closed PRs: {len(closed_prs)}")
    print(f"  Merged PRs: {len(merged_prs)}")

    # Show recent PRs
    print("\nMost recent 10 PRs:")
    for pr in prs[:10]:
        state = pr["state"]
        if state == "closed" and pr.get("merged_at"):
            state = "merged"
        print(f"  #{pr['number']}: {pr['title']} [{state}]")
        print(f"    Author: {pr['user']['login']}")
        print(f"    Created: {pr['created_at']}")
        print()


def save_pr_data(prs, filename="policyengine_prs.json"):
    """Save PR data to a JSON file."""
    with open(filename, "w") as f:
        json.dump(prs, f, indent=2)
    print(f"\nPR data saved to {filename}")


def main():
    # Check if we're in a git repository
    try:
        subprocess.run(["git", "status"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("Error: Not in a git repository!")
        print(
            "Please run this script from within the policyengine-us repository."
        )
        sys.exit(1)

    # Fetch all PRs
    prs = get_all_prs_to_master()

    if prs:
        # Display summary
        display_pr_summary(prs)

        # Save PR data
        save_pr_data(prs)

        # Pull latest master
        print("\n" + "=" * 50)
        pull_latest_master()
    else:
        print("No PRs found or unable to fetch PRs.")


if __name__ == "__main__":
    main()
