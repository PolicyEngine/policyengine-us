"""Hypothesis coverage of Schedule M's person-level subtraction limits.

The 2025 IT-140 Schedule M line 47, boxes (c) and (d), first caps the income
remaining after the modified income receipts on lines 35-46 at $8,000, then
subtracts the person's own lines 29-34 modifications. These properties
exercise combinations that the worked YAML examples do not enumerate,
using the real model and independent
conservation and spouse-isolation checks.

Only income receipts enter the excluded Schedule M amounts. Section
11-21-12a independently authorizes the line 39 contribution deduction in
addition to the section 11-21-12(c) modifications. Contributions are outside the income-conservation property below; their
independence from the senior modification is covered by the variable YAML
tests.

Fresh two- or four-person simulations reuse the package's reference model;
they do not share simulation caches, mutate parameters, or load datasets.
"""

import numpy as np
from hypothesis import example, given, settings, strategies as st

from policyengine_us import Simulation

YEAR = 2025
CAP = 8_000
DEDUCTION = "wv_senior_citizen_disability_deduction_person"
MODIFICATION_SOURCES = (
    "us_govt_interest_person",
    "military_retirement_pay",
    "wv_public_pension_subtraction_person",
    "wv_social_security_benefits_subtraction_person",
)
EXCLUDED_SOURCES = (
    "military_service_income",
    "salt_refund_income",
)

AGIS = st.integers(min_value=-20_000, max_value=60_000)
AMOUNTS = st.integers(min_value=0, max_value=20_000)
MODIFICATIONS = st.tuples(*(AMOUNTS for _ in MODIFICATION_SOURCES))
EXCLUSIONS = st.tuples(*(AMOUNTS for _ in EXCLUDED_SOURCES))
PERSON = st.tuples(AGIS, MODIFICATIONS, EXCLUSIONS)
COUPLE = st.tuples(PERSON, PERSON)
PROPERTY_SETTINGS = settings(max_examples=50, deadline=None, derandomize=True)
ZERO_MODIFICATIONS = (0, 0, 0, 0)
ZERO_EXCLUSIONS = (0, 0)
LOW_INCOME_COUPLE = (
    (6_000, ZERO_MODIFICATIONS, ZERO_EXCLUSIONS),
    (6_000, ZERO_MODIFICATIONS, ZERO_EXCLUSIONS),
)


def _simulation(*couples):
    """Build independent joint returns, preserving each source's ownership."""
    people, tax_units, households = {}, {}, {}
    for couple_index, couple in enumerate(couples):
        members = []
        for person_index, (agi, modifications, exclusions) in enumerate(couple):
            name = f"person_{couple_index}_{person_index}"
            members.append(name)
            values = {
                "age": {YEAR: 66},
                "adjusted_gross_income_person": {YEAR: agi},
                "is_tax_unit_head": {YEAR: person_index == 0},
                "is_tax_unit_spouse": {YEAR: person_index == 1},
            }
            for source, amount in zip(MODIFICATION_SOURCES, modifications):
                values[source] = {YEAR: amount}
            for source, amount in zip(EXCLUDED_SOURCES, exclusions):
                values[source] = {YEAR: amount}
            people[name] = values
        tax_units[f"tax_unit_{couple_index}"] = {
            "members": members,
            "filing_status": {YEAR: "JOINT"},
        }
        households[f"household_{couple_index}"] = {
            "members": members,
            "state_code": {YEAR: "WV"},
        }
    return Simulation(
        situation={
            "people": people,
            "tax_units": tax_units,
            "households": households,
        }
    )


@PROPERTY_SETTINGS
@given(couple=COUPLE)
def test_each_persons_modification_is_between_zero_and_cap(couple):
    deduction = _simulation(couple).calculate(DEDUCTION, YEAR)
    assert np.all(deduction >= 0)
    assert np.all(deduction <= CAP)


@PROPERTY_SETTINGS
@given(
    agis=st.tuples(AGIS, AGIS),
    modifications=st.tuples(MODIFICATIONS, MODIFICATIONS),
)
def test_without_excluded_amounts_matches_previous_formula(agis, modifications):
    couple = tuple(
        (agi, person_modifications, ZERO_EXCLUSIONS)
        for agi, person_modifications in zip(agis, modifications)
    )
    deduction = _simulation(couple).calculate(DEDUCTION, YEAR)
    # The pre-fix formula is a compatibility reference only for this domain.
    previous = np.maximum(
        0,
        np.minimum(CAP, np.asarray(agis)) - np.sum(modifications, axis=1),
    )
    np.testing.assert_array_equal(deduction, previous)


@PROPERTY_SETTINGS
@given(couple=COUPLE)
@example(
    couple=(
        (6_000, ZERO_MODIFICATIONS, (0, 2_000)),
        (6_000, ZERO_MODIFICATIONS, ZERO_EXCLUSIONS),
    )
)
@example(
    couple=(
        (6_000, ZERO_MODIFICATIONS, (2_000, 0)),
        (6_000, ZERO_MODIFICATIONS, ZERO_EXCLUSIONS),
    )
)
def test_senior_and_other_subtractions_do_not_exceed_income_or_other_subtractions(
    couple,
):
    deduction = _simulation(couple).calculate(DEDUCTION, YEAR)
    # Sum each person's independently supplied modified income receipts,
    # without using the deduction formula or its intermediate totals.
    # A 529 contribution is a payment, so it does not enter this bound.
    subtractions = np.array(
        [
            sum(modifications) + sum(exclusions)
            for _, modifications, exclusions in couple
        ]
    )
    agis = np.array([agi for agi, _, _ in couple])
    assert np.all(deduction + subtractions <= np.maximum(agis, subtractions))


@PROPERTY_SETTINGS
@given(
    couple=COUPLE,
    changed_person=st.integers(min_value=0, max_value=1),
    source_index=st.integers(min_value=0, max_value=len(EXCLUDED_SOURCES) - 1),
    increase=st.integers(min_value=1, max_value=8_000),
)
@example(couple=LOW_INCOME_COUPLE, changed_person=0, source_index=0, increase=2_000)
@example(couple=LOW_INCOME_COUPLE, changed_person=1, source_index=0, increase=2_000)
@example(couple=LOW_INCOME_COUPLE, changed_person=0, source_index=1, increase=2_000)
@example(couple=LOW_INCOME_COUPLE, changed_person=1, source_index=1, increase=2_000)
def test_changing_one_spouses_excluded_amount_preserves_the_others_modification(
    couple, changed_person, source_index, increase
):
    agi, modifications, exclusions = couple[changed_person]
    changed_exclusions = list(exclusions)
    changed_exclusions[source_index] += increase
    changed_couple = list(couple)
    changed_couple[changed_person] = (agi, modifications, tuple(changed_exclusions))
    # Paired joint returns in one simulation also check vectorized isolation.
    deduction = _simulation(couple, changed_couple).calculate(DEDUCTION, YEAR)
    other_person = 1 - changed_person
    assert deduction[other_person] == deduction[2 + other_person]
    assert deduction[2 + changed_person] <= deduction[changed_person]
