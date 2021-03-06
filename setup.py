from setuptools import setup, find_packages
from pathlib import Path

setup(
    name="PolicyEngine-US",
    version="0.1.0",
    author="PolicyEngine",
    license="http://www.fsf.org/licensing/licenses/agpl-3.0.html",
    url="https://github.com/policyengine/policyengine-us",
    install_requires=[
        "plotly",
        "flask",
        "flask_cors",
        "rdbl",
        "kaleido",
        "google-cloud-storage>=1.42.0",
        "gunicorn",
    ],
    packages=find_packages(),
)
