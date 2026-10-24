"""Non-spouse military survivor benefits stay in Michigan's tax base.

Each year uses one vectorized simulation of paired tax units. The pairs
share every input except increasing military survivor benefits, including
benefits paid to dependents. Seeded incomes span the retirement deduction
caps and ages span Michigan's retirement tiers. This catches an exemption
that incorrectly leaves taxable income flat as well as deductions that
incorrectly count taxable survivor benefits against another deduction.
"""

import numpy as np
import pytest

from policyengine_us import Simulation


SEED = 20261022
TOLERANCE = 0.05  # dollars; model calculations use float32 arrays
FILER_AGES = [20, 40, 59, 62, 65, 67, 70, 75, 80, 85]


def _draw_units(year):
    rng = np.random.default_rng(SEED + year)
    units = []
    for i in range(24):
        joint = i % 2 == 1

        def filer(age):
            return {
                "age": age,
                "employment_income": float(rng.integers(0, 80_001)),
                "taxable_private_pension_income": float(rng.integers(0, 100_001)),
                "military_retirement_pay": (
                    0.0 if i % 3 == 0 else float(rng.integers(0, 50_001))
                ),
                "taxable_interest_income": float(rng.integers(0, 20_001)),
                "retirement_benefits_from_ss_exempt_employment": (
                    10_000.0 if age >= 59 and i % 3 != 0 else 0.0
                ),
                "year_of_retirement": 2008 if i % 4 == 0 else 2018,
                "military_retirement_pay_survivors": float(rng.integers(0, 30_001)),
                # Unchanged pairs check that units cannot affect each other.
                "increment": 0.0 if i % 6 == 0 else float(rng.integers(1, 30_001)),
            }

        head = filer(FILER_AGES[i % len(FILER_AGES)])
        spouse = filer(FILER_AGES[(i + 3) % len(FILER_AGES)]) if joint else None
        dependents = [
            {
                "age": 8 + j * 4,
                "military_retirement_pay_survivors": float(rng.integers(0, 10_001)),
                "increment": 0.0 if i % 6 == 0 else float(rng.integers(1, 10_001)),
            }
            for j in range(i % 3)
        ]
        units.append({"head": head, "spouse": spouse, "dependents": dependents})

    # Guarantee a young filer above the zero floor, independently of the draw.
    units[0] = {
        "head": {
            "age": 20,
            "employment_income": 40_000.0,
            "military_retirement_pay_survivors": 0.0,
            "increment": 10_000.0,
        },
        "spouse": None,
        "dependents": [],
    }
    # This pair changes only a dependent's benefits, which belong on their
    # own return and must not change the filer's AGI or Michigan deductions.
    units[1]["head"]["increment"] = 0.0
    units[1]["spouse"]["increment"] = 0.0
    units[1]["dependents"][0]["increment"] = 10_000.0
    # Guarantee a pair whose small survivor increase remains below the tax
    # base's zero floor, alongside the positive-base example above.
    units[2]["head"] = {
        "age": 20,
        "employment_income": 0.0,
        "military_retirement_pay_survivors": 0.0,
        "increment": 1_000.0,
    }
    return units


def _paired_situation(units, year):
    people, tax_units, marital_units = {}, {}, {}
    households, families, spm_units = {}, {}, {}
    for increased in (False, True):
        for i, unit in enumerate(units):
            key = f"{int(increased)}_{i}"
            members, couple = [], []

            def add_person(role, record):
                name = f"{role}_{key}"
                members.append(name)
                person = {
                    variable: {year: amount}
                    for variable, amount in record.items()
                    if variable != "increment"
                }
                benefits = record["military_retirement_pay_survivors"]
                person["military_retirement_pay_survivors"] = {
                    year: benefits + increased * record["increment"]
                }
                person.update(
                    {
                        "is_surviving_spouse": {year: False},
                        "is_tax_unit_head": {year: role == "head"},
                        "is_tax_unit_spouse": {year: role == "spouse"},
                        "is_tax_unit_dependent": {year: role.startswith("dependent")},
                    }
                )
                people[name] = person
                return name

            couple.append(add_person("head", unit["head"]))
            if unit["spouse"] is not None:
                couple.append(add_person("spouse", unit["spouse"]))
            marital_units[f"couple_{key}"] = {"members": couple}
            for j, record in enumerate(unit["dependents"]):
                name = add_person(f"dependent_{j}", record)
                marital_units[f"dependent_{key}_{j}"] = {"members": [name]}
            tax_units[f"tax_unit_{key}"] = {"members": members}
            households[f"household_{key}"] = {
                "members": members,
                "state_name": {year: "MI"},
            }
            families[f"family_{key}"] = {"members": members}
            spm_units[f"spm_unit_{key}"] = {"members": members}
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        "households": households,
        "families": families,
        "spm_units": spm_units,
    }


@pytest.mark.parametrize("year", [2024, 2025, 2026])
def test_nonspouse_survivor_benefits_never_reduce_michigan_taxable_income(year):
    units = _draw_units(year)
    sim = Simulation(situation=_paired_situation(units, year))
    count = len(units)

    def paired(variable):
        amounts = sim.calculate(variable, year)
        return amounts[:count], amounts[count:]

    increments = np.array(
        [
            unit["head"]["increment"]
            + (unit["spouse"]["increment"] if unit["spouse"] is not None else 0)
            for unit in units
        ]
    )
    # Child benefits are excluded from the filer's federal AGI; every dollar
    # paid to the head or spouse is federally taxable on this return.
    agi_before, agi_after = paired("adjusted_gross_income")
    np.testing.assert_allclose(
        agi_after - agi_before, increments, rtol=0, atol=TOLERANCE
    )
    for variable in ("mi_subtractions", "mi_exemptions"):
        before, after = paired(variable)
        np.testing.assert_allclose(
            after,
            before,
            rtol=0,
            atol=TOLERANCE,
            err_msg=f"Non-spouse survivor benefits changed {variable}",
        )

    before, after = paired("mi_taxable_income")
    assert (after >= before - TOLERANCE).all()
    above_floor = before > TOLERANCE
    np.testing.assert_allclose(
        after[above_floor] - before[above_floor],
        increments[above_floor],
        rtol=0,
        atol=TOLERANCE,
        err_msg="Non-spouse benefits must increase a positive Michigan tax base",
    )
    unchanged_filer_income = increments == 0
    np.testing.assert_allclose(
        after[unchanged_filer_income],
        before[unchanged_filer_income],
        rtol=0,
        atol=TOLERANCE,
    )
    assert (above_floor & (increments > 0)).any()
    assert ((before == 0) & (after == 0) & (increments > 0)).any()
    assert unchanged_filer_income.any()
