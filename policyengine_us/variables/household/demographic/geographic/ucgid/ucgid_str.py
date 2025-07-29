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

        # Get the UCGID enum values for each household
        ucgid_values = household("ucgid", period)

        # Convert enum values to their string code representations
        # ucgid_values contains UCGID enum instances
        result = []
        for ucgid_value in ucgid_values:
            if isinstance(ucgid_value, UCGID):
                # Get the string value (e.g., "0100000US", "0400000US06", etc.)
                result.append(ucgid_value.value)
            else:
                # Fallback to US if something unexpected happens
                result.append(UCGID.US.value)

        return np.array(result)
