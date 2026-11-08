"""Vermont's child care payment counts only children who attend care.

Section V of the CCFAP Regulations pays only for weeks of attendance, in the
2009 text and as the division revised it effective June 30, 2024. The model
reads a child's care hours as attendance and gives the children in care the
bill shares of the members not in care. It falls back on each child's share of
the SPM unit's bill only when no child in the unit has care hours.

1. Once one child in the SPM unit has care hours, a sibling with none adds
   nothing to the payment, whatever the bill, the share, the sibling's age,
   either provider type or the year. Through 2023 the bill caps the payment, so
   the child in care has to carry the sibling's share of it.
2. Care hours on an adult change nothing.
3. For a preschooler in full-time care at a licensed center in 2026, with a
   sibling in no care, the state pays the $439 state rate less the share and the
   family owes the whole bill less that payment, each floored at zero. That is
   the department's sample invoice in its January 13, 2026 memo
   (CDD-Memo-UPK-and-CCFAP-family-tuition, PDF page 6).
"""

import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

WEEKS = 52
TOLERANCE = 0.02
PROVIDERS = ["LICENSED_CENTER", "REGISTERED_HOME"]
# 2023 caps the state rate at the bill; 2024 and 2026 pay the state rate.
YEARS = [2023, 2024, 2026]
# Full-time preschool at a licensed center from January 1, 2024.
PRESCHOOL_FULL_TIME_RATE = 439


def vermont(children, weekly_bill, weekly_share, year=2026, adult_hours=0):
    """Weekly state payment, family expense and counted subsidy."""
    members = ["parent", *children]
    parent = {"age": {year: 30}}
    if adult_hours:
        parent["childcare_hours_per_week"] = {year: adult_hours}
    people = {"parent": parent}
    for name, child in children.items():
        person = {
            "age": {year: child["age"]},
            "is_tax_unit_dependent": {year: True},
            "vt_ccfap_provider_type": {year: child["provider"]},
        }
        if child["hours"]:
            person["childcare_hours_per_week"] = {year: child["hours"]}
        people[name] = person
    situation = {
        "people": people,
        "tax_units": {"tax_unit": {"members": members}},
        "spm_units": {
            "spm_unit": {
                "members": members,
                "vt_ccfap_eligible": {year: True},
                "vt_ccfap_family_share": {year: weekly_share * WEEKS},
                "spm_unit_pre_subsidy_childcare_expenses": {year: weekly_bill * WEEKS},
            }
        },
        "families": {"family": {"members": members}},
        "marital_units": {"marital_unit": {"members": ["parent"]}},
        "households": {"household": {"members": members, "state_name": {year: "VT"}}},
    }
    simulation = Simulation(situation=situation)
    return [
        float(simulation.calculate(name, year)[0]) / WEEKS
        for name in (
            "child_care_subsidies",
            "childcare_expenses",
            "household_child_care_subsidies",
        )
    ]


