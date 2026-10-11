"""Iowa, Kansas, Kentucky, Louisiana and Maryland rules for a filer who can be
claimed as a dependent.

A return on which the filer (or, if joint, either spouse) can be claimed has no
dependents unless the would-be claimant meets the filing exception (IRC
152(b)(1), Publication 501), so these states' dependent exemptions and credits,
Kansas's food sales tax credit child route, Maryland's child tax credit and the
childless pro forma EITC follow that test. Iowa's low-income exemption and tax
reduction and Kansas's 2021-2023 exemptions turn on an actual claim; Maryland's
own exemption and poverty line credit turn on claimability (filing status 6).

For couples drawn by Hypothesis (claimable, claimed and filing-exception
patterns) and a seeded population in these states:

1. Swap invariance: each output is the same under either head/spouse
   labelling.
2. Monotonicity: marking another filer as claimed never raises the amounts in
   MONOTONE. This holds for the drawn inputs, which have no self-employment
   losses: on separate Maryland returns a claimable spouse's loss no longer
   offsets the other spouse's earnings, which is intended.
3. Identities: with a filer claimable outside the filing exception there is no
   Louisiana dependent exemption, Maryland aged dependent exemption or child
   tax credit, and no pro forma federal EITC without a child; with every filer
   claimable, no poverty line credit.
4. Differential: wherever the federal EITC's eligibility holds, Maryland's
   pro forma federal EITC without the minimum age equals the federal credit
   before take-up and filing.
5. Unchanged when nobody can be claimed: Maryland's exemption count is the tax
   unit's size, the poverty line credit's earned income and poverty level are
   `eitc_earned_income` and `tax_unit_fpg`, and Louisiana's dependent
   exemption is $1,000 per dependent.
6. Filing exception scope: the exception never lowers the 152(b)(1) amounts in
   EXCEPTION_RESTORES and does not change the claimability and actual-claim
   rules in EXCEPTION_NEUTRAL.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.tests.core.test_claimable_filer_federal_invariants import (
    check_monotone,
    check_swap,
)
from policyengine_us.tests.core.test_dependent_elsewhere_head_spouse_swap_invariance import (
    CLAIM_PATTERNS,
    TOLERANCE,
    _calc,
    _crafted_cases,
    _exception_variants,
    _seeded_couples,
    _situation,
    adults,
    dependents,
)

STATES = ["IA", "KS", "KY", "LA", "MD"]
# 2022: Iowa's net-income path, Kansas's exemption count and Louisiana's
# exemptions; 2024: Iowa's consolidated path and Kansas's filing-status
# allowance; 2026: Louisiana's flat tax and Maryland's child tax credit
# phase-out.
YEARS = [2022, 2024, 2026]
MONOTONE = [
    "ia_exemption_credit",
    "ks_exemptions",
    "ks_fstc",
    "la_dependents_exemption",
    "md_personal_exemptions_count",
    "md_total_personal_exemptions",
    "md_aged_dependent_exemption",
    "federal_eitc_without_age_minimum",
    "md_ctc",
    "md_poverty_line_credit_earned_income",
]
OUTPUTS = MONOTONE + [
    "ia_is_tax_exempt",
    "ia_income_tax",
    "ks_income_tax",
    "ky_income_tax",
    "la_income_tax",
    "is_eligible_md_poverty_line_credit",
    "md_poverty_line_credit",
    "md_local_poverty_line_credit",
    "md_income_tax",
    "state_income_tax",
]
# 152(b)(1) amounts that the claimant filing exception restores.
EXCEPTION_RESTORES = [
    "ia_exemption_credit",
    "ks_exemptions",
    "ks_fstc",
    "la_dependents_exemption",
    "md_personal_exemptions_count",
    "md_aged_dependent_exemption",
    "federal_eitc_without_age_minimum",
    "md_ctc",
]
# Rules on claimability or an actual claim, which the exception leaves alone.
EXCEPTION_NEUTRAL = [
    "ia_is_tax_exempt",
    "md_poverty_line_credit_earned_income",
]


@st.composite
def couples(draw):
    claimable = draw(st.sampled_from(CLAIM_PATTERNS))
    claimed = tuple(can_claim and draw(st.booleans()) for can_claim in claimable)
    return {
        "state": draw(st.sampled_from(STATES)),
        "adults": [draw(adults()), draw(adults())],
        "dependents": draw(st.lists(dependents(), max_size=2)),
        "claimed": claimed,
        "claimable": claimable,
        "exception": tuple(
            not is_claimed and draw(st.booleans()) for is_claimed in claimed
        ),
    }


def _identities(sim, year):
    claimable = _calc(sim, "head_or_spouse_is_dependent_elsewhere", year) > 0
    no_dependents = (
        _calc(
            sim, "head_or_spouse_is_dependent_elsewhere_without_filing_exception", year
        )
        > 0
    )
    every = _calc(sim, "every_filer_is_dependent_elsewhere", year) > 0
    childless = _calc(sim, "eitc_child_count", year) == 0
    for name in ["la_dependents_exemption", "md_aged_dependent_exemption", "md_ctc"]:
        assert not _calc(sim, name, year)[no_dependents].any(), name
    pro_forma = _calc(sim, "federal_eitc_without_age_minimum", year)
    assert not pro_forma[no_dependents & childless].any()
    assert not _calc(sim, "is_eligible_md_poverty_line_credit", year)[every].any()
    # Each tax unit has its own household, in the same order.
    state = np.asarray(sim.calculate("state_code_str", year))
    md, la = state == "MD", state == "LA"
    # 5. Unchanged when nobody can be claimed.
    nobody = ~claimable
    np.testing.assert_array_equal(
        _calc(sim, "md_personal_exemptions_count", year)[md & nobody],
        _calc(sim, "tax_unit_size", year)[md & nobody],
    )
    np.testing.assert_allclose(
        _calc(sim, "md_poverty_line_credit_earned_income", year)[md & nobody],
        _calc(sim, "eitc_earned_income", year)[md & nobody],
        atol=TOLERANCE,
    )
    np.testing.assert_allclose(
        _calc(sim, "md_poverty_line_credit_income_level", year)[md & nobody],
        _calc(sim, "tax_unit_fpg", year)[md & nobody],
        atol=TOLERANCE,
    )
    np.testing.assert_allclose(
        _calc(sim, "la_dependents_exemption", year)[la & nobody],
        1_000 * _calc(sim, "tax_unit_dependents", year)[la & nobody],
        atol=TOLERANCE,
    )
    # 4. Differential: the federal credit before take-up and filing.
    federal_eligible = md & (_calc(sim, "eitc_eligible", year) > 0)
    federal = np.minimum(
        _calc(sim, "eitc_phased_in", year),
        np.maximum(
            0, _calc(sim, "eitc_maximum", year) - _calc(sim, "eitc_reduction", year)
        ),
    )
    np.testing.assert_allclose(
        pro_forma[federal_eligible], federal[federal_eligible], atol=TOLERANCE
    )


@settings(
    max_examples=3,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.sampled_from(YEARS), st.lists(couples(), min_size=6, max_size=12))
def test_ia_ks_ky_la_md_claimable_filer_rules_are_label_free(year, units):
    check_swap(units, year, OUTPUTS, _identities)


@pytest.mark.parametrize("year", YEARS)
def test_ia_ks_ky_la_md_claimable_filer_rules_seeded_population(year):
    units = _seeded_couples(STATES, per_state=3) + _crafted_cases(STATES)
    check_swap(units, year, OUTPUTS, _identities)
    check_monotone(units, year, MONOTONE, _identities)


@pytest.mark.parametrize("year", [2022, 2025])
def test_ia_ks_ky_la_md_filing_exception_scope(year):
    # Each unit runs four times with nobody actually claimed: claimable
    # without the exception (both labellings), then with it.
    units = [
        unit
        for unit in _seeded_couples(STATES, per_state=3) + _crafted_cases(STATES)
        if any(unit["claimed"])
    ]
    sim = Simulation(situation=_situation(units, year, _exception_variants))
    for name in EXCEPTION_RESTORES + EXCEPTION_NEUTRAL:
        copies = _calc(sim, name, year).reshape(-1, 4)
        np.testing.assert_allclose(
            copies[:, 0::2], copies[:, 1::2], atol=TOLERANCE, rtol=0
        )
        without, with_exception = copies[:, :2], copies[:, 2:]
        if name in EXCEPTION_NEUTRAL:
            np.testing.assert_allclose(
                with_exception,
                without,
                atol=TOLERANCE,
                rtol=0,
                err_msg=f"The filing exception changes {name}",
            )
        else:
            assert not (with_exception < without - TOLERANCE).any(), (
                f"The filing exception lowers {name}"
            )
