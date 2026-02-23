# PolicyEngine US

[![codecov](https://codecov.io/gh/PolicyEngine/policyengine-us/branch/master/graph/badge.svg?token=BLoCjCf5Qr)](https://codecov.io/gh/PolicyEngine/policyengine-us)
[![PyPI version](https://badge.fury.io/py/policyengine-us.svg)](https://badge.fury.io/py/policyengine-us)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

PolicyEngine US is a microsimulation model of the US state and federal tax and benefit system.

To install, run `pip install policyengine-us`.

## System requirements

PolicyEngine-US loads the full US tax-benefit system on import, which requires significant memory. Based on [empirical testing](https://gist.github.com/MaxGhenis/253efeb07f4bfa8b50af768accf73c9d):

| Use case | RAM (minimum) | RAM (recommended) | Typical usage |
| --- | --- | --- | --- |
| Household calculations | 8 GB | 16 GB | ~500 MB |
| Microsimulation (CPS data) | 16 GB | 24-32 GB | 2-4 GB |

Key details:
- Importing the package loads the tax-benefit system, using ~400 MB
- Memory scales linearly with multiple simultaneous simulations
- CPS dataset operations may spike memory during calculations
