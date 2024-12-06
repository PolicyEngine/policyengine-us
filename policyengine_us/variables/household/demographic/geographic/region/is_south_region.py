from policyengine_us.model_api import *


class is_south_region(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Is in South region"
    definition_period = YEAR
    reference = "https://www.irs.gov/businesses/small-businesses-self-employed/local-standards-transportation"

    def formula(spm_unit, period, parameters):
        state = spm_unit.household("state_code", period)

        p = parameters(
            period
        ).gov.bankruptcy.local_standards.vehicle_operation.state_group

        return np.isin(state, p.south)
