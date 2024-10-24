from policyengine_core.periods import period as period_


def create_reform_if_active(
    parameters, period, parameter_path, reform_function, bypass: bool = False
):
    """
    Check if a reform's parameter is truthy in any of the next five years and create the reform if so.

    Args:
    parameters: The parameters object from the reform function.
    period: The current period.
    parameter_path: A string representing the path to the relevant parameter.
    reform_function: A function that creates and returns the reform.
    bypass: If True, always return the reform regardless of the parameter value.

    Returns:
    Reform or None: The reform if the parameter is truthy or bypassed, None otherwise.
    """

    def create_reform():
        if "parameters" in reform_function.__code__.co_varnames:
            return reform_function(parameters, period)
        else:
            return reform_function()

    if bypass:
        return create_reform()

    current_period = period_(period)

    for _ in range(5):
        if parameters(current_period).get_descendants(parameter_path):
            return create_reform()
        current_period = current_period.offset(1, "year")

    return None
