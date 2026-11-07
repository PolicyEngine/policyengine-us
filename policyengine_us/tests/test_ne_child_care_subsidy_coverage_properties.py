"""Nebraska's child care subsidy pays only for the children the program covers.

392 NAC 1-001.04 and 2-004(E) limit the Child Care Subsidy program to the care
of children age 12 or younger and of children age 18 or younger with a special
need. 392 NAC 2-004(H) and 3-001.02(C) require an approved, enrolled provider,
and 3-004.01 pays the lesser of the provider's charge and the Department's
maximum rate.

1. A member the program doesn't cover, a teenager without a special need or a
   child with no provider, adds nothing to the payment, whatever that member's
   bill share, the covered child's care schedule or the family fee.
2. The payment never falls below zero or exceeds the bills of the children the
   program covers. With no care schedule and no family fee, the rate matrix
   prices nothing, and the payment equals those bills.

Each child carries the same monthly bill share: the SPM unit's bill is that
share times the number of children, which the model splits evenly among
members under 18.
"""

import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEAR = 2026
MONTH = f"{YEAR}-01"
TOLERANCE = 0.01
# Providers that take a daily rate. A license-exempt in-home provider takes an
# hourly rate and needs a minimum number of children, so it is left out here.
PROVIDERS = ["CENTER", "HOME_I_II", "LICENSE_EXEMPT_FAMILY_HOME"]
BASE_AGE_LIMIT = 12
SPECIAL_NEEDS_AGE_LIMIT = 18


def nebraska(children, monthly_share, monthly_fee):
    """January payment for an SPM unit of one parent and these children."""
    members = ["parent", *children]
    people = {"parent": {"age": {YEAR: 30}}}
    for name, child in children.items():
        people[name] = {
            "age": {YEAR: child["age"]},
            "is_tax_unit_dependent": {YEAR: True},
            "ne_dhhs_has_special_needs": {YEAR: child["special_needs"]},
            "childcare_attending_days_per_month": {YEAR: child["days"]},
            "ne_child_care_subsidy_provider_type": {MONTH: child["provider"]},
        }
    situation = {
        "people": people,
        "tax_units": {"tax_unit": {"members": members}},
        "spm_units": {
            "spm_unit": {
                "members": members,
                "ne_child_care_subsidy_eligible": {MONTH: True},
                "ne_child_care_subsidy_family_fee": {MONTH: monthly_fee},
                "spm_unit_pre_subsidy_childcare_expenses": {
                    YEAR: monthly_share * 12 * len(children)
                },
            }
        },
        "families": {"family": {"members": members}},
        "marital_units": {"marital_unit": {"members": ["parent"]}},
        "households": {"household": {"members": members, "state_name": {YEAR: "NE"}}},
    }
    simulation = Simulation(situation=situation)
    return float(simulation.calculate("ne_child_care_subsidy", MONTH)[0])


def covered(child):
    """Whether the rules cover the child: age limit and an approved provider."""
    age_eligible = child["age"] <= BASE_AGE_LIMIT or (
        child["special_needs"] and child["age"] <= SPECIAL_NEEDS_AGE_LIMIT
    )
    return age_eligible and child["provider"] != "NONE"


covered_children = st.fixed_dictionaries(
    dict(
        age=st.integers(min_value=0, max_value=BASE_AGE_LIMIT),
        special_needs=st.booleans(),
        days=st.integers(min_value=0, max_value=23),
        provider=st.sampled_from(PROVIDERS),
    )
)
teenagers = st.fixed_dictionaries(
    dict(
        age=st.integers(min_value=BASE_AGE_LIMIT + 1, max_value=17),
        special_needs=st.just(False),
        days=st.integers(min_value=0, max_value=23),
        provider=st.sampled_from([*PROVIDERS, "NONE"]),
    )
)
children_without_provider = st.fixed_dictionaries(
    dict(
        age=st.integers(min_value=0, max_value=17),
        special_needs=st.booleans(),
        days=st.integers(min_value=0, max_value=23),
        provider=st.just("NONE"),
    )
)
any_children = st.fixed_dictionaries(
    dict(
        age=st.integers(min_value=0, max_value=17),
        special_needs=st.booleans(),
        days=st.integers(min_value=0, max_value=23),
        provider=st.sampled_from([*PROVIDERS, "NONE"]),
    )
)


@settings(max_examples=15, deadline=None)
# A 3-year-old in 21 days of center care with a 15-year-old sibling and $1,000
# monthly shares; the same with no schedule; a sibling with no provider.
@example(
    child=dict(age=3, special_needs=False, days=21, provider="CENTER"),
    other=dict(age=15, special_needs=False, days=0, provider="CENTER"),
    share=1_000,
    fee=0,
)
@example(
    child=dict(age=3, special_needs=False, days=0, provider="CENTER"),
    other=dict(age=13, special_needs=False, days=10, provider="HOME_I_II"),
    share=1_000,
    fee=50,
)
@example(
    child=dict(age=8, special_needs=True, days=12, provider="HOME_I_II"),
    other=dict(age=5, special_needs=False, days=21, provider="NONE"),
    share=600,
    fee=0,
)
@given(
    child=covered_children,
    other=st.one_of(teenagers, children_without_provider),
    share=st.integers(min_value=0, max_value=2_000),
    fee=st.integers(min_value=0, max_value=500),
)
def test_a_member_the_program_does_not_cover_adds_nothing(child, other, share, fee):
    alone = nebraska({"child": child}, share, fee)
    with_other = nebraska({"child": child, "other": other}, share, fee)
    assert with_other == pytest.approx(alone, abs=TOLERANCE)


@settings(max_examples=20, deadline=None)
# No schedule and no fee: the fallback pays every covered child's share and
# nothing for the rest.
@example(
    children=[
        dict(age=3, special_needs=False, days=0, provider="CENTER"),
        dict(age=15, special_needs=True, days=0, provider="CENTER"),
        dict(age=15, special_needs=False, days=0, provider="CENTER"),
    ],
    share=1_000,
    fee=0,
)
@example(
    children=[dict(age=10, special_needs=False, days=0, provider="NONE")],
    share=800,
    fee=0,
)
@given(
    children=st.lists(any_children, min_size=1, max_size=3),
    share=st.integers(min_value=0, max_value=2_000),
    fee=st.integers(min_value=0, max_value=500),
)
def test_the_payment_stays_within_the_covered_childrens_bills(children, share, fee):
    named = {f"child_{i}": child for i, child in enumerate(children)}
    paid = nebraska(named, share, fee)
    covered_bills = share * sum(covered(child) for child in children)
    assert paid >= -TOLERANCE
    assert paid <= covered_bills + TOLERANCE
    if fee == 0 and all(child["days"] == 0 for child in children):
        assert paid == pytest.approx(covered_bills, abs=TOLERANCE)
