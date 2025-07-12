import argparse
import os


def main():
    # First, find the current package version number from the pyproject.toml file
    with open("pyproject.toml", "r") as f:
        setup = f.read()
    version = setup.split("version = ")[1].split(",")[0].strip('"')
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
        f"git clone https://nikhilwodruff:{pat}@github.com/policyengine/policyengine-household-api"
    )

    os.system(
        f"cd policyengine-household-api && python gcp/bump_country_package.py --country policyengine-us --version {version}"
    )


if __name__ == "__main__":
    main()
