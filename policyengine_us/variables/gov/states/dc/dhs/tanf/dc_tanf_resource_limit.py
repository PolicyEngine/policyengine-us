from policyengine_us.model_api import *


class dc_tanf_resource_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC TANF resource limit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.dc.dhs.tanf.eligibility.resource_limit
        # Check if the household includes a person is age 60 or older.
        if_age_over_60 = spm_unit.members("age", period) >= 60
        # Look up resource limit by the condition.
        resource_limit = p.main.calc(spm_unit.sum(if_age_over_60))
        return resource_limit
