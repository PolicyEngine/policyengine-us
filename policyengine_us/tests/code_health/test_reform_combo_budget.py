"""Cap the reform-combo memory weight a single test file can carry.

policyengine-core's YAML runner deep-copies the full tax-benefit system
once per distinct (reforms, parametric-overrides) combination and caches
it for the life of the subprocess — the cache is never evicted. Each
structural-reform combo holds ~1.45 GB permanently (calibrated against 46
contrib batches on 16 GB CI runners, run 28756084246), so a file that
accumulates many combos can exceed what one subprocess may safely hold no
matter how the CI batcher splits work: files are the smallest unit a
subprocess can run.

The batcher (tests/test_batched.py) packs files so no subprocess exceeds
MAX_BATCH_COMBO_WEIGHT. This test enforces the same budget per FILE at
authoring time: when it fails, split the file's cases into smaller files
grouped by combo (see the RI ctc_reform_*_test.yaml split for precedent)
instead of raising the budget.
"""

import importlib.util

from policyengine_us.model_api import REPO

_spec = importlib.util.spec_from_file_location(
    "test_batched", REPO / "tests" / "test_batched.py"
)
_test_batched = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_test_batched)

POLICY_TESTS_ROOT = REPO / "tests" / "policy"


def test_no_test_file_exceeds_reform_combo_budget():
    over_budget = []
    for yaml_file in sorted(POLICY_TESTS_ROOT.rglob("*.yaml")):
        combos = _test_batched.file_reform_combos(yaml_file)
        weight = _test_batched.combo_weight(combos)
        if weight > _test_batched.MAX_BATCH_COMBO_WEIGHT:
            over_budget.append(
                f"{yaml_file.relative_to(REPO.parent)} "
                f"(weight {weight:.2f}, "
                f"{len(combos)} distinct reform combos)"
            )
    assert not over_budget, (
        "Test files exceed the per-file reform-combo budget of "
        f"{_test_batched.MAX_BATCH_COMBO_WEIGHT} (each distinct combo pins "
        "~1.45 GB for the life of its CI subprocess, and a file cannot be "
        "split across subprocesses). Split the cases into smaller files "
        "grouped by reform combo:\n  " + "\n  ".join(over_budget)
    )
