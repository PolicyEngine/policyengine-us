"""The AFA contrib reform removes non_refundable_ctc from the federal
non-refundable credit list (fully-refundable restructure). Oklahoma's
ok_federal_ctc used to .index() that entry unconditionally, so any Oklahoma
simulation under the AFA raised ValueError. The formula now treats an
absent non-refundable CTC as fully refundable — this test locks that in
through the same Reform.from_dict path production traffic uses."""

import numpy as np
import pytest

from policyengine_core.reforms import Reform
from policyengine_us import Simulation


def test_ok_federal_ctc_computes_under_afa():
    reform = Reform.from_dict(
        {"gov.contrib.congress.afa.in_effect": {"2026-01-01.2100-12-31": True}},
        country_id="us",
    )
    situation = {
        "people": {
            "parent": {
                "age": {"2026": 35},
                "employment_income": {"2026": 30_000},
            },
            "child": {"age": {"2026": 4}},
        },
        "tax_units": {"tax_unit": {"members": ["parent", "child"]}},
        "spm_units": {"spm_unit": {"members": ["parent", "child"]}},
        "households": {
            "household": {
                "members": ["parent", "child"],
                "state_name": {"2026": "OK"},
            }
        },
    }
    sim = Simulation(situation=situation, reform=reform)
    ok_federal_ctc = sim.calculate("ok_federal_ctc", 2026)[0]
    refundable_ctc = sim.calculate("refundable_ctc", 2026)[0]
    # With the CTC fully refundable there is no non-refundable portion, so
    # the credit allowed for the Oklahoma calculation is the refundable CTC.
    assert ok_federal_ctc == refundable_ctc
    assert refundable_ctc > 0

    # [A1] Lock the full downstream consumer path: the Oklahoma Child
    # Care/Child Tax Credit takes the greater of 20% of the federal CDCC or
    # 5% of the federal CTC allowed, prorated by OK AGI / US AGI. Here AGI is
    # 30k <= the 100k eligibility limit, this is a full-year OK resident so
    # ok_agi / us_agi == 1, and there is no child-care spending so cdcc == 0.
    # The 5% CTC arm therefore wins, and the credit equals 5% of the federal
    # CTC allowed (which under AFA is the refundable CTC read above).
    ok_child_care_child_tax_credit = sim.calculate(
        "ok_child_care_child_tax_credit", 2026
    )[0]
    assert ok_child_care_child_tax_credit == pytest.approx(
        0.05 * refundable_ctc, rel=1e-4
    )


def _ok_situation(period, employment_income, *, with_child=True):
    """Build a single-parent Oklahoma household situation.

    Uses string period keys to match the neighboring contrib convention
    (see test_id_ga_ctc_reform_activation.py) [S1].
    """
    people = {
        "parent": {
            "age": {period: 35},
            "employment_income": {period: employment_income},
        }
    }
    members = ["parent"]
    if with_child:
        people["child"] = {"age": {period: 4}}
        members = ["parent", "child"]
    return {
        "people": people,
        "tax_units": {"tax_unit": {"members": members}},
        "spm_units": {"spm_unit": {"members": members}},
        "households": {
            "household": {
                "members": members,
                "state_name": {period: "OK"},
            }
        },
    }


def test_ok_federal_ctc_zero_ctc_guard_path_under_afa():
    """[A2] Guard path with no qualifying children: a single OK adult under
    AFA has no CTC at all. The guard returns refundable_ctc, which is 0 here,
    and — the point of the fix — the formula must not crash."""
    reform = Reform.from_dict(
        {"gov.contrib.congress.afa.in_effect": {"2026-01-01.2100-12-31": True}},
        country_id="us",
    )
    situation = _ok_situation("2026", 30_000, with_child=False)
    sim = Simulation(situation=situation, reform=reform)
    ok_federal_ctc = sim.calculate("ok_federal_ctc", 2026)[0]
    refundable_ctc = sim.calculate("refundable_ctc", 2026)[0]
    assert refundable_ctc == 0
    assert ok_federal_ctc == 0


# [S3] The three CTC-restructuring contrib reforms all remove
# non_refundable_ctc from the federal non-refundable credit list (AFA and
# ECPA via list-rebuild, FISC via neutralize_variable), which is exactly the
# fragility ok_federal_ctc's .index() call used to hit. Oklahoma is the only
# state that indexes the federal credit list, so smoke-test each flag: the
# Oklahoma credit must COMPUTE (no crash) and be finite and non-negative.
CTC_RESTRUCTURE_FLAGS = [
    "gov.contrib.congress.afa.in_effect",
    "gov.contrib.congress.tlaib.economic_dignity_for_all_agenda.end_child_poverty_act.in_effect",
    "gov.contrib.congress.golden.fisc_act.in_effect",
]


@pytest.mark.parametrize("in_effect_flag", CTC_RESTRUCTURE_FLAGS)
def test_ok_federal_ctc_computes_under_ctc_restructuring_reforms(in_effect_flag):
    reform = Reform.from_dict(
        {in_effect_flag: {"2026-01-01.2100-12-31": True}},
        country_id="us",
    )
    situation = _ok_situation("2026", 30_000, with_child=True)
    sim = Simulation(situation=situation, reform=reform)
    ok_federal_ctc = sim.calculate("ok_federal_ctc", 2026)[0]
    assert np.isfinite(ok_federal_ctc)
    assert ok_federal_ctc >= 0


def test_ok_federal_ctc_computes_after_afa_2039_cliff():
    """[S4] AFA's modify_parameters only runs through 2039-12-31; after that,
    non_refundable_ctc re-enters gov.irs.credits.non_refundable and the guard
    goes inert, so ok_federal_ctc falls back to its ordered-allocation path.
    This asserts the Oklahoma credit still computes at 2040 under AFA.

    NOTE: the 2039 cliff is a hard boundary in the AFA reform's
    modify_parameters (start 2025-01-01, stop 2039-12-31). If a future
    year-bump moves that stop date, this test would silently switch which
    branch of ok_federal_ctc it exercises — update the year here to stay on
    the post-cliff (ordered-allocation) side."""
    reform = Reform.from_dict(
        {"gov.contrib.congress.afa.in_effect": {"2026-01-01.2100-12-31": True}},
        country_id="us",
    )
    situation = _ok_situation("2040", 30_000, with_child=True)
    sim = Simulation(situation=situation, reform=reform)
    ok_federal_ctc = sim.calculate("ok_federal_ctc", 2040)[0]
    assert np.isfinite(ok_federal_ctc)
    assert ok_federal_ctc >= 0


def test_ok_federal_ctc_high_income_guard_branch_under_afa():
    """[S5] High-income OK household under AFA: the fully-refundable CTC is
    reduced/phased while still on the guard branch (non_refundable_ctc absent
    from the list). Assert the guard invariant relationally — the Oklahoma
    credit allowed equals the refundable CTC read from the same simulation —
    regardless of how far the phase-out has run (0 is a valid result)."""
    reform = Reform.from_dict(
        {"gov.contrib.congress.afa.in_effect": {"2026-01-01.2100-12-31": True}},
        country_id="us",
    )
    situation = _ok_situation("2026", 400_000, with_child=True)
    sim = Simulation(situation=situation, reform=reform)
    ok_federal_ctc = sim.calculate("ok_federal_ctc", 2026)[0]
    refundable_ctc = sim.calculate("refundable_ctc", 2026)[0]
    assert ok_federal_ctc == pytest.approx(refundable_ctc)
