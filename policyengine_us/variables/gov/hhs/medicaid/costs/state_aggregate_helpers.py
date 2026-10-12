"""Helper functions for aggregating person-level values by state.

This module provides shared state-aggregation logic used by:
- medicaid_slcsp_state_average_cost_index (state-average cost index)
- medicaid_slcsp_state_denominator (state allocation denominator)
"""

from policyengine_us.model_api import *


def sum_by_state(values, state):
    """Broadcast each person to the total of ``values`` within their state.

    Args:
        values: Person-level array to sum within each state.
        state: Person-level array of state codes, same length as ``values``.

    Returns:
        Array the same shape as ``values`` where each person holds the sum of
        ``values`` over everyone sharing their state code.
    """
    result = np.zeros_like(values, dtype=float)
    for state_code in np.unique(state):
        in_state = state == state_code
        result[in_state] = np.sum(values[in_state])
    return result
