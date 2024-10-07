from policyengine_core.periods import period as period_

def is_reform_active(parameter, period, years_to_check=5, condition_attr='in_effect'):
    """
    Check if a reform is active within the specified number of years.

    Args:
    parameter: The parameter object to check for activation.
    period: The starting period to check from.
    years_to_check: Number of years to check (default is 5).
    condition_attr: The attribute or method to check for activation (default is 'in_effect').

    Returns:
    bool: True if the reform is active within the specified years, False otherwise.
    """
    current_period = period_(period)
    
    for _ in range(years_to_check):
        param_value = parameter(current_period)
        if getattr(param_value, condition_attr, False):
            return True
        current_period = current_period.offset(1, "year")
    
    return False