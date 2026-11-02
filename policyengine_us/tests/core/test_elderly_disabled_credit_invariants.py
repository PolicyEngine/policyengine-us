"""Properties of the elderly or disabled credit (26 U.S.C. 22, Schedule R).

1. A married individual filing a separate return starts from $3,750
   (22(c)(2)(A)(iii)), and the later steps only reduce it, so the section 22
   amount for a separate filer never exceeds $3,750.
2. The credit never exceeds the Schedule R credit limit: tax before credits
   less the credits that precede it.

Each Hypothesis example is a batch of tax units run as one vectorized
simulation, so the test checks the formulas on mixed arrays as well.
"""

from hypothesis import HealthCheck, given, settings, strategies as st

from policyengine_us import Simulation

YEAR = 2024
SEPARATE_INITIAL_AMOUNT = 3_750

FILING_STATUSES = ["SINGLE", "JOINT", "SEPARATE", "HEAD_OF_HOUSEHOLD"]

money = st.one_of(st.just(0.0), st.floats(0, 60_000).map(round))

case = st.fixed_dictionaries(
    {
        "filing_status": st.sampled_from(FILING_STATUSES),
        "cohabitating": st.booleans(),
        "head_age": st.integers(40, 90),
        "spouse_age": st.integers(40, 90),
        "head_disabled": st.booleans(),
        "wages": money,
        "pension": money,
        "taxable_share": st.floats(0, 1),
        "social_security": money,
        "disability_payments": st.floats(0, 10_000).map(round),
    }
)


def build_situation(cases):
    people, tax_units, households = {}, {}, {}
    for i, c in enumerate(cases):
        head = f"head_{i}"
        pension = c["pension"]
        people[head] = {
            "age": {YEAR: c["head_age"]},
            "retired_on_total_disability": {YEAR: c["head_disabled"]},
            "employment_income": {YEAR: c["wages"]},
            "total_disability_payments": {
                YEAR: min(c["disability_payments"], c["wages"])
            },
            "pension_income": {YEAR: pension},
            "taxable_pension_income": {YEAR: round(pension * c["taxable_share"])},
            "social_security_retirement": {YEAR: c["social_security"]},
        }
        members = [head]
        if c["filing_status"] == "JOINT":
            spouse = f"spouse_{i}"
            people[spouse] = {"age": {YEAR: c["spouse_age"]}}
            members.append(spouse)
        tax_units[f"tax_unit_{i}"] = {
            "members": members,
            "filing_status": {YEAR: c["filing_status"]},
            "cohabitating_spouses": {YEAR: c["cohabitating"]},
        }
        households[f"household_{i}"] = {
            "members": members,
            "state_code": {YEAR: "TX"},
        }
    return {"people": people, "tax_units": tax_units, "households": households}


@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.lists(case, min_size=8, max_size=8))
def test_separate_amount_and_credit_limit(cases):
    sim = Simulation(situation=build_situation(cases))
    filing_status = sim.calculate("filing_status", YEAR).decode_to_str()
    section_22 = sim.calculate("section_22_income", YEAR)
    credit = sim.calculate("elderly_disabled_credit", YEAR)
    credit_limit = sim.calculate("elderly_disabled_credit_credit_limit", YEAR)
    tax_before_credits = sim.calculate("income_tax_before_credits", YEAR)

    separate = filing_status == "SEPARATE"
    assert (section_22[separate] <= SEPARATE_INITIAL_AMOUNT).all()
    assert (section_22 >= 0).all()
    assert (credit >= 0).all()
    assert (credit <= credit_limit + 1e-6).all()
    assert (credit <= tax_before_credits + 1e-6).all()
