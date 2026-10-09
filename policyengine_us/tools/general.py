from policyengine_core.model_api import *
from policyengine_core.projectors import Projector
from policyengine_us.entities import *
from policyengine_us.tools.branched_simulation import BranchedSimulation
from policyengine_us.tools.period_branch import (
    get_branch_for_period,
    get_override_branch,
)
from pathlib import Path
import pandas as pd
from policyengine_us.typing import Formula

USD = "currency-USD"


def tax_unit_non_dep_sum(var, tax_unit, period):
    return tax_unit.sum(
        tax_unit.members(var, period)
        * not_(tax_unit.members("is_tax_unit_dependent", period))
    )


def tax_unit_non_dep_add(tax_unit, period, variables, include_dependents=()):
    """
    Add variables over a tax unit's head and spouse, leaving out dependents.

    Like `add`, but a person-level variable is summed only over members who
    are not tax unit dependents, whose items belong on their own returns
    (irs_gross_income leaves them out of the filer's federal AGI the same
    way). Person-level variables named in `include_dependents` are summed
    over every member: they are the filer's amounts even when recorded on a
    dependent. A variable of any other entity falls back to `add`, so a
    tax-unit-level variable is added as is and must already describe the
    filer's own return. Variables are added in the order given.
    """
    if tax_unit.entity.key != "tax_unit":
        raise ValueError(
            f"tax_unit_non_dep_add needs a tax unit, not a {tax_unit.entity.key}."
        )
    # float32 like the model's values, so the sum rounds as `add`'s does.
    total = np.zeros(tax_unit.count, dtype=np.float32)
    # A person.tax_unit projector reports the underlying tax-unit count,
    # but its calculations and sums return one value per person.
    if isinstance(tax_unit, Projector):
        total = tax_unit.transform_and_bubble_up(total)
    for variable in variables:
        variable_entity = tax_unit.entity.get_variable(
            variable, check_existence=True
        ).entity
        if not variable_entity.is_person:
            total = total + add(tax_unit, period, [variable])
        elif variable in include_dependents:
            total = total + tax_unit.sum(tax_unit.members(variable, period))
        else:
            total = total + tax_unit_non_dep_sum(variable, tax_unit, period)
    return total


def person_share_of_tax_unit_amount(
    person,
    period,
    tax_unit_variable,
    person_variable,
    split_between_spouses=False,
):
    """
    Attribute a tax unit's amount to its members.

    Dependents keep their own person-level amounts, which a tax-unit amount
    describing the filer's return leaves out. The head and spouse get their
    own amounts when those sum to the tax unit's amount. When the tax-unit
    amount differs, as when it is an input or a reform changes its formula,
    the head's and spouse's own amounts are scaled to sum to it; if they have
    no own amounts, the head takes it, or with `split_between_spouses` the
    head and spouse take equal halves, which does not depend on which spouse
    is labelled head. With non-negative own amounts and a non-negative
    tax-unit amount, as for deductions, no share is negative. Every tax unit
    is assumed to have a head.
    """
    # The person-level projector returns tax-unit values for each member.
    tax_unit = person.tax_unit
    own = person(person_variable, period)
    filer = ~person("is_tax_unit_dependent", period)
    filers_own = tax_unit.sum(own * filer)
    amount = tax_unit(tax_unit_variable, period)
    # The tax-unit amount is stored in float32, so compare in its precision.
    matches = amount == filers_own.astype(amount.dtype)
    has_own = filers_own > 0
    scale = np.divide(
        amount,
        filers_own,
        out=np.zeros_like(filers_own, dtype=float),
        where=has_own,
    )
    is_head = person("is_tax_unit_head", period)
    if split_between_spouses:
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        takes_unattributed = head_or_spouse / max_(tax_unit.sum(head_or_spouse), 1)
    else:
        takes_unattributed = is_head
    reconciled = own * scale + takes_unattributed * where(has_own, 0, amount)
    filer_share = where(matches, own, reconciled)
    return where(filer, filer_share, own)


def sum_contained_tax_units(var, population, period):
    tax_unit = population.members.tax_unit.reference_entity
    values = tax_unit(var, period)
    is_head = population.members("is_tax_unit_head", period)
    person_level_values = tax_unit.project(values) * is_head
    return population.sum(person_level_values)


infinity = np.inf
select = np.select
where = np.where

PERCENT = "/1"


def variable_alias(name: str, variable_cls: type) -> type:
    """
    Copy a variable class and return a new class.
    """
    class_dict = dict(variable_cls.__dict__)
    class_dict["formula"] = lambda entity, period: entity(variable_cls.__name__, period)
    return type(
        name,
        variable_cls.__bases__,
        class_dict,
    )


def sum_among_non_dependents(variable: str) -> Callable:
    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum(variable, tax_unit, period)

    return formula


def spouse(person: Population, period: int, variable: str) -> ArrayLike:
    values = person(variable, period)
    return (person.marital_unit.sum(values) - values).astype(values.dtype)


def in_state(state):
    def is_eligible(population, period, parameters):
        return population("state_code_str", period) == state

    return is_eligible


def get_next_threshold(values: ArrayLike, thresholds: ArrayLike) -> ArrayLike:
    """
    Return the next threshold in the sequence of thresholds.
    """
    t = np.array(thresholds)
    return t[min_((t <= values.reshape((1, len(values))).T).sum(axis=1), len(t) - 1)]


def get_previous_threshold(values: ArrayLike, thresholds: ArrayLike) -> ArrayLike:
    """
    Return the previous threshold in the sequence of thresholds.
    """
    t = np.array(thresholds)
    return t[max_((t <= values.reshape((1, len(values))).T).sum(axis=1) - 1, 0)]
