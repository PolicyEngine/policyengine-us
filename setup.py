"""This file contains your country package's metadata and dependencies."""

from setuptools import find_packages, setup

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

setup(
    name="policyengine-us",
    version="1.144.0",
    author="PolicyEngine",
    author_email="hello@policyengine.org",
    long_description=readme,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    description="PolicyEngine tax and benefit system for the US",
    keywords="benefit microsimulation social tax",
    license="http://www.fsf.org/licensing/licenses/agpl-3.0.html",
    url="https://github.com/PolicyEngine/policyengine-us",
    include_package_data=True,  # Will read MANIFEST.in
    data_files=[
        (
            "share/openfisca/openfisca-country-template",
            ["CHANGELOG.md", "LICENSE", "README.md"],
        ),
    ],
    install_requires=[
        "policyengine-core>=3.10.0",
        "policyengine-us-data==1.11.1",
        "microdf-python>=0.4.3",
        "tqdm",
    ],
    extras_require={
        "dev": [
            "setuptools",
            "jupyter-book",
            "furo",
            "coverage",
        ],
    },
    python_requires=">=3.10,<3.13",
    entry_points={
        "console_scripts": [
            "policyengine-us = policyengine_us.tools.cli:main",
        ],
    },
    packages=find_packages(),
)
