"""
Datasets can carry ``long_term_capital_loss_carryover`` or
``short_term_capital_loss_carryover`` as a person column. Each now adds two
leaves: the person's own carryover and one from a terminated estate or trust
(Schedule K-1 (Form 1041), box 11, codes D and C). Core does not uprate a
variable that adds others, so ``MICRODATA_UPRATING_OVERRIDES`` gives the sums
the series their leaves follow. A dataset carrying the sums must keep them in
every extended year and give the same results as one carrying the leaves.
"""

import numpy as np
import pandas as pd
import pytest
from policyengine_core.parameters.operations.get_parameter import get_parameter

from policyengine_us import Microsimulation
from policyengine_us.data.dataset_schema import USSingleYearDataset
from policyengine_us.system import system
from policyengine_us.tools.per_capita_uprating import per_capita_path

BASE_YEAR, LATER_YEAR = 2024, 2026
SERIES = {
    "long": per_capita_path("calibration.gov.irs.soi.long_term_capital_gains"),
    "short": per_capita_path("calibration.gov.irs.soi.short_term_capital_gains"),
}
# Per person: the carryover sums and the own part of each.
CARRYOVERS = {
    "long": ([3_000.0, 0.0, 1_200.0], [1_000.0, 0.0, 1_200.0]),
    "short": ([1_000.0, 0.0, 400.0], [0.0, 0.0, 100.0]),
}
OUTPUTS = [
    "az_property_tax_credit_capital_gains",
    "az_property_tax_credit_income",
    "az_property_tax_credit",
    "adjusted_gross_income",
    "income_tax",
]


def _dataset(carryover_columns: dict) -> USSingleYearDataset:
    """Two Arizona households: a renter aged 70 whose gains are net of
    carryovers, and a renter aged 68 with a dependent grandchild who has
    carryovers."""
    return USSingleYearDataset(
        person=pd.DataFrame(
            {
                "person_id": [1, 2, 3],
                "person_household_id": [1, 2, 2],
                "person_tax_unit_id": [1, 2, 2],
                "person_spm_unit_id": [1, 2, 2],
                "person_family_id": [1, 2, 2],
                "person_marital_unit_id": [1, 2, 3],
                "age": [70.0, 68.0, 15.0],
                "is_tax_unit_dependent": [False, False, True],
                "rent": [5_000.0, 6_000.0, 0.0],
                "employment_income": [0.0, 2_000.0, 0.0],
                # Schedule D lines 15 and 7, net of the carryovers.
                "long_term_capital_gains_before_response": [1_000.0, 0.0, -1_200.0],
                "short_term_capital_gains": [-500.0, 0.0, -400.0],
                **carryover_columns,
            }
        ),
        household=pd.DataFrame(
            {
                "household_id": [1, 2],
                "household_weight": [1.0, 1.0],
                "state_fips": [4, 4],
            }
        ),
        tax_unit=pd.DataFrame({"tax_unit_id": [1, 2]}),
        spm_unit=pd.DataFrame({"spm_unit_id": [1, 2]}),
        family=pd.DataFrame({"family_id": [1, 2]}),
        marital_unit=pd.DataFrame({"marital_unit_id": [1, 2, 3]}),
        time_period=BASE_YEAR,
    )


def _sums() -> dict:
    return {
        f"{term}_term_capital_loss_carryover": totals
        for term, (totals, _) in CARRYOVERS.items()
    }


def _leaves() -> dict:
    columns = {}
    for term, (totals, own) in CARRYOVERS.items():
        columns[f"own_{term}_term_capital_loss_carryover"] = own
        columns[f"estate_or_trust_{term}_term_capital_loss_carryover"] = [
            total - part for total, part in zip(totals, own)
        ]
    return columns


def _growth(path: str, year: int) -> float:
    parameter = get_parameter(system.parameters, path)
    return parameter(f"{year}-01-01") / parameter(f"{BASE_YEAR}-01-01")


@pytest.fixture(scope="module")
def simulations():
    return {
        name: Microsimulation(dataset=_dataset(columns), dataset_end_year=LATER_YEAR)
        for name, columns in [("sums", _sums()), ("leaves", _leaves())]
    }


@pytest.mark.parametrize("year", [BASE_YEAR, LATER_YEAR])
def test_carryover_sums_from_a_dataset_uprate_as_their_leaves(simulations, year):
    for term, (totals, _) in CARRYOVERS.items():
        expected = np.array(totals) * _growth(SERIES[term], year)
        for simulation in simulations.values():
            np.testing.assert_allclose(
                simulation.calculate(
                    f"{term}_term_capital_loss_carryover", year
                ).values,
                expected,
                rtol=1e-6,
            )


@pytest.mark.parametrize("year", [BASE_YEAR, LATER_YEAR])
def test_dataset_sums_and_leaves_give_the_same_results(simulations, year):
    for name in OUTPUTS:
        np.testing.assert_allclose(
            simulations["leaves"].calculate(name, year).values,
            simulations["sums"].calculate(name, year).values,
            atol=0.01,
            err_msg=name,
        )


def test_line_d_adds_back_dataset_carryovers(simulations):
    # ITR 12-1 item (7): the year's own result counts on line D. The first
    # renter: 1,000 + 3,000 - 500 + 1,000. The grandchild:
    # -1,200 + 1,200 - 400 + 400.
    for simulation in simulations.values():
        line_d = simulation.calculate("az_property_tax_credit_capital_gains", BASE_YEAR)
        np.testing.assert_allclose(line_d.values, [4_500, 0, 0], atol=0.01)
