"""This file contains your country package's metadata and dependencies."""

from setuptools import find_packages, setup

setup(
    name="OpenFisca-US",
    version="0.109.0",
    author="PolicyEngine",
    author_email="hello@policyengine.org",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    description="OpenFisca tax and benefit system for the US",
    keywords="benefit microsimulation social tax",
    license="http://www.fsf.org/licensing/licenses/agpl-3.0.html",
    url="https://github.com/PolicyEngine/openfisca-us",
    include_package_data=True,  # Will read MANIFEST.in
    data_files=[
        (
            "share/openfisca/openfisca-country-template",
            ["CHANGELOG.md", "LICENSE", "README.md"],
        ),
    ],
    install_requires=[
        "h5py",
        "microdf_python",
        "OpenFisca-Core[web-api] >= 35.0.0",
        "OpenFisca-Tools>=0.12.0,<1.0.0",
        "pandas",
        "pathlib",
        "pytest",
        "pytest-dependency",
        "pyyaml",
        "requests",
        "synthimpute",
        "tables",
        "tqdm",
        "click>=8.0.0",
    ],
    extras_require={
        "dev": [
            "autopep8 >= 1.5.4, < 2.0.0",
            "black",
            "coverage",
            "jupyter-book",
            "plotly",
            "pytest",
            "setuptools",
            "wheel",
            "yaml-changelog>=0.1.7",
            "linecheck",
        ],
    },
    python_requires=">=3.7,<3.8",
    entry_points={
        "console_scripts": [
            "openfisca-us = openfisca_us.tools.cli:main",
            "openfisca-us-data = openfisca_us.data.cli:cli",
        ],
    },
    packages=find_packages(),
)
