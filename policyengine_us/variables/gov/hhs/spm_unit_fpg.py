from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class spm_unit_fpg(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit's federal poverty guideline"
    definition_period = YEAR
    unit = USD

    def formula(spm_unit, period, parameters):
        n = spm_unit("spm_unit_size", period)
        state_group = spm_unit.household("state_group_str", period)
        return fpg(n, state_group, period, parameters)
