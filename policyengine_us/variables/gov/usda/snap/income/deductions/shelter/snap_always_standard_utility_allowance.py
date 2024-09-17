from policyengine_us.model_api import *


class snap_always_standard_utility_allowance(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Always use the standard utility allowance"

    def formula(spm_unit, period, parameters):
        state = spm_unit.household("state_code", period)
        p = parameters(period).gov.usda.snap.income.deductions.utility

        return p.always_standard[state]
