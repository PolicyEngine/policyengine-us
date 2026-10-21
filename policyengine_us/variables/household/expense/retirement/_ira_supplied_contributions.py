from policyengine_us.model_api import *

IRA_CONTRIBUTION_VARIABLES = (
    "traditional_ira_contributions",
    "roth_ira_contributions",
)


def _is_supplied(simulation, name, period):
    """Whether the caller set ``name`` for ``period`` as an input.

    Inputs given when the simulation is built are listed in
    ``simulation.input_variables``. Core records later ``set_input`` calls in
    ``_user_input_keys`` by variable, branch and period. Neither lists a value
    that a formula calculated.
    """
    if name in simulation.input_variables:
        return True
    keys = getattr(simulation, "_user_input_keys", None) or ()
    if hasattr(simulation, "_get_visible_branch_names"):
        branches = set(simulation._get_visible_branch_names())
    else:
        branches = {getattr(simulation, "branch_name", "default"), "default"}
    return any(
        variable == name and branch in branches and set_period == period
        for variable, branch, set_period in keys
    )


def supplied_ira_contributions(person, period):
    """Actual IRA contributions the caller supplied as inputs, by variable.

    Both variables are derived from ``ira_contribution_limit`` through
    ``ira_contribution_scale``, so neither can be calculated while the limit
    or the scale is being calculated. This reads only values the caller set
    as inputs, at construction or later through ``set_input``, and never runs
    a formula, so a value another formula calculated is never mistaken for a
    supplied one. A variable that is not supplied for the period maps to
    ``None``. Core stores an input for every person once any person sets it,
    so a supplied variable replaces its formula for the whole population.
    """
    simulation = person.simulation
    supplied = {}
    for name in IRA_CONTRIBUTION_VARIABLES:
        array = None
        if _is_supplied(simulation, name, period):
            array = simulation.get_array(name, period)
        supplied[name] = array
    return supplied


def traditional_ira_contributions_without_spousal_rule(person, period, own_limit):
    """Traditional IRA contributions under a limit that ignores the spousal rule.

    Supplied traditional contributions are returned as given (floored at
    zero). Otherwise desired traditional contributions are scaled, as
    ``ira_contribution_scale`` does, to fit what the limit leaves after any
    supplied Roth contributions, sharing it with desired Roth contributions in
    proportion. This matches ``traditional_ira_contributions`` for anyone the
    IRC 219(c) spousal rule cannot reach, such as a tax unit dependent, without
    reading the tax unit's filing status.
    """
    supplied = supplied_ira_contributions(person, period)
    supplied_traditional = supplied["traditional_ira_contributions"]
    if supplied_traditional is not None:
        return max_(supplied_traditional, 0)
    desired_traditional = person("traditional_ira_contributions_desired", period)
    supplied_roth = supplied["roth_ira_contributions"]
    if supplied_roth is None:
        generated_desired = desired_traditional + person(
            "roth_ira_contributions_desired", period
        )
        available = own_limit
    else:
        generated_desired = desired_traditional
        available = max_(own_limit - max_(supplied_roth, 0), 0)
    denominator = where(generated_desired > 0, generated_desired, 1)
    return desired_traditional * min_(available / denominator, 1)
