from policyengine_core.periods import period as period_

def create_reform_if_active(parameters, period, parameter_path: str, active_parameter_path: str, reform_function, bypass: bool = False) -> bool:
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
    path_parts = parameter_path.split(".")
    
    p = parameters
    for part in path_parts:
        p = getattr(p, part)
    
    for _ in range(5):
        if getattr(p(current_period), active_parameter_path):
            return reform_function()
        current_period = current_period.offset(1, "year")
    
    return None
