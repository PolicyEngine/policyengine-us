"""Weighted OASDI accounting totals must count each entity's amount once.

``Microsimulation`` weights a tax unit by its first member's household weight.
``oasdi_income`` credits each tax unit's amount to that same household, so
household-weighted totals equal the independent Person and TaxUnit weighted
totals. This needs Python: YAML has no dataset loading or weights.

The fixture has five households with distinct, non-binary weights: households
with two tax units, a beneficiary couple who owe tax on benefits, wages above
the wage base, self-employment earnings, and one tax unit whose members live in
two households. That last unit separates the first-member credit from core's
group-to-group mapping, which splits a tax unit's amount by member count.
"""

import numpy as np
import pandas as pd
import pytest

from policyengine_us import Microsimulation
from policyengine_us.data.dataset_schema import USMultiYearDataset, USSingleYearDataset

YEAR = 2026
# Household ID, weight and members as (person ID, tax unit ID, inputs).
HOUSEHOLDS = (
    (
        11,
        1_130.5,
        (
            (
                101,
                21,
                dict(
                    age=72,
                    social_security_retirement=18_000.0,
                    taxable_interest_income=45_000.0,
                ),
            ),
            (102, 21, dict(age=70, social_security_retirement=14_000.0)),
            (103, 22, dict(age=40, employment_income=60_000.0)),
        ),
    ),
    (
        12,
        2_457.25,
        (
            (104, 23, dict(age=45, employment_income=260_000.0)),
            (105, 23, dict(age=44, self_employment_income=80_000.0)),
            (
                106,
                24,
                dict(
                    age=50,
                    employment_income=250_000.0,
                    taxable_interest_income=120_000.0,
                ),
            ),
        ),
    ),
    (
        13,
        397.75,
        (
            (
                107,
                25,
                dict(
                    age=68,
                    social_security_retirement=24_000.0,
                    taxable_interest_income=30_000.0,
                ),
            ),
            (
                108,
                26,
                dict(
                    age=40, employment_income=166_030.0, self_employment_income=20_000.0
                ),
            ),
        ),
    ),
    # Tax unit 27's first member lives in household 14, its second in 15.
    (
        14,
        1_750.125,
        (
            (
                109,
                27,
                dict(
                    age=69,
                    social_security_retirement=20_000.0,
                    taxable_interest_income=40_000.0,
                ),
            ),
        ),
    ),
    (
        15,
        3_003.5,
        (
            (110, 28, dict(age=40, employment_income=90_000.0)),
            (111, 27, dict(age=67, social_security_retirement=16_000.0)),
        ),
    ),
)
# Married couples share a marital unit; everyone else has their own.
MARITAL_UNIT = {102: 101, 105: 104}
INPUTS = (
    "age",
    "employment_income",
    "self_employment_income",
    "social_security_retirement",
    "taxable_interest_income",
)


def build_dataset():
    people, households, tax_unit_ids = [], [], []
    for household_id, weight, members in HOUSEHOLDS:
        households.append(
            {
                "household_id": household_id,
                "household_weight": weight,
                "state_fips": 48,
            }
        )
        for person_id, tax_unit_id, inputs in members:
            person = {name: 0.0 for name in INPUTS}
            person.update(inputs)
            person.update(
                person_id=person_id,
                person_household_id=household_id,
                person_tax_unit_id=tax_unit_id,
                person_spm_unit_id=household_id,
                person_family_id=household_id,
                person_marital_unit_id=MARITAL_UNIT.get(person_id, person_id),
            )
            people.append(person)
            if tax_unit_id not in tax_unit_ids:
                tax_unit_ids.append(tax_unit_id)
    people = pd.DataFrame(people)
    household_ids = [household["household_id"] for household in households]
    dataset = USSingleYearDataset(
        person=people,
        household=pd.DataFrame(households),
        tax_unit=pd.DataFrame(
            {
                "tax_unit_id": tax_unit_ids,
                # Keep optional itemized deductions out of the counterfactuals.
                "itemized_medical_expenses": 0.0,
                "salt_deduction": 0.0,
            }
        ),
        spm_unit=pd.DataFrame(
            {"spm_unit_id": household_ids, "takes_up_tanf_if_eligible": False}
        ),
        family=pd.DataFrame({"family_id": household_ids}),
        marital_unit=pd.DataFrame(
            {"marital_unit_id": people.person_marital_unit_id.unique()}
        ),
        time_period=YEAR,
    )
    return dataset, people, dict(zip(household_ids, households))


