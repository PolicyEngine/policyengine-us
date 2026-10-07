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


def move_dependent_amounts_to_filer(person, period, amount):
    """Puts the tax unit dependents' `amount` on a filer's own column.

    Some states count dependents' income on their filers' return. When spouses
    file separately on one return, each column is a separate return, and a
    child's income that parents filing separately report goes on the return
    of the parent with the greater taxable income (26 U.S.C. 1(g)(5)(B); IRS
    Form 8814 instructions). The spouse whose own `amount` is greater takes
    the dependents' total, and an exact tie splits it equally, so the result
    does not depend on which spouse is labelled head. Without a spouse the
    head takes it. Dependents keep nothing of their own.
    """
    tax_unit = person.tax_unit
    is_dependent = person("is_tax_unit_dependent", period)
    is_head = person("is_tax_unit_head", period)
    is_spouse = person("is_tax_unit_spouse", period)
    dependents_amount = tax_unit.sum(is_dependent * amount)
    head_amount = tax_unit.sum(is_head * amount)
    spouse_amount = tax_unit.sum(is_spouse * amount)
    own = where(is_head, head_amount, spouse_amount)
    other = where(is_head, spouse_amount, head_amount)
    has_spouse = tax_unit.any(is_spouse)
    share = where(
        has_spouse,
        where(own > other, 1, where(own == other, 0.5, 0)),
        1,
    )
    filer_share = (is_head | is_spouse) * share
    return where(is_dependent, 0, amount) + filer_share * dependents_amount


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
