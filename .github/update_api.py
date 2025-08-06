import argparse
import tomllib
import os


def main():
    # First, find the current package version number from the pyproject.toml file
    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)
        version = data["project"]["version"]  # Would give us "1.358.0"
    # Then, clone the https://github.com/policyengine/policyengine-api repo using the GitHub CLI
    pat = os.environ["GITHUB_TOKEN"]
    os.system(
        f"git clone https://nikhilwoodruff:{pat}@github.com/policyengine/policyengine-api"
    )
    # Then, cd inside and run gcp/bump_country_package.py --country policyengine-uk --version {version}
    os.system(
        f"cd policyengine-api && python gcp/bump_country_package.py --country policyengine-us --version {version}"
    )

    # Repeat the above for https://github.com/policyengine/policyengine-household-api
    os.system(
        f"git clone https://nikhilwoodruff:{pat}@github.com/policyengine/policyengine-household-api"
    )

    os.system(
        f"cd policyengine-household-api && python gcp/bump_country_package.py --country policyengine-us --version {version}"
    )


if __name__ == "__main__":
    main()
