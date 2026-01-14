from policyengine_core.periods import period as period_
import numpy as np
import operator


def get_nested_value(base_param, path):
    value = base_param
    for part in path.split("."):
        value = getattr(value, part)
    return value


def create_reform_if_active(
    parameters,
    period,
    parameter_path: str,
    active_parameter_path: str,
    reform_function,
    bypass: bool = False,
) -> bool:
    """
    Check if a reform parameter is active in any of the next 5 years.

    Args:
        parameters: PolicyEngine parameters object
        period: Current period
        parameter_path: Full path to the parameter to check
        active_parameter_path: Full path to the active parameter
        years: Number of years to check into the future
    Returns:
        Reform: The reform function if the parameter is active, otherwise None
    """
    if bypass:
        return reform_function()

    current_period = period_(period)
    p = get_nested_value(parameters, parameter_path)

    for _ in range(5):
        if getattr(p(current_period), active_parameter_path):
            return reform_function()
        current_period = current_period.offset(1, "year")

    return None


def create_reform_threshold_check(
    parameters,
    period,
    parameter_path: str,
    comparison_parameter_path: str,
    reform_function,
    threshold_check: float = np.inf,
    comparison_operator=operator.lt,
    bypass: bool = False,
):
    """
    Create a reform based on a parameter threshold check.

    Args:
        parameters: PolicyEngine parameters object
        period: Time period for the reform
        parameter_path: Dot-separated path to the parameter to check
        comparison_parameter_path: Dot-separated path to the parameter to compare with threshold
        reform_function: The specific reform creation function to call
        bypass: If True, skip parameter checks and return reform
        threshold_check: Value to compare parameter against
        comparison_operator: Operator to use for comparison (default: less than)
    """
    if bypass:
        return reform_function()

    # Navigate parameter tree using the path
    p = get_nested_value(parameters, parameter_path)
    current_period = period_(period)

    for _ in range(5):
        if comparison_operator(
            getattr(p(current_period), comparison_parameter_path),
            threshold_check,
        ):
            return reform_function()
        current_period = current_period.offset(1, "year")

    return None


def create_reform_two_threshold_check(
    parameters,
    period,
    parameter_path: str,
    reform_function,
    comparison_parameter_path_1: str,
    comparison_parameter_path_2: str,
    threshold_check_1: float = np.inf,
    threshold_check_2: float = np.inf,
    comparison_operator_1=operator.lt,
    comparison_operator_2=operator.lt,
    bypass: bool = False,
):
    """
    Create a reform based on a parameter two-threshold check.

    Args:
        parameters: PolicyEngine parameters object
        period: Time period for the reform
        parameter_path: Dot-separated path to the parameter to check
        reform_function: The specific reform creation function to call
        comparison_parameter_path_1: Dot-separated path to the parameter to compare with threshold 1
        comparison_parameter_path_2: Dot-separated path to the parameter to compare with threshold 2
        threshold_check_1: Value to compare parameter against threshold 1
        threshold_check_2: Value to compare parameter against threshold 2
        comparison_operator_1: Operator to use for comparison (default: less than)
        comparison_operator_2: Operator to use for comparison (default: less than)
        bypass: If True, skip parameter checks and return reform
    """
    if bypass:
        return reform_function()

    # Navigate parameter tree using the path
    p = get_nested_value(parameters, parameter_path)
    current_period = period_(period)

    for _ in range(5):
        param_at_period = p(current_period)
        value1 = get_nested_value(param_at_period, comparison_parameter_path_1)
        value2 = get_nested_value(param_at_period, comparison_parameter_path_2)

        if comparison_operator_1(
            value1, threshold_check_1
        ) or comparison_operator_2(value2, threshold_check_2):
            return reform_function()
        current_period = current_period.offset(1, "year")

    return None
