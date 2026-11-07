"""Vermont's child care payment counts only children who attend care.

Under CCFAP Regulations V, as the department revised it on June 28, 2024,
payment runs from the first week of submitted attendance. The model reads care
hours as attendance, and falls back on the SPM unit's bill only when no one in
the unit has care hours.

1. Once one child in the SPM unit has care hours, a sibling with none adds
   nothing to the payment, whatever the bill, the share, the sibling's age or
   either provider type.
2. For a preschooler in full-time care at a licensed center in 2026, with a
   sibling in no care, the state pays the $439 state rate less the share and the
   family owes the whole bill less that payment, each floored at zero. That is
   the department's sample invoice in its January 13, 2026 memo
   (CDD-Memo-UPK-and-CCFAP-family-tuition, PDF page 6).
"""

import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEAR = 2026
WEEKS = 52
TOLERANCE = 0.02
PROVIDERS = ["LICENSED_CENTER", "REGISTERED_HOME"]
# Full-time preschool at a licensed center from January 1, 2024.
PRESCHOOL_FULL_TIME_RATE = 439


def vermont(children, weekly_bill, weekly_share):
    """Weekly state payment, family expense and counted subsidy."""
    members = ["parent", *children]
    people = {"parent": {"age": {YEAR: 30}}}
    for name, child in children.items():
        person = {
            "age": {YEAR: child["age"]},
            "is_tax_unit_dependent": {YEAR: True},
            "vt_ccfap_provider_type": {YEAR: child["provider"]},
        }
        if child["hours"]:
            person["childcare_hours_per_week"] = {YEAR: child["hours"]}
        people[name] = person
    situation = {
        "people": people,
        "tax_units": {"tax_unit": {"members": members}},
        "spm_units": {
            "spm_unit": {
                "members": members,
                "vt_ccfap_eligible": {YEAR: True},
                "vt_ccfap_family_share": {YEAR: weekly_share * WEEKS},
                "spm_unit_pre_subsidy_childcare_expenses": {YEAR: weekly_bill * WEEKS},
            }
        },
        "families": {"family": {"members": members}},
        "marital_units": {"marital_unit": {"members": ["parent"]}},
        "households": {"household": {"members": members, "state_name": {YEAR: "VT"}}},
    }
    simulation = Simulation(situation=situation)
    return [
        float(simulation.calculate(name, YEAR)[0]) / WEEKS
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
    hours=10, age=3, sibling_age=10, provider=0, sibling_provider=0, bill=350, share=300
)
@example(
    hours=35, age=3, sibling_age=0, provider=0, sibling_provider=1, bill=350, share=0
)
@example(
    hours=60, age=1, sibling_age=4, provider=1, sibling_provider=0, bill=0, share=50
)
@given(
    hours=st.integers(min_value=1, max_value=70),
    age=st.integers(min_value=0, max_value=12),
    sibling_age=st.integers(min_value=0, max_value=12),
    provider=st.integers(min_value=0, max_value=1),
    sibling_provider=st.integers(min_value=0, max_value=1),
    bill=st.integers(min_value=0, max_value=800),
    share=st.integers(min_value=0, max_value=600),
)
def test_a_sibling_with_no_hours_adds_nothing(
    hours, age, sibling_age, provider, sibling_provider, bill, share
):
    child = dict(age=age, hours=hours, provider=PROVIDERS[provider])
    sibling = dict(age=sibling_age, hours=0, provider=PROVIDERS[sibling_provider])
    alone, _, _ = vermont({"child": child}, bill, share)
    with_sibling, _, _ = vermont({"child": child, "sibling": sibling}, bill, share)
    assert with_sibling == pytest.approx(alone, abs=TOLERANCE)


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
