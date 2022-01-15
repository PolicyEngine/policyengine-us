"""This file contains your country package's metadata and dependencies."""

from setuptools import find_packages, setup

setup(
    name="OpenFisca-US",
    version="0.23.0",
    author="Nikhil Woodruff",
    author_email="nikhil@policyengine.org",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
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
        "OpenFisca-Core[web-api] >= 35.0.0",
        "openfisca_us_data >= 0.1.2",
        "microdf_python",
        "pandas",
        "tqdm",
        "requests",
        "OpenFisca-Tools>=0.1.9",
        "pyyaml",
    ],
    extras_require={
        "dev": [
            "autopep8 >= 1.5.4, < 2.0.0",
            "black",
            "wheel",
            "pytest",
            "setuptools",
            "jupyter-book",
            "coverage",
        ],
    },
    python_requires=">=3.7,<3.8",
    entry_points={},
    packages=find_packages(),
)
