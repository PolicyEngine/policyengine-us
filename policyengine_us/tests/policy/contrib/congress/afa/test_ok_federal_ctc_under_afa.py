"""The AFA contrib reform removes non_refundable_ctc from the federal
non-refundable credit list (fully-refundable restructure). Oklahoma's
ok_federal_ctc used to .index() that entry unconditionally, so any Oklahoma
simulation under the AFA raised ValueError. The formula now treats an
absent non-refundable CTC as fully refundable — this test locks that in
through the same Reform.from_dict path production traffic uses."""

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


# [A1] Only AFA removes non_refundable_ctc from the federal non-refundable
# credit PARAMETER LIST (gov.irs.credits.non_refundable), so only AFA fires
# ok_federal_ctc's fully-refundable guard (return refundable_ctc). The other
# two CTC-restructuring reforms leave the parameter list intact, so the guard
# is INERT and the ordered-allocation (.index()) branch runs:
#   - AFA  -> list rebuilt WITHOUT non_refundable_ctc -> guard FIRES;
#            ok_federal_ctc == refundable_ctc.
#   - ECPA -> filters non_refundable_ctc only inside its overridden
#            income_tax_non_refundable_credits variable; the parameter list
#            still contains non_refundable_ctc -> guard INERT, .index() branch
#            runs -> positive baseline-style CTC.
#   - FISC -> neutralizes both refundable_ctc and non_refundable_ctc but
#            leaves the parameter list intact -> guard INERT, .index() branch
#            runs against two zeroed components -> ok_federal_ctc == 0.
# Oklahoma is the only state that indexes the federal credit list, so each
# flag is a per-branch regression check (below), not just a no-crash smoke.


def _reform_for(in_effect_flag):
    return Reform.from_dict(
        {in_effect_flag: {"2026-01-01.2100-12-31": True}},
        country_id="us",
    )


AFA_FLAG = "gov.contrib.congress.afa.in_effect"
ECPA_FLAG = "gov.contrib.congress.tlaib.economic_dignity_for_all_agenda.end_child_poverty_act.in_effect"
FISC_FLAG = "gov.contrib.congress.golden.fisc_act.in_effect"


def _check_afa(sim):
    # Guard FIRES: non_refundable_ctc removed from the parameter list, so the
    # Oklahoma credit allowed collapses to the refundable CTC.
    ok_federal_ctc = sim.calculate("ok_federal_ctc", 2026)[0]
    refundable_ctc = sim.calculate("refundable_ctc", 2026)[0]
    assert ok_federal_ctc == refundable_ctc


def _check_ecpa(sim):
    # Guard INERT (.index() branch): ECPA keeps non_refundable_ctc in the
    # parameter list, so ok_federal_ctc takes the ordered-allocation branch and
    # returns a positive baseline-style CTC. A passing assertion here is NOT an
    # endorsement of the ECPA-interaction value — that phantom baseline-style
    # CTC is pre-existing behavior; the guard fix does not touch this branch.
    ok_federal_ctc = sim.calculate("ok_federal_ctc", 2026)[0]
    assert ok_federal_ctc > 0


def _check_fisc(sim):
    # Guard INERT (.index() branch): FISC leaves the parameter list intact but
    # neutralizes both refundable_ctc and non_refundable_ctc, so the ordered-
    # allocation branch sums two zeroed components to 0.
    ok_federal_ctc = sim.calculate("ok_federal_ctc", 2026)[0]
    assert ok_federal_ctc == 0


# [A2] (flag, per-branch check) table replacing the weak isfinite/>=0 smoke.
CTC_RESTRUCTURE_CHECKS = [
    (AFA_FLAG, _check_afa),
    (ECPA_FLAG, _check_ecpa),
    (FISC_FLAG, _check_fisc),
]


@pytest.mark.parametrize("in_effect_flag,check", CTC_RESTRUCTURE_CHECKS)
def test_ok_federal_ctc_computes_under_ctc_restructuring_reforms(in_effect_flag, check):
    """[A2] Per-flag regression: AFA fires the guard (ok_federal_ctc ==
    refundable_ctc); ECPA and FISC leave the guard inert and run the ordered-
    allocation branch (ECPA -> positive phantom baseline-style CTC, pre-existing
    behavior and not an endorsement; FISC -> 0 from two neutralized CTC vars)."""
    reform = _reform_for(in_effect_flag)
    situation = _ok_situation("2026", 30_000, with_child=True)
    sim = Simulation(situation=situation, reform=reform)
    check(sim)


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
    afa_sim = Simulation(situation=situation, reform=reform)
    afa_ok_federal_ctc = afa_sim.calculate("ok_federal_ctc", 2040)[0]
    # [S2] Post-cliff (2040 > AFA's 2039 stop) the parameter list is unmodified,
    # so the guard is inert and AFA must produce exactly the baseline result.
    # Compare against the SAME household with no reform — no hardcoded value.
    baseline_sim = Simulation(situation=_ok_situation("2040", 30_000, with_child=True))
    baseline_ok_federal_ctc = baseline_sim.calculate("ok_federal_ctc", 2040)[0]
    assert afa_ok_federal_ctc == baseline_ok_federal_ctc