@pytest.fixture(scope="module")
def results():
    dataset, people, households = build_dataset()
    # Bypass automatic multi-year projection for this fixed-year fixture.
    sim = Microsimulation(dataset=USMultiYearDataset(datasets=[dataset]))
    out = {}
    for name in (
        "oasdi_payroll_tax_revenue",
        "oasdi_benefit_taxation_revenue",
        "oasdi_niit_revenue",
        "oasdi_income",
        "oasdi_cost",
        "oasdi_modeled_balance",
        "social_security",
        "person_id",
        "tax_unit_id",
        "household_id",
    ):
        calculated = sim.calculate(name, YEAR)
        out[name] = (np.asarray(calculated).copy(), np.asarray(calculated.weights))
    tob = out["oasdi_benefit_taxation_revenue"][0]
    out["projected_tob"] = sim.calculate(
        "oasdi_benefit_taxation_revenue", YEAR, map_to="person"
    )
    out["split_tax_unit_revenue"] = sim.map_result(
        tob + out["oasdi_niit_revenue"][0], "tax_unit", "household"
    )
    return out, people, households


def weighted(out, name):
    values, weights = out[name]
    return float(np.sum(values.astype(float) * weights))


def test_tax_units_carry_their_first_members_household_weight(results):
    out, people, households = results
    # Persons appear in dataset order; a tax unit's first member is its first
    # person in that order.
    first_household = people.groupby("person_tax_unit_id")[
        "person_household_id"
    ].first()
    tax_unit_ids = out["tax_unit_id"][0].astype(int)
    expected = [
        households[first_household[tax_unit_id]]["household_weight"]
        for tax_unit_id in tax_unit_ids
    ]
    np.testing.assert_array_equal(out["oasdi_niit_revenue"][1], expected)


def test_household_totals_match_independent_entity_totals(results):
    out, people, households = results
    payroll = weighted(out, "oasdi_payroll_tax_revenue")
    tob = weighted(out, "oasdi_benefit_taxation_revenue")
    niit = weighted(out, "oasdi_niit_revenue")
    income = weighted(out, "oasdi_income")
    cost = weighted(out, "oasdi_cost")
    assert income == pytest.approx(payroll + tob + niit, rel=1e-6)
    assert cost == pytest.approx(weighted(out, "social_security"), rel=1e-6)
    assert weighted(out, "oasdi_modeled_balance") == pytest.approx(
        income - cost, rel=1e-6
    )
    # The fixture exercises every term it checks.
    assert payroll > 0 and tob > 0 and cost > 0
    # Projecting tax-unit revenue to every member counts couples twice; the
    # fixture would detect that error.
    assert float(out["projected_tob"].sum()) > tob + 1


def test_each_household_holds_its_members_and_first_member_tax_units(results):
    out, people, households = results
    household_ids = out["household_id"][0].astype(int)
    person_household = dict(zip(people.person_id, people.person_household_id))
    first_household = people.groupby("person_tax_unit_id")[
        "person_household_id"
    ].first()
    expected = dict.fromkeys(household_ids, 0.0)
    payroll = out["oasdi_payroll_tax_revenue"][0]
    for person_id, value in zip(out["person_id"][0].astype(int), payroll):
        expected[person_household[person_id]] += float(value)
    tax_unit_revenue = (
        out["oasdi_benefit_taxation_revenue"][0] + out["oasdi_niit_revenue"][0]
    )
    for tax_unit_id, value in zip(out["tax_unit_id"][0].astype(int), tax_unit_revenue):
        expected[first_household[tax_unit_id]] += float(value)
    np.testing.assert_allclose(
        out["oasdi_income"][0],
        [expected[household_id] for household_id in household_ids],
        rtol=0,
        atol=0.01,
    )


def test_split_mapping_agrees_only_where_tax_units_nest_in_households(results):
    out, people, households = results
    household_ids = out["household_id"][0].astype(int)
    person_household = dict(zip(people.person_id, people.person_household_id))
    household_payroll = dict.fromkeys(household_ids, 0.0)
    for person_id, value in zip(
        out["person_id"][0].astype(int), out["oasdi_payroll_tax_revenue"][0]
    ):
        household_payroll[person_household[person_id]] += float(value)
    credited = out["oasdi_income"][0] - [
        household_payroll[household_id] for household_id in household_ids
    ]
    split = out["split_tax_unit_revenue"]
    nested = ~np.isin(household_ids, [14, 15])
    np.testing.assert_allclose(credited[nested], split[nested], rtol=0, atol=0.01)
    # Tax unit 27 spans households 14 and 15: splitting it by member count
    # moves half of its revenue to a household with another weight.
    assert not np.allclose(credited[~nested], split[~nested], rtol=0, atol=0.01)
    weights = out["oasdi_income"][1]
    tax_unit_total = weighted(out, "oasdi_benefit_taxation_revenue") + weighted(
        out, "oasdi_niit_revenue"
    )
    assert float(np.sum(credited * weights)) == pytest.approx(tax_unit_total, rel=1e-6)
    assert float(np.sum(split * weights)) != pytest.approx(tax_unit_total, rel=1e-6)
