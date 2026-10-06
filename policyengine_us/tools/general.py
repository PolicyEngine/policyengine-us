from policyengine_core.model_api import *
from policyengine_us.entities import *
from policyengine_us.tools.branched_simulation import BranchedSimulation
from policyengine_us.tools.period_branch import get_branch_for_period
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
    are not tax unit dependents, whose items belong on their own returns. A
    tax-unit-level variable is added as is, so it must already describe the
    filer's own return. Person-level variables named in `include_dependents`
    are summed over every member: they are the filer's amounts even when
    recorded on a dependent. Variables are added in the order given.
    """
    total = 0
    for variable in variables:
        variable_entity = tax_unit.entity.get_variable(
            variable, check_existence=True
        ).entity
        if not variable_entity.is_person:
            total = total + tax_unit(variable, period)
        elif variable in include_dependents:
            total = total + tax_unit.sum(tax_unit.members(variable, period))
        else:
            total = total + tax_unit_non_dep_sum(variable, tax_unit, period)
    return total


def person_share_of_tax_unit_amount(person, period, tax_unit_variable, person_variable):
    """
    Attribute a tax unit's amount to its members.

    Each member gets their own person-level amount. Any difference between
    the tax unit's amount and its head's and spouse's own amounts, as when the
    tax-unit variable is an input or a reform changes its formula, goes to
    the head. Dependents keep their own amounts, which a tax-unit amount that
    describes the filer's return leaves out.
    """
    own = person(person_variable, period)
    not_dependent = ~person("is_tax_unit_dependent", period)
    filers_own = person.tax_unit.sum(own * not_dependent)
    residual = person.tax_unit(tax_unit_variable, period) - filers_own
    return own + person("is_tax_unit_head", period) * residual


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