def test_ok_federal_ctc_high_income_guard_branch_under_afa():
    """[A3] OK household with AGI INSIDE the AFA phase-out range but still
    carrying a residual credit (single filer, one child under age 6, AGI
    ~$150k — above the $112,500 SINGLE lower threshold but below full phase-out,
    so the AFA CTC is partially reduced yet non-zero). Assert BOTH that a
    residual refundable CTC survives AND the guard invariant holds
    (ok_federal_ctc == refundable_ctc). Requiring refundable_ctc > 0
    distinguishes the guard branch from a trivial 0 == 0 pass at full
    phase-out."""
    reform = Reform.from_dict(
        {"gov.contrib.congress.afa.in_effect": {"2026-01-01.2100-12-31": True}},
        country_id="us",
    )
    situation = _ok_situation("2026", 150_000, with_child=True)
    sim = Simulation(situation=situation, reform=reform)
    ok_federal_ctc = sim.calculate("ok_federal_ctc", 2026)[0]
    refundable_ctc = sim.calculate("refundable_ctc", 2026)[0]
    assert refundable_ctc > 0
    assert ok_federal_ctc == pytest.approx(refundable_ctc)


def test_ok_federal_ctc_leading_edge_2025_under_afa():
    """[S3] 2025 leading edge: AFA's modify_parameters removes
    non_refundable_ctc from the parameter list starting 2025-01-01, so at 2025
    (the first modify_parameters year) the guard already fires and the Oklahoma
    credit collapses to refundable_ctc — the same invariant as 2026+."""
    # Enable the reform from 2025 so its modify_parameters (start 2025-01-01) is
    # exercised at its leading edge.
    reform = Reform.from_dict(
        {"gov.contrib.congress.afa.in_effect": {"2025-01-01.2100-12-31": True}},
        country_id="us",
    )
    situation = _ok_situation("2025", 30_000, with_child=True)
    sim = Simulation(situation=situation, reform=reform)
    ok_federal_ctc = sim.calculate("ok_federal_ctc", 2025)[0]
    refundable_ctc = sim.calculate("refundable_ctc", 2025)[0]
    # Guard fires at the 2025 leading edge (param removal active): the credit
    # allowed equals the refundable CTC. Correct by construction, no hardcode.
    assert ok_federal_ctc == refundable_ctc


def test_ok_child_care_child_tax_credit_downstream_under_afa():
    """[S4a] Downstream OK Child Care/Child Tax Credit with a nonzero federal
    CDCC under AFA: the credit is the greater of 20% of the federal CDCC and 5%
    of the Oklahoma federal CTC allowed (Form 511 Schedule 511-F). This pins
    that the CDCC arm flows through under AFA (ok_federal_ctc == refundable_ctc
    here) and that the greater-of selection is correct, whichever arm wins.
    AGI is below the $100k OK limit and OK AGI == US AGI (full-year resident),
    so no proration/eligibility factor applies."""
    reform = Reform.from_dict(
        {"gov.contrib.congress.afa.in_effect": {"2026-01-01.2100-12-31": True}},
        country_id="us",
    )
    situation = {
        "people": {
            "parent": {
                "age": {"2026": 35},
                "employment_income": {"2026": 60_000},
            },
            "child": {"age": {"2026": 4}},
        },
        "tax_units": {
            "tax_unit": {
                "members": ["parent", "child"],
                # Real child-care spend so the federal CDCC (and thus the 20%
                # arm) is nonzero; cdcc_relevant_expenses consumes this input.
                "tax_unit_childcare_expenses": {"2026": 8_000},
            }
        },
        "spm_units": {"spm_unit": {"members": ["parent", "child"]}},
        "households": {
            "household": {
                "members": ["parent", "child"],
                "state_name": {"2026": "OK"},
            }
        },
    }
    sim = Simulation(situation=situation, reform=reform)
    cdcc = sim.calculate("cdcc", 2026)[0]
    ok_federal_ctc = sim.calculate("ok_federal_ctc", 2026)[0]
    ok_credit = sim.calculate("ok_child_care_child_tax_credit", 2026)[0]
    p = sim.tax_benefit_system.parameters(
        "2026-01-01"
    ).gov.states.ok.tax.income.credits.child
    # The federal CDCC arm is genuinely exercised (nonzero), so this is not a
    # no-op even though AFA's enlarged CTC makes the 5% arm win here.
    assert cdcc > 0
    expected = max(p.cdcc_fraction * cdcc, p.ctc_fraction * ok_federal_ctc)
    assert ok_credit == pytest.approx(expected, rel=1e-4)


def test_ok_child_care_child_tax_credit_over_agi_limit_under_afa():
    """[S4b] Downstream OK Child Care/Child Tax Credit is $0 when federal AGI
    exceeds the $100k Oklahoma eligibility limit, even under AFA."""
    reform = Reform.from_dict(
        {"gov.contrib.congress.afa.in_effect": {"2026-01-01.2100-12-31": True}},
        country_id="us",
    )
    situation = _ok_situation("2026", 150_000, with_child=True)
    sim = Simulation(situation=situation, reform=reform)
    us_agi = sim.calculate("adjusted_gross_income", 2026)[0]
    p = sim.tax_benefit_system.parameters(
        "2026-01-01"
    ).gov.states.ok.tax.income.credits.child
    # Confirm the household is genuinely over the OK AGI eligibility limit.
    assert us_agi > p.agi_limit
    ok_credit = sim.calculate("ok_child_care_child_tax_credit", 2026)[0]
    assert ok_credit == 0
