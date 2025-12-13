from policyengine_us.model_api import *


class StateGroup(Enum):
    CONTIGUOUS_US = "Contiguous US"
    AK = "Alaska"
    HI = "Hawaii"
    GU = "Guam"
    PR = "Puerto Rico"
    VI = "Virgin Islands"
    # Omit other territories for now.


class state_group(Variable):
    value_type = Enum
    possible_values = StateGroup
    default_value = StateGroup.CONTIGUOUS_US
    entity = Household
    label = "State group"
    definition_period = YEAR

    def formula(household, period, parameters):
        NON_CONTIGUOUS_STATES = ("AK", "HI", "GU", "PR", "VI")
        state_code = household("state_code", period).decode_to_str()
        is_non_contiguous = np.isin(state_code, NON_CONTIGUOUS_STATES)
        encoded = np.empty(state_code.shape, dtype=object)
        encoded[:] = StateGroup.CONTIGUOUS_US
        if is_non_contiguous.any():
            encoded[is_non_contiguous] = StateGroup.encode(
                state_code[is_non_contiguous]
            ).decode()
        return encoded
