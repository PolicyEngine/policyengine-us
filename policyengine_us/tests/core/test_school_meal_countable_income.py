"""Check school meal income with generated households and model calculations."""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation


YEAR = 2026
BUSINESS_SOURCES = (
    "self_employment_income",
    "sstb_self_employment_income",
    "rental_income",
    "farm_operations_income",
    "farm_rent_income",
    "partnership_s_corp_income",
    "estate_income",
)
ADDED_CASH_SOURCES = (
    "alimony_income",
    "workers_compensation",
    "disability_benefits",
    "military_retirement_pay",
    "military_retirement_pay_survivors",
)
LEGACY_PERSON_SOURCES = (
    "employment_income",
    "self_employment_income",
    "sstb_self_employment_income",
    "dividend_income",
    "interest_income",
    "gi_cash_assistance",
    "child_support_received",
    "social_security",
    "ssi",
    "general_assistance",
    "pension_income",
    "survivor_benefits",
    "financial_assistance",
    "miscellaneous_income",
    "veterans_benefits",
    "total_unemployment_compensation",
    "strike_benefits",
    "rental_income",
    "retirement_distributions",
)
SETTINGS = dict(
    max_examples=6,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


def _income(units, variable="school_meal_countable_income"):
    people = {}
    groups = {
        "families": {},
        "tax_units": {},
        "spm_units": {},
        "marital_units": {},
        "households": {},
    }
    for unit_index, unit in enumerate(units):
        members = []
        for person_index, inputs in enumerate(unit["people"]):
            name = f"person_{unit_index}_{person_index}"
            members.append(name)
            values = {"age": 35, "ssi": 0, **inputs}
            people[name] = {source: {YEAR: value} for source, value in values.items()}
            groups["marital_units"][name] = {"members": [name]}
        for entity in ("families", "tax_units"):
            groups[entity][str(unit_index)] = {"members": members}
        groups["spm_units"][str(unit_index)] = {
            "members": members,
            "tanf": {YEAR: unit.get("tanf", 0)},
        }
        groups["households"][str(unit_index)] = {
            "members": members,
            "state_code": {YEAR: "TN"},
        }
    simulation = Simulation(situation={"people": people, **groups})
    return np.asarray(simulation.calculate(variable, YEAR), dtype=float)


amounts = st.integers(0, 20_000)
business_people = st.fixed_dictionaries(
    {
        "employment_income": amounts,
        **{source: st.integers(-20_000, 20_000) for source in BUSINESS_SOURCES},
    }
)


@settings(**SETTINGS)
@given(
    st.lists(st.lists(business_people, min_size=1, max_size=3), min_size=1, max_size=4)
)
def test_business_losses_cannot_offset_any_person_or_income_source(households):
    actual = _income([{"people": people} for people in households])
    wages = np.array(
        [sum(person["employment_income"] for person in people) for people in households]
    )
    business = np.array(
        [
            sum(
                max(person[source], 0)
                for person in people
                for source in BUSINESS_SOURCES
            )
            for people in households
        ]
    )
    np.testing.assert_allclose(actual, wages + business, atol=0.01)
    assert np.all(actual >= wages)


@settings(**SETTINGS)
@given(
    source=st.sampled_from(ADDED_CASH_SOURCES),
    wages=amounts,
    initial=amounts,
    increase=st.integers(1, 20_000),
)
def test_increasing_included_cash_increases_income_by_the_same_amount(
    source, wages, initial, increase
):
    actual = _income(
        [
            {"people": [{"employment_income": wages, source: initial}]},
            {"people": [{"employment_income": wages, source: initial + increase}]},
        ]
    )
    np.testing.assert_allclose(actual, [wages + initial, wages + initial + increase])
    assert actual[1] - actual[0] == increase


@settings(**SETTINGS)
@given(
    st.lists(
        st.fixed_dictionaries(
            {"employment_income": amounts, "educational_assistance": amounts}
        ),
        min_size=1,
        max_size=4,
    )
)
def test_educational_assistance_does_not_change_school_meal_income(people):
    without_aid = [{**person, "educational_assistance": 0} for person in people]
    actual = _income([{"people": without_aid}, {"people": people}])
    expected = sum(person["employment_income"] for person in people)
    np.testing.assert_allclose(actual, [expected, expected], atol=0.01)


@settings(**SETTINGS)
@given(
    people=st.lists(
        st.fixed_dictionaries({source: amounts for source in LEGACY_PERSON_SOURCES}),
        min_size=1,
        max_size=3,
    ),
    tanf=amounts,
)
def test_unchanged_sources_keep_the_income_sum_from_main(people, tanf):
    # Sum the original person sources and add the SPM unit's TANF grant once.
    expected = sum(sum(person.values()) for person in people) + tanf
    actual = _income([{"people": people, "tanf": tanf}])
    np.testing.assert_allclose(actual, [expected], atol=0.01)


@settings(**SETTINGS)
@given(
    people=st.lists(
        st.fixed_dictionaries(
            {
                **{source: amounts for source in LEGACY_PERSON_SOURCES},
                "educational_assistance": amounts,
                **{source: st.integers(-20_000, 20_000) for source in BUSINESS_SOURCES},
                **{source: amounts for source in ADDED_CASH_SOURCES},
            }
        ),
        min_size=1,
        max_size=3,
    ),
    tanf=amounts,
)
def test_ancillary_income_measures_keep_the_original_source_sum(people, tanf):
    expected = (
        sum(
            sum(person[source] for source in LEGACY_PERSON_SOURCES)
            + person["educational_assistance"]
            for person in people
        )
        + tanf
    )
    for variable in (
        "csfp_countable_income",
        "tx_dta_csfp_countable_income",
        "ca_cvrp_countable_income",
    ):
        actual = _income([{"people": people, "tanf": tanf}], variable)
        np.testing.assert_allclose(actual, [expected], atol=0.01)
