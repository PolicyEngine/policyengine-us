from policyengine_us.model_api import *


class is_west_region(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Is in West region"
    definition_period = YEAR
    reference = "https://www.irs.gov/businesses/small-businesses-self-employed/local-standards-transportation"

    def formula(spm_unit, period, parameters):
        state_code = spm_unit.household("state_code_str", period)

        p = parameters(
            period
        ).gov.bankruptcy.local_standards.vehicle_operation.state_group

        return np.isin(state_code, p.west)
