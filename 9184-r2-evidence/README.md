Round-2 validation evidence for PolicyEngine US PR #9184.

The affected formula/parameter was unchanged from `b24094b166` when each before-fix regression ran. The new default-true determination input schema was registered solely to accept the new continuing-resource input; the old resource formula ignored it. Initial/default controls and passing equity controls stayed green.

Before-fix results: equity 2 failed/14 passed; resources 2 failed/21 passed; income 1 failed/13 passed; MMMNA 2 failed/7 passed. These seven failures preserve the defects described in review-r1.

All tests ran one file at a time, with no concurrent test processes or national microsimulation. The first before-equity run used `policyengine-core test <single YAML file> -c policyengine_us`. Other YAML runs used the same Core runner with the country's initialized system, avoiding the CLI's additional model construction:

```python
from policyengine_us.system import system
from policyengine_core.tools.test_runner import run_tests

raise SystemExit(run_tests(system, [single_file_path]))
```

The invariant file used `python -m pytest policyengine_us/tests/core/test_medicaid_ltss_financial_invariants.py -q` in a separate process. The existing assertions and 18-test count are preserved; its independent applicants now have explicit singleton marital units.

Environment: Python 3.13.9, policyengine-core 3.32.20, NumPy 2.5.3, pandas 3.0.6, pytest 9.1.1, ruff 0.16.10. The prior job's virtual environment was executed read-only, with `PYTHONDONTWRITEBYTECODE=1` and `PYTHONPATH` set to this workspace. Imports were confirmed to resolve to this workspace.

`make format` ran before every commit, using `UV_NO_SYNC=1`, `UV_PYTHON=3.13`, that existing environment and a workspace-local UV cache. Format logs include the accompanying lint checks.

The after-equity test itself passed all 16 cases. Its optional `/usr/bin/time -l` wrapper returned 1 after the successful test because sandbox permissions denied `sysctl kern.clockrate`; the log records 137.43 seconds wall time, but peak-memory reporting is unavailable. This instrumentation failure does not indicate a test failure. Remaining validation runs omit that wrapper.

The dependency audit finds zero existing variable consumers of the 28 new financial screen/input variables. The completed hub microsimulation at merge base `6b80a8e447` versus `b24094b166` found exactly zero change in all five existing Medicaid/household outputs for 2026 and 2028; this carries over because no existing consumer or its parameters changes in round 2.

No partner contract test files or expected outputs changed. CI snapshots identify the head they verify in the final report and PR body.
