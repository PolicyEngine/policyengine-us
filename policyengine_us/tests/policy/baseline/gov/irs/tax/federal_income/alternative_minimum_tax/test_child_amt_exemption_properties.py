"""Properties of the AMT child exemption limitation that follow from the law.

- IRC 59(j)(1) (2016 ed.): for a child to whom IRC 1(g) applies, the AMT
  exemption cannot exceed earned income plus the indexed child amount.
- IRC 1(g)(2)(C): IRC 1(g) never applies to a joint return.
- IRC 55(d)(4)(A)(iii): IRC 59(j) does not apply from 2018, so a child's
  exemption equals that of an otherwise identical adult.

YAML cases pin hand-computed values; this test checks the properties across
generated households, without restating the model's formulas.
"""

import hypothesis
import numpy as np
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system

STATUSES = ("SINGLE", "JOINT", "SEPARATE", "HEAD_OF_HOUSEHOLD", "SURVIVING_SPOUSE")
CAP_YEARS = (2015, 2017)
NO_CAP_YEARS = (2018, 2025, 2026)
YEARS = CAP_YEARS + NO_CAP_YEARS
ADULT_AGE = 40

# Fixed cases keep each property non-vacuous whatever Hypothesis draws: a
# capped child, an uncapped child, an 18-year-old on each side of the support
# test, and a joint return by spouses under 18 (no support test applies).
FIXED_CASES = (
    dict(status="SINGLE", age=17, student=False, earnings=0, support=0, amti=50_000),
    dict(
        status="SINGLE", age=17, student=False, earnings=47_000, support=0, amti=77_000
    ),
    dict(
        status="SEPARATE",
        age=18,
        student=False,
        earnings=10_000,
        support=20_000,
        amti=60_000,
    ),
    dict(
        status="SINGLE",
        age=18,
        student=False,
        earnings=10_000,
        support=15_000,
        amti=60_000,
    ),
    dict(
        status="JOINT", age=17, student=False, earnings=29_000, support=0, amti=150_000
    ),
)


def situation(cases):
    """Each case appears twice: as given, and as an otherwise identical adult."""
    people, tax_units, households = {}, {}, {}
    twins = [dict(case, twin=False) for case in cases] + [
        dict(case, age=ADULT_AGE, student=False, twin=True) for case in cases
    ]
    for i, case in enumerate(twins):
        joint = case["status"] == "JOINT"
        members = []
        for role in ("head", "spouse") if joint else ("head",):
            person_id = f"{role}_{i}"
            members.append(person_id)
            people[person_id] = {
                "age": {year: case["age"] for year in YEARS},
                "is_full_time_student": {year: case["student"] for year in YEARS},
                "is_tax_unit_head": {year: role == "head" for year in YEARS},
                "is_tax_unit_spouse": {year: role == "spouse" for year in YEARS},
                "is_tax_unit_dependent": {year: False for year in YEARS},
                "adjusted_earnings": {
                    year: case["earnings"] if role == "head" else 0 for year in YEARS
                },
                "care_and_support_costs": {year: case["support"] for year in YEARS},
            }
        tax_units[f"unit_{i}"] = {
            "members": members,
            "filing_status": {year: case["status"] for year in YEARS},
            "amt_income": {year: case["amti"] for year in YEARS},
        }
        households[f"household_{i}"] = {
            "members": members,
            "state_code": {year: "TX" for year in YEARS},
        }
    return {"people": people, "tax_units": tax_units, "households": households}


case_strategy = st.fixed_dictionaries(
    {
        "status": st.sampled_from(STATUSES),
        "age": st.integers(14, 30),
        "student": st.booleans(),
        "earnings": st.integers(0, 150_000),
        "support": st.integers(0, 150_000),
        "amti": st.integers(0, 2_000_000),
    }
)


@hypothesis.settings(max_examples=5, deadline=None, derandomize=True)
@hypothesis.given(cases=st.lists(case_strategy, min_size=1, max_size=20))
def test_child_amt_exemption_properties(cases):
    cases = [*FIXED_CASES, *cases]
    n = len(cases)
    sim = Simulation(tax_benefit_system=system, situation=situation(cases))
    earnings = np.array([case["earnings"] for case in cases], dtype=float)

    for year in YEARS:
        applies = sim.calculate("amt_kiddie_tax_applies", year)
        exemption = sim.calculate("amt_exemption", year)
        status = sim.calculate("filing_status", year).decode_to_str()
        child, adult = slice(0, n), slice(n, 2 * n)
        p = system.parameters(str(year)).gov.irs.income.amt.exemption

        # IRC 1(g)(2)(C): never a joint return.
        assert not applies[status == "JOINT"].any(), year
        # An adult aged 40 is never a child under IRC 1(g)(2)(A).
        assert not applies[adult].any(), year
        # The exemption never exceeds the statutory amount for the status.
        assert np.all(exemption <= p.amount[status]), year

        if year in CAP_YEARS:
            # IRC 59(j)(1): earned income plus the indexed child amount.
            limit = earnings + p.child.amount
            covered = applies[child]
            assert covered.any(), year
            assert np.all(exemption[child][covered] <= limit[covered]), year
            # The limit is the only difference from an identical adult.
            np.testing.assert_array_equal(
                exemption[child],
                np.minimum(exemption[adult], np.where(covered, limit, np.inf)),
                err_msg=str(year),
            )
            # The limit binds for at least one fixed case.
            assert np.any(exemption[child] < exemption[adult]), year
        else:
            # IRC 55(d)(4)(A)(iii): no limit, so age makes no difference.
            np.testing.assert_array_equal(
                exemption[child], exemption[adult], err_msg=str(year)
            )
