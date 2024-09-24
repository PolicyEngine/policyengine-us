from policyengine_core.model_api import *
from policyengine_us.entities import *
from policyengine_us.tools.branched_simulation import BranchedSimulation
from pathlib import Path
import pandas as pd
from policyengine_us.typing import Formula

USD = "currency-USD"


def tax_unit_non_dep_sum(var, tax_unit, period):
    return tax_unit.sum(
        tax_unit.members(var, period)
        * not_(tax_unit.members("is_tax_unit_dependent", period))
    )


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
    class_dict["formula"] = lambda entity, period: entity(
        variable_cls.__name__, period
    )
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
    return t[
        min_((t <= values.reshape((1, len(values))).T).sum(axis=1), len(t) - 1)
    ]


def get_previous_threshold(
    values: ArrayLike, thresholds: ArrayLike
) -> ArrayLike:
    """
    Return the previous threshold in the sequence of thresholds.
    """
    t = np.array(thresholds)
    return t[
        max_((t <= values.reshape((1, len(values))).T).sum(axis=1) - 1, 0)
    ]
