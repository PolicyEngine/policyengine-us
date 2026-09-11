# PolicyEngine US

[![codecov](https://codecov.io/gh/PolicyEngine/policyengine-us/branch/main/graph/badge.svg?token=BLoCjCf5Qr)](https://codecov.io/gh/PolicyEngine/policyengine-us)
[![PyPI version](https://badge.fury.io/py/policyengine-us.svg)](https://badge.fury.io/py/policyengine-us)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

> **For microsimulation, use [policyengine.py](https://github.com/PolicyEngine/policyengine.py).** Society-wide microsimulation — population aggregates and distributional or budgetary impacts — is moving to the managed `policyengine.py` bundle, which pins certified, calibration-gated datasets. **Direct microsimulation via `policyengine-us` (`Microsimulation()`) is deprecated** and being migrated to `policyengine.py`. This package remains the home of the US tax-benefit rules and household-level calculations. Microsimulation results are estimates — inspect dataset calibration at https://calibration-diagnostics.vercel.app/populace.


PolicyEngine US is a microsimulation model of the US state and federal tax and benefit system.

PolicyEngine US supports Python 3.11 through 3.14 and requires pandas 3 or
later. To install, run `pip install policyengine-us`.

This release pins `spm-calculator==0.3.1` to preserve its SPM threshold API.
Previously published country versions retain their original dependency metadata;
when reproducing one of those versions, include the compatible calculator
explicitly, for example:

```bash
uv pip install "policyengine-us==1.824.7" "spm-calculator==0.3.1"
```

To install PolicyEngine US as part of a certified PolicyEngine bundle, use the
bundle installer published by `policyengine`, for example:

```bash
uvx --from policyengine policyengine bundle install --country us --venv .venv
```
