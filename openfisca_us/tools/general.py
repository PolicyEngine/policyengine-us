from openfisca_core.model_api import *
from openfisca_us.entities import *
import numpy as np

USD = "currency-USD"


def add(entity, period, *variables):
    return sum([entity(var, period) for var in variables])


def aggr(entity, period, *variables):
    return entity.sum(add(entity, period, *variables))


def amount_between(x, lower, upper):
    return max_(min_(x, upper), lower) - lower


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


def variable_alias(name: str, variable_cls: type) -> type:
    """
    Copy a variable class and return a new class.
    """
    return type(name, variable_cls.__bases__, dict(variable_cls.__dict__))