@settings(max_examples=15, deadline=None)
# Part-time, full-time and extended care for the child with hours; a sibling who
# is an infant, a preschooler or school age; no bill and no share.
@example(
    hours=10,
    age=3,
    sibling_age=10,
    provider=0,
    sibling_provider=0,
    bill=350,
    share=300,
    year=2026,
)
@example(
    hours=35,
    age=3,
    sibling_age=0,
    provider=0,
    sibling_provider=1,
    bill=350,
    share=0,
    year=2026,
)
@example(
    hours=60,
    age=1,
    sibling_age=4,
    provider=1,
    sibling_provider=0,
    bill=0,
    share=50,
    year=2026,
)
# Through 2023 the bill caps the rate, and half of $350 falls below the $325
# full-time preschool rate.
@example(
    hours=35,
    age=3,
    sibling_age=0,
    provider=0,
    sibling_provider=1,
    bill=350,
    share=0,
    year=2023,
)
# One hour at age 12 and 70 hours at age 0.
@example(
    hours=1,
    age=12,
    sibling_age=0,
    provider=0,
    sibling_provider=1,
    bill=350,
    share=0,
    year=2026,
)
@example(
    hours=70,
    age=0,
    sibling_age=12,
    provider=1,
    sibling_provider=0,
    bill=350,
    share=0,
    year=2026,
)
# Each side of the part-time to full-time edge (25 hours) and the full-time to
# extended edge (50 hours).
@example(
    hours=25,
    age=4,
    sibling_age=7,
    provider=0,
    sibling_provider=0,
    bill=300,
    share=0,
    year=2023,
)
@example(
    hours=26,
    age=4,
    sibling_age=7,
    provider=1,
    sibling_provider=1,
    bill=300,
    share=100,
    year=2024,
)
@example(
    hours=50,
    age=2,
    sibling_age=9,
    provider=0,
    sibling_provider=1,
    bill=800,
    share=0,
    year=2026,
)
@example(
    hours=51,
    age=2,
    sibling_age=9,
    provider=1,
    sibling_provider=0,
    bill=800,
    share=200,
    year=2023,
)
@given(
    hours=st.integers(min_value=1, max_value=70),
    age=st.integers(min_value=0, max_value=12),
    sibling_age=st.integers(min_value=0, max_value=12),
    provider=st.integers(min_value=0, max_value=1),
    sibling_provider=st.integers(min_value=0, max_value=1),
    bill=st.integers(min_value=0, max_value=800),
    share=st.integers(min_value=0, max_value=600),
    year=st.sampled_from(YEARS),
)
def test_a_sibling_with_no_hours_adds_nothing(
    hours, age, sibling_age, provider, sibling_provider, bill, share, year
):
    child = dict(age=age, hours=hours, provider=PROVIDERS[provider])
    sibling = dict(age=sibling_age, hours=0, provider=PROVIDERS[sibling_provider])
    alone, _, _ = vermont({"child": child}, bill, share, year)
    with_sibling, _, _ = vermont(
        {"child": child, "sibling": sibling}, bill, share, year
    )
    assert with_sibling == pytest.approx(alone, abs=TOLERANCE)


@settings(max_examples=10, deadline=None)
# Hours on the parent alone, and on the parent beside a child with hours before
# 2024.
@example(adult_hours=10, hours=0, sibling_hours=0, bill=350, share=0, year=2026)
@example(adult_hours=40, hours=35, sibling_hours=0, bill=350, share=0, year=2023)
@given(
    adult_hours=st.integers(min_value=1, max_value=70),
    hours=st.integers(min_value=0, max_value=70),
    sibling_hours=st.integers(min_value=0, max_value=70),
    bill=st.integers(min_value=0, max_value=800),
    share=st.integers(min_value=0, max_value=600),
    year=st.sampled_from(YEARS),
)
def test_an_adults_care_hours_change_nothing(
    adult_hours, hours, sibling_hours, bill, share, year
):
    children = {
        "preschooler": dict(age=3, hours=hours, provider="LICENSED_CENTER"),
        "sibling": dict(age=10, hours=sibling_hours, provider="REGISTERED_HOME"),
    }
    without = vermont(children, bill, share, year)
    with_adult_hours = vermont(children, bill, share, year, adult_hours)
    assert with_adult_hours == pytest.approx(without, abs=TOLERANCE)


@settings(max_examples=15, deadline=None)
# The memo's invoice, a bill below the state's payment, no share, and a share at
# or above the state rate.
@example(bill=350, share=300, sibling_age=10)
@example(bill=100, share=300, sibling_age=0)
@example(bill=350, share=0, sibling_age=6)
@example(bill=350, share=439, sibling_age=12)
@example(bill=350, share=500, sibling_age=4)
@given(
    bill=st.integers(min_value=1, max_value=800),
    share=st.integers(min_value=0, max_value=600),
    sibling_age=st.integers(min_value=0, max_value=12),
)
def test_the_family_balance_follows_the_invoice_for_the_child_in_care(
    bill, share, sibling_age
):
    preschooler = dict(age=3, hours=35, provider="LICENSED_CENTER")
    sibling = dict(age=sibling_age, hours=0, provider="LICENSED_CENTER")
    paid, balance, counted = vermont(
        {"preschooler": preschooler, "sibling": sibling}, bill, share
    )
    state_payment = max(PRESCHOOL_FULL_TIME_RATE - share, 0)
    assert paid == pytest.approx(state_payment, abs=TOLERANCE)
    assert balance == pytest.approx(max(bill - state_payment, 0), abs=TOLERANCE)
    assert counted == pytest.approx(min(state_payment, bill), abs=TOLERANCE)
