"""Iowa, Kansas, Kentucky, Louisiana and Maryland rules for a filer who can be
claimed as a dependent.

A return on which the filer (or, if joint, either spouse) can be claimed has no
dependents (IRC 152(b)(1)), so these states' dependent exemptions and credits,
Kansas's food sales tax credit child route and Maryland's child tax credit
count none. A claimed filer keeps Iowa's personal credit and, from 2024,
Kansas's filing-status allowance, but gets no Kansas exemptions in 2021-2023,
no Iowa low-income exemption above $5,000 or tax reduction, and no Maryland
personal exemption, poverty line credit or childless EITC; on a joint return
Maryland's poverty line credit stays for the spouse who cannot be claimed.

For couples drawn by Hypothesis and a seeded population in these states, with
either, both or neither spouse claimed:

1. Swap invariance: each output is the same under either head/spouse
   labelling.
2. Monotonicity: marking another filer as claimed never raises the amounts in
   MONOTONE. This holds for the drawn inputs, which have no self-employment
   losses: on separate Maryland returns a claimable spouse's loss no longer
   offsets the other spouse's earnings, which is intended.
3. Identities: with a claimable filer there is no Louisiana dependent
   exemption, Maryland aged dependent exemption or child tax credit, and no
   pro forma federal EITC without a child; with no claimable filer the
   poverty line credit's earned income and poverty level are the unchanged
   EITC earned income and tax unit poverty guideline.
4. Differential: wherever the federal EITC's eligibility holds, Maryland's
   pro forma federal EITC without the minimum age equals the federal credit
   before take-up, so the two eligibility paths agree, including on the
   claimable-filer bar.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us.tests.core.test_claimable_filer_federal_invariants import (
    check_monotone,
    check_swap,
)
from policyengine_us.tests.core.test_dependent_elsewhere_head_spouse_swap_invariance import (
    CLAIM_PATTERNS,
    TOLERANCE,
    _calc,
    _crafted_cases,
    _seeded_couples,
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


@st.composite
def couples(draw):
    return {
        "state": draw(st.sampled_from(STATES)),
        "adults": [draw(adults()), draw(adults())],
        "dependents": draw(st.lists(dependents(), max_size=2)),
        "claimed": draw(st.sampled_from(CLAIM_PATTERNS)),
    }


def _identities(sim, year):
    claimed = _calc(sim, "head_or_spouse_is_dependent_elsewhere", year) > 0
    every = _calc(sim, "every_filer_is_dependent_elsewhere", year) > 0
    childless = _calc(sim, "eitc_child_count", year) == 0
    for name in ["la_dependents_exemption", "md_aged_dependent_exemption", "md_ctc"]:
        assert not _calc(sim, name, year)[claimed].any(), name
    pro_forma = _calc(sim, "federal_eitc_without_age_minimum", year)
    assert not pro_forma[claimed & childless].any()
    assert not _calc(sim, "is_eligible_md_poverty_line_credit", year)[every].any()
    # Each tax unit has its own household, in the same order.
    md = np.asarray(sim.calculate("state_code_str", year)) == "MD"
    nobody = md & ~claimed
    np.testing.assert_allclose(
        _calc(sim, "md_poverty_line_credit_earned_income", year)[nobody],
        _calc(sim, "eitc_earned_income", year)[nobody],
        atol=TOLERANCE,
    )
    np.testing.assert_allclose(
        _calc(sim, "md_poverty_line_credit_income_level", year)[nobody],
        _calc(sim, "tax_unit_fpg", year)[nobody],
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
    max_examples=2,
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
