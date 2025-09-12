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
        childcare_expenses = spm_unit("childcare_expenses", period)
        # Exclude ineligible members' share per SNAP proration rules (result always >= 0 since prorate_fraction < spm_unit_size)
        prorate_fraction = spm_unit("snap_prorate_fraction", period.this_year)
        spm_unit_size = spm_unit("spm_unit_size", period)
        return childcare_expenses * (1 - prorate_fraction / spm_unit_size)
