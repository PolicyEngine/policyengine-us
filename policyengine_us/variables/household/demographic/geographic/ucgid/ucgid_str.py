from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.geographic.ucgid.ucgid_enum import (
    UCGID,
)


class ucgid_str(Variable):
    value_type = str
    entity = Household
    label = "UCGID (string)"
    documentation = "UCGID variable, stored as a string"
    definition_period = YEAR

    def formula(household, period, parameters):
        import numpy as np

        ucgid_enum_names = household("ucgid", period).decode_to_str()

        # Convert each enum name to its hierarchical codes
        result = []
        for enum_name in ucgid_enum_names:
            # Get the enum instance from its name
            ucgid_enum = UCGID[enum_name]

            # Get all hierarchical codes and join with commas
            hierarchical_codes = ucgid_enum.get_hierarchical_codes()
            result.append(",".join(hierarchical_codes))

        return np.array(result)
