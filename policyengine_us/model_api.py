from policyengine_us.variables.household.demographic.geographic.state_code import (
    StateCode,
)
from functools import reduce
from policyengine_core.model_api import *
from policyengine_us.entities import *
from policyengine_us.tools.general import *
from pathlib import Path
from policyengine_us.typing import *
import warnings
from policyengine_us.tools.cloning import get_stored_variables

warnings.filterwarnings("ignore")

REPO = Path(__file__).parent


def all_of_variables(variables: List[str]) -> Formula:
    def formula(entity, period, parameters):
        value = True
        for variable in variables:
            value = value & (add(entity, period, [variable]) > 0)
        return value

    return formula


def allocate_joint_amount_to_minimize_combined_tax(
    rate, head_income, spouse_income, total_allocable_amount
):
    best_head_allocation = total_allocable_amount
    best_tax = rate.calc(max_(head_income - best_head_allocation, 0)) + rate.calc(
        max_(spouse_income - (total_allocable_amount - best_head_allocation), 0)
    )

    for threshold in rate.thresholds:
        if not np.isfinite(threshold):
            continue

        for candidate in (
            np.clip(head_income - threshold, 0, total_allocable_amount),
            np.clip(
                total_allocable_amount - (spouse_income - threshold),
                0,
                total_allocable_amount,
            ),
        ):
            candidate_tax = rate.calc(max_(head_income - candidate, 0)) + rate.calc(
                max_(spouse_income - (total_allocable_amount - candidate), 0)
            )
            improves_tax = candidate_tax < (best_tax - 1e-9)
            best_tax = where(improves_tax, candidate_tax, best_tax)
            best_head_allocation = where(improves_tax, candidate, best_head_allocation)

    return best_head_allocation


STATES = [
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DC",
    "DE",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
    "PR",
    "VI",
]
