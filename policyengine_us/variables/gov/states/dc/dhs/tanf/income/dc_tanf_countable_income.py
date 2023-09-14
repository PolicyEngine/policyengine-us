from policyengine_us.model_api import *


class dc_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC TANF countable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        gross_earnings = spm_unit("dc_tanf_gross_earned_income", period)
        gross_unearned_income = spm_unit(
            "dc_tanf_countable_gross_unearned_income", period
        )
        p = parameters(period).gov.states.dc.dhs.tanf.income.deductions.earned
        annual_flat_exclusion = p.flat * MONTHS_IN_YEAR
        earnings_after_deduction = max_(
            gross_earnings - annual_flat_exclusion, 0
        ) * (1 - p.percentage)
        return earnings_after_deduction + gross_unearned_income
