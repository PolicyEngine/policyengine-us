from policyengine_us.model_api import *


class is_western_region(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Is in a western region under the Chapter 7 Bankruptcy means test"
    definition_period = YEAR
    reference = "https://www.irs.gov/businesses/small-businesses-self-employed/local-standards-transportation"

    def formula(spm_unit, period, parameters):
        state_code = spm_unit.household("state_code", period).decode_to_str()

        p = parameters(period).household.state_group

        return np.isin(state_code, p.west)
