from policyengine_us.model_api import *


class snap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Final SNAP benefit amount, equal to net income minus food contribution"
    label = "SNAP allotment"
    reference = "https://www.law.cornell.edu/uscode/text/7/2017#a"
    unit = USD

    def formula(spm_unit, period, parameters):
        emergency_allotment_months = spm_unit(
            "snap_emergency_allotment_monthly", period, options=[ADD]
        )
        normal_allotment = spm_unit("snap_normal_allotment", period)
        return normal_allotment + emergency_allotment_months
