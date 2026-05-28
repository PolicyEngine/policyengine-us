from policyengine_us.model_api import *


def sum_by_state(values, state):
    result = np.zeros_like(values, dtype=float)
    for state_code in np.unique(state):
        in_state = state == state_code
        result[in_state] = np.sum(values[in_state])
    return result
