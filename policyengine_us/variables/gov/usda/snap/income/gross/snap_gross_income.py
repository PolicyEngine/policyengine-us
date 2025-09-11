from policyengine_us.model_api import *


class snap_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "SNAP gross income"
    documentation = "Gross income for calculating SNAP eligibility"
    reference = "https://www.law.cornell.edu/cfr/text/7/273.11#c"
    unit = USD

    def formula(spm_unit, period, parameters):
        gross_income_pre_prorated = spm_unit(
            "snap_gross_income_pre_proration", period
        )
        proration_factor = spm_unit("snap_proration_factor", period)
        return gross_income_pre_prorated * proration_factor
