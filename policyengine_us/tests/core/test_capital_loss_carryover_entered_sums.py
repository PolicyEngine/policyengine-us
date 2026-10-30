"""A capital loss carryover sum entered as an input is filed as the person's
own carryover when a Simulation is built, as employment_income is filed as
employment_income_before_lsr (``policyengine_us.system``). YAML tests build
Core simulations, which skip that step, so these run through
``policyengine_us.Simulation``.

Invariants:

1. Uprating: a sum entered for 2024 grows to later years by the series its
   leaves follow, as it did when the sum was an uprated input, and gives the
   same results as entering the person's own carryover for 2024.
2. People: a sum entered for one person leaves another person's leaves for
   the same year alone.
3. Replacement: a nonzero sum entered for a person replaces the leaves entered
   for that person for the same year; a zero sum leaves them.
"""

import numpy as np
import pytest
from policyengine_core.parameters.operations.get_parameter import get_parameter

from policyengine_us import Simulation
from policyengine_us.system import system
from policyengine_us.tools.per_capita_uprating import per_capita_path

BASE_YEAR, LATER_YEARS = 2024, (2025, 2026, 2030)
TERMS = {
    "long": per_capita_path("calibration.gov.irs.soi.long_term_capital_gains"),
    "short": per_capita_path("calibration.gov.irs.soi.short_term_capital_gains"),
}


def _growth(path, year):
    parameter = get_parameter(system.parameters, path)
    return parameter(f"{year}-01-01") / parameter(f"{BASE_YEAR}-01-01")


def _renter(carryovers: dict, year=BASE_YEAR) -> dict:
    """An Arizona renter aged 70 whose gains are net of the carryovers."""
    person = {
        "age": {year: 70},
        "rent": {year: 5_000},
        "long_term_capital_gains": {year: 1_000},
        "short_term_capital_gains": {year: -500},
    }
    person.update({name: {year: amount} for name, amount in carryovers.items()})
    return {
        "people": {"head": person},
        "tax_units": {"tax_unit": {"members": ["head"]}},
        "households": {"household": {"members": ["head"], "state_code": {year: "AZ"}}},
    }


@pytest.mark.parametrize("term", TERMS)
def test_entered_sum_uprates_as_its_own_leaf(term):
    sum_entered = Simulation(
        situation=_renter({f"{term}_term_capital_loss_carryover": 3_000})
    )
    own_entered = Simulation(
        situation=_renter({f"own_{term}_term_capital_loss_carryover": 3_000})
    )
    for year in LATER_YEARS:
        np.testing.assert_allclose(
            sum_entered.calculate(f"{term}_term_capital_loss_carryover", year),
            [3_000 * _growth(TERMS[term], year)],
            rtol=1e-6,
        )
        for name in [
            f"{term}_term_capital_loss_carryover",
            "az_property_tax_credit_capital_gains",
            "az_property_tax_credit",
            "capital_gains_28_percent_rate_gain",
            "income_tax",
        ]:
            np.testing.assert_array_equal(
                sum_entered.calculate(name, year),
                own_entered.calculate(name, year),
                err_msg=f"{name} {year}",
            )
    # The sum is no longer an input; the own leaf holds it.
    assert f"{term}_term_capital_loss_carryover" not in sum_entered.input_variables
    assert f"own_{term}_term_capital_loss_carryover" in sum_entered.input_variables


@pytest.mark.parametrize("term", TERMS)
def test_entered_sum_leaves_other_peoples_leaves(term):
    year = str(BASE_YEAR)
    simulation = Simulation(
        situation={
            "people": {
                "head": {
                    "age": {year: 40},
                    f"{term}_term_capital_loss_carryover": {year: 1_000},
                },
                "spouse": {
                    "age": {year: 40},
                    f"estate_or_trust_{term}_term_capital_loss_carryover": {
                        year: 2_000
                    },
                },
                "child": {
                    "age": {year: 10},
                    f"own_{term}_term_capital_loss_carryover": {year: 300},
                },
            }
        }
    )
    np.testing.assert_array_equal(
        simulation.calculate(f"{term}_term_capital_loss_carryover", year),
        [1_000, 2_000, 300],
    )


@pytest.mark.parametrize("term", TERMS)
def test_entered_sum_replaces_the_persons_leaves(term):
    year = str(BASE_YEAR)
    leaves = {
        f"own_{term}_term_capital_loss_carryover": {year: 1_000},
        f"estate_or_trust_{term}_term_capital_loss_carryover": {year: 500},
    }
    simulation = Simulation(
        situation={
            "people": {
                "replaced": {
                    "age": {year: 40},
                    f"{term}_term_capital_loss_carryover": {year: 4_000},
                    **leaves,
                },
                "kept": {
                    "age": {year: 40},
                    f"{term}_term_capital_loss_carryover": {year: 0},
                    **leaves,
                },
            }
        }
    )
    for name, expected in [
        (f"{term}_term_capital_loss_carryover", [4_000, 1_500]),
        (f"own_{term}_term_capital_loss_carryover", [4_000, 1_000]),
        (f"estate_or_trust_{term}_term_capital_loss_carryover", [0, 500]),
    ]:
        np.testing.assert_array_equal(
            simulation.calculate(name, year), expected, err_msg=name
        )
