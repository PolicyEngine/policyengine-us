from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_tools.model_api import *
import numpy as np

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


def taxcalc_read_only_variable(name: str, variable_cls: type) -> type:
    """
    Copy a variable class and return a new class for a tax-calc variable.
    """
    class_dict = dict(variable_cls.__dict__)
    class_dict["formula"] = lambda entity, period: entity(
        variable_cls.__name__, period
    )
    return type(
        name,
        (Variable,),
        dict(
            value_type=variable_cls.value_type,
            entity=variable_cls.entity,
            label=variable_cls.label + " (Tax-Calculator)",
            definition_period=variable_cls.definition_period,
            unit=variable_cls.unit,
            documentation=variable_cls.documentation
            + " This is a read-only copy variable, matching the corresponding variable in the open-source US federal tax model Tax-Calculator.",
        ),
    )


def sum_among_non_dependents(variable: str) -> Callable:
    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum(variable, tax_unit, period)

    return formula
