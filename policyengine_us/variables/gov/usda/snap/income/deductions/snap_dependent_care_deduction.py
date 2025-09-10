from policyengine_us.model_api import *


class snap_dependent_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP dependent care deduction"
    unit = USD
    documentation = "Deduction from SNAP gross income for dependent care"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/uscode/text/7/2014#e_3"

    def formula(spm_unit, period, parameters):
        childcare = add(spm_unit, period, ["childcare_expenses"])
        # Per 273.11(c)(1), only eligible members' share of expenses count as deductions
        proration_factor = spm_unit("snap_deduction_proration_factor", period)
        return childcare * proration_factor
