"""Property tests: Medicaid federal share for enrollees without federal status.

42 U.S.C. 1396b(v)(1) bars Title XIX payment for medical assistance to anyone
who fails the federal immigration test, apart from emergency services under
(v)(2) and the lawfully residing children and pregnant people option under
(v)(4). is_federal_medicaid_immigration_status_eligible applies that test,
including (v)(4); is_medicaid_immigration_status_eligible also counts
state-funded coverage. https://www.law.cornell.edu/uscode/text/42/1396b#v

For every generated person:

1. medicaid_federal_share is between 0 and 1.
2. An enrollee who fails the federal immigration test, or whose Medicaid
   category is NONE, gets 0, whichever route enrolled them (state coverage
   regardless of immigration status, California FFYP, Illinois HBI or Rhode
   Island's postpartum continuation).
3. An enrollee who passes the test in any category other than NONE or ADULT
   gets the state's regular FMAP. An ADULT gets the regular or the expansion
   FMAP.
4. An enrollee's federal and state costs add up to medicaid_cost, and a
   person who is not enrolled has no federal share or cost.

Each case is its own household, so states vary within one simulation.
"""

import numpy as np
from hypothesis import given, settings, strategies as st

from policyengine_us import Simulation

STATES = ["CA", "IL", "DC", "NY", "OR", "MA", "RI", "TX", "FL", "WA"]
STATUSES = [
    "CITIZEN",
    "LEGAL_PERMANENT_RESIDENT",
    "REFUGEE",
    "ASYLEE",
    "DEPORTATION_WITHHELD",
    "CUBAN_HAITIAN_ENTRANT",
    "CONDITIONAL_ENTRANT",
    "PAROLED_ONE_YEAR",
    "UNDOCUMENTED",
    "DACA",
    "TPS",
]
CATEGORIES = [
    "INFANT",
    "YOUNG_CHILD",
    "OLDER_CHILD",
    "YOUNG_ADULT",
    "ADULT",
    "PARENT",
    "PREGNANT",
    "SSI_RECIPIENT",
    "SENIOR_OR_DISABLED",
    "NONE",
    "MEDICALLY_NEEDY",
    "WORKING_DISABLED_BUY_IN",
    "SECTION_1115_MEC_ADULT",
]

case = st.tuples(
    st.sampled_from(STATES),
    st.sampled_from(STATUSES),
    st.sampled_from([0, 5, 10, 17, 19, 22, 30, 45, 50, 64, 67]),
    st.sampled_from(CATEGORIES),
    st.sampled_from([0, 2, 6, 20]),
    st.booleans(),
    st.sampled_from([0, 0.5, 1, 1.38, 2, 4]),
    st.booleans(),
    st.integers(0, 20_000),
)


def situation(cases, year):
    people, households = {}, {}
    for index, spec in enumerate(cases):
        state, status, age, category, years, foster, income, takes_up, cost = spec
        name = f"person{index}"
        people[name] = {
            "age": {year: age},
            "immigration_status": {year: status},
            "years_since_us_entry": {year: years},
            "was_in_foster_care": {year: foster},
            "medicaid_category": {year: category},
            "medicaid_household_size": {year: 1},
            "medicaid_income_level": {year: income},
            "takes_up_medicaid_if_eligible": {year: takes_up},
            "medicaid_cost": {year: cost},
        }
        households[f"household{index}"] = {
            "members": [name],
            "state_code": {year: state},
        }
    return {"people": people, "households": households}


@settings(max_examples=8, deadline=None, derandomize=True)
@given(
    st.sampled_from([2024, 2025, 2026, 2027]),
    st.lists(case, min_size=1, max_size=40),
)
def test_federal_share_follows_federal_immigration_status(year, cases):
    sim = Simulation(situation=situation(cases, year))
    share = sim.calculate("medicaid_federal_share", year)
    enrolled = sim.calculate("medicaid_enrolled", year)
    federal_status = sim.calculate(
        "is_federal_medicaid_immigration_status_eligible", year
    )
    category = sim.calculate("medicaid_category", year).decode_to_str()
    cost = sim.calculate("medicaid_cost", year)
    federal_cost = sim.calculate("medicaid_federal_cost", year)
    state_cost = sim.calculate("medicaid_state_cost", year)
    p = sim.tax_benefit_system.parameters(f"{year}-01-01").gov.hhs.medicaid
    regular = np.array([p.cost_share.fmap[spec[0]] for spec in cases])
    expansion = p.cost_share.expansion_fmap

    assert np.all((share >= 0) & (share <= 1))
    matched = enrolled & federal_status & (category != "NONE")
    assert np.all(share[~matched] == 0)
    other = matched & (category != "ADULT")
    assert np.allclose(share[other], regular[other])
    adult = matched & (category == "ADULT")
    assert np.all(
        np.isclose(share[adult], regular[adult]) | np.isclose(share[adult], expansion)
    )
    assert np.allclose(federal_cost[enrolled] + state_cost[enrolled], cost[enrolled])
    assert np.all(federal_cost[~enrolled] == 0)
