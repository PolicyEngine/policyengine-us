from policyengine_us.model_api import *


class dc_tanf_countable_income_for_computing_benefits(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC TANF countable earned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        gross_earnings = spm_unit("dc_tanf_gross_earned_income", period)
        gross_unearnings = spm_unit(
            "dc_tanf_countable_gross_unearned_income", period
        )
        p = parameters(period).gov.states.dc.dhs.tanf.income.earned_deduction
        annual_flat_exclusion = p.flat * MONTHS_IN_YEAR
        return (
            max_(gross_earnings - annual_flat_exclusion, 0)
            * (1 - p.percentage)
            + gross_unearnings
        )
