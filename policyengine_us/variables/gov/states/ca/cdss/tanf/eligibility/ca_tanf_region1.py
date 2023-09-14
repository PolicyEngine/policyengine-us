from policyengine_us.model_api import *


class ca_tanf_region1(Variable):
    value_type = bool
    entity = SPMUnit
    label = "California CalWORKs Region 1"
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(spm_unit, period, parameters):
        county = spm_unit.household("county_str", period)
        region1 = parameters(period).gov.states.ca.cdss.tanf.region1
        return county in region1
