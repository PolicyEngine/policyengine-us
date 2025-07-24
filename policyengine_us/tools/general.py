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


def select_filing_status_value(
    filing_status: ArrayLike,
    filing_status_values: dict,
    input_value: ArrayLike = None,
    **kwargs,
) -> ArrayLike:
    """
    Select a value based on filing status, with SINGLE as the default.

    This is a common pattern for selecting parameter values based on filing status.
    According to IRS SOI data, SINGLE is the most common filing status.

    Args:
        filing_status: Array of filing status enum values
        filing_status_values: Dict mapping filing status to values or functions
        input_value: Optional input value to pass to functions (e.g., taxable income)

    Returns:
        Array of selected values based on filing status

    Example:
        # For parameter values
        result = select_filing_status_value(
            filing_status,
            parameters.amount
        )

        # For calculated values (e.g., tax brackets)
        result = select_filing_status_value(
            filing_status,
            parameters.rates,
            taxable_income
        )
    """
    statuses = filing_status.possible_values

    # Helper function to get value
    def get_value(fs_value):
        if input_value is not None and hasattr(fs_value, "calc"):
            # It's a rate schedule or similar
            return fs_value.calc(input_value, **kwargs)
        elif hasattr(fs_value, "__call__"):
            # It's a callable
            return (
                fs_value(input_value, **kwargs)
                if input_value is not None
                else fs_value(**kwargs)
            )
        else:
            # It's a simple value
            return fs_value

    # Build conditions and values, excluding SINGLE
    conditions = []
    values = []

    # Check each filing status except SINGLE
    for status_name in [
        "JOINT",
        "SEPARATE",
        "HEAD_OF_HOUSEHOLD",
        "SURVIVING_SPOUSE",
    ]:
        # Check if this enum value exists in this filing status enum
        if hasattr(statuses, status_name):
            status_enum = getattr(statuses, status_name)
            if status_enum.name.lower() in filing_status_values:
                conditions.append(filing_status == status_enum)
                values.append(
                    get_value(filing_status_values[status_enum.name.lower()])
                )

    # SINGLE is the default
    default_value = get_value(filing_status_values["single"])

    return select(conditions, values, default=default_value)
