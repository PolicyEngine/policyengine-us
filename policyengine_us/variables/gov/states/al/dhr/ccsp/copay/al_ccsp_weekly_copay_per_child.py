from policyengine_us.model_api import *


class al_ccsp_weekly_copay_per_child(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Alabama CCSP weekly per-child parental fee"
    definition_period = MONTH
    defined_for = StateCode.AL
    reference = "https://dhr.alabama.gov/wp-content/uploads/2024/01/Child-Care-Fact-Sheet-2024.pdf"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.al.dhr.ccsp.copay
        # Floor income at 0 so self-employment / farm losses land in the
        # $0 copay band rather than producing a negative FPL ratio.
        monthly_income = max_(spm_unit("al_ccsp_countable_income", period), 0)
        # Use the prior calendar year's HHS poverty guidelines to match
        # Alabama's Child Care Fact Sheet operational thresholds.
        monthly_fpg = spm_unit("spm_unit_fpg", period.last_year) / MONTHS_IN_YEAR
        fpl_ratio = where(monthly_fpg > 0, monthly_income / monthly_fpg, 0)
        fee = p.fee_by_fpl.calc(fpl_ratio)
        copay_waived = spm_unit("al_ccsp_copay_waived", period)
        return where(copay_waived, 0, fee)
