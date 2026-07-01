# PolicyEngine US

[![codecov](https://codecov.io/gh/PolicyEngine/policyengine-us/branch/master/graph/badge.svg?token=BLoCjCf5Qr)](https://codecov.io/gh/PolicyEngine/policyengine-us)
[![PyPI version](https://badge.fury.io/py/policyengine-us.svg)](https://badge.fury.io/py/policyengine-us)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **For microsimulation, use [policyengine.py](https://github.com/PolicyEngine/policyengine.py).** Society-wide microsimulation — population aggregates and distributional or budgetary impacts — is moving to the managed `policyengine.py` bundle, which pins certified, calibration-gated datasets. **Direct microsimulation via `policyengine-us` (`Microsimulation()`) is deprecated** and being migrated to `policyengine.py`. This package remains the home of the US tax-benefit rules and household-level calculations. Microsimulation results are estimates — inspect dataset calibration at https://calibration-diagnostics.vercel.app/populace.


PolicyEngine US is a microsimulation model of the US state and federal tax and benefit system.

To install, run `pip install policyengine-us`.

To install PolicyEngine US as part of a certified PolicyEngine bundle, use the
bundle installer published by `policyengine`, for example:

```bash
uvx --from policyengine policyengine bundle install --country us --venv .venv
```
