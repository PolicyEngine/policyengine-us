"""Nebraska's child care subsidy pays only for the children the program covers.

392 NAC 1-001.04 and 2-004(E) limit the Child Care Subsidy program to the care
of children age 12 or younger and of children age 18 or younger with a special
need. 392 NAC 2-004(H) and 3-001.02(C) require an approved, enrolled provider,
and 3-004.01 pays the lesser of the provider's charge and the Department's
maximum rate.

Properties 1 and 2 cover the provider-rate model, which starts October 1, 2025.
Each fixes the family fee, treats the family as otherwise eligible and gives
every member under 18 the same monthly share of the bill, since the model splits
the bill evenly among members under 18. Before October 1, 2025, the model
approximates the payment from the bill and checks no provider.

1. A member the program doesn't cover, such as a teenager without a special
   need, a child with no provider or an adult, adds nothing to the payment,
   whatever that member's age, the covered child's care schedule or the family
   fee.
2. The payment never falls below zero or exceeds the bills of the children the
   program covers. With no care schedule and no family fee, the rate matrix
   prices nothing, and the payment equals those bills.
3. Before and after October 1, 2025, a lone child with a special need gets the
   same payment at 18 as at 17. The model gives an 18-year-old no share of the
   bill, so the child takes the part that no member received.
"""

import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01
# Providers that take a daily rate. A license-exempt in-home provider takes an
# hourly rate and needs a minimum number of children, so it is left out here.
PROVIDERS = ["CENTER", "HOME_I_II", "LICENSE_EXEMPT_FAMILY_HOME"]
BASE_AGE_LIMIT = 12
SPECIAL_NEEDS_AGE_LIMIT = 18


def nebraska(children, monthly_bill, monthly_fee, year=2026):
    """January payment for an SPM unit of one parent and these children."""
    month = f"{year}-01"
    members = ["parent", *children]
    people = {"parent": {"age": {year: 30}}}
    for name, child in children.items():
        person = {
            "age": {year: child["age"]},
            "is_tax_unit_dependent": {year: True},
            "ne_dhhs_has_special_needs": {year: child["special_needs"]},
            "childcare_attending_days_per_month": {year: child["days"]},
            "ne_child_care_subsidy_provider_type": {month: child["provider"]},
        }
        if "in_school" in child:
            person["is_in_k12_school"] = {year: child["in_school"]}
        people[name] = person
    situation = {
        "people": people,
        "tax_units": {"tax_unit": {"members": members}},
        "spm_units": {
            "spm_unit": {
                "members": members,
                "ne_child_care_subsidy_eligible": {month: True},
                "ne_child_care_subsidy_family_fee": {month: monthly_fee},
                "spm_unit_pre_subsidy_childcare_expenses": {year: monthly_bill * 12},
            }
        },
        "families": {"family": {"members": members}},
        "marital_units": {"marital_unit": {"members": ["parent"]}},
        "households": {"household": {"members": members, "state_name": {year: "NE"}}},
    }
    simulation = Simulation(situation=situation)
    return float(simulation.calculate("ne_child_care_subsidy", month)[0])


def equal_shares(children, monthly_share):
    """The monthly bill that gives each member under 18 this share."""
    return monthly_share * sum(child["age"] < 18 for child in children.values())


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
# Adults past the age limit: 18 or older without a special need, or 19 or
# older with one.
adults = st.one_of(
    st.fixed_dictionaries(
        dict(
            age=st.integers(min_value=18, max_value=22),
            special_needs=st.just(False),
            days=st.integers(min_value=0, max_value=23),
            provider=st.sampled_from([*PROVIDERS, "NONE"]),
        )
    ),
    st.fixed_dictionaries(
        dict(
            age=st.integers(min_value=SPECIAL_NEEDS_AGE_LIMIT + 1, max_value=22),
            special_needs=st.just(True),
            days=st.integers(min_value=0, max_value=23),
            provider=st.sampled_from([*PROVIDERS, "NONE"]),
        )
    ),
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
# monthly shares; the same with no schedule; a sibling with no provider; an
# 18-year-old without a special need and a 19-year-old with one.
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
@example(
    child=dict(age=12, special_needs=False, days=0, provider="CENTER"),
    other=dict(age=18, special_needs=False, days=0, provider="CENTER"),
    share=1_000,
    fee=0,
)
@example(
    child=dict(age=0, special_needs=False, days=0, provider="CENTER"),
    other=dict(age=19, special_needs=True, days=0, provider="CENTER"),
    share=1_000,
    fee=0,
)
@given(
    child=covered_children,
    other=st.one_of(teenagers, children_without_provider, adults),
    share=st.integers(min_value=0, max_value=2_000),
    fee=st.integers(min_value=0, max_value=500),
)
def test_a_member_the_program_does_not_cover_adds_nothing(child, other, share, fee):
    alone = {"child": child}
    with_other = {"child": child, "other": other}
    paid_alone = nebraska(alone, equal_shares(alone, share), fee)
    paid_with_other = nebraska(with_other, equal_shares(with_other, share), fee)
    assert paid_with_other == pytest.approx(paid_alone, abs=TOLERANCE)


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
    paid = nebraska(named, equal_shares(named, share), fee)
    covered_bills = share * sum(covered(child) for child in children)
    assert paid >= -TOLERANCE
    assert paid <= covered_bills + TOLERANCE
    if fee == 0 and all(child["days"] == 0 for child in children):
        assert paid == pytest.approx(covered_bills, abs=TOLERANCE)


@settings(max_examples=15, deadline=None)
# A $1,000 monthly bill with no schedule in each period, and a priced schedule
# with a fee.
@example(year=2025, days=0, provider="CENTER", bill=1_000, fee=0)
@example(year=2026, days=0, provider="CENTER", bill=1_000, fee=0)
@example(year=2026, days=21, provider="HOME_I_II", bill=1_000, fee=100)
@given(
    year=st.sampled_from([2025, 2026]),
    days=st.integers(min_value=0, max_value=23),
    provider=st.sampled_from(PROVIDERS),
    bill=st.integers(min_value=0, max_value=2_000),
    fee=st.integers(min_value=0, max_value=500),
)
def test_a_child_with_a_special_need_gets_the_same_payment_at_18(
    year, days, provider, bill, fee
):
    def lone_child(age):
        # Both ages attend school, so they share the school-age rates.
        child = dict(
            age=age, special_needs=True, days=days, provider=provider, in_school=True
        )
        return nebraska({"child": child}, bill, fee, year)

    assert lone_child(18) == pytest.approx(lone_child(17), abs=TOLERANCE)
