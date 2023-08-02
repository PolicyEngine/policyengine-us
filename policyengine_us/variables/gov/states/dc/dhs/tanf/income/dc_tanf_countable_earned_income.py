from policyengine_us.model_api import *


class dc_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC TANF countable earned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        gross_earnings = spm_unit("dc_tanf_gross_earned_income", period)
        p = parameters(period).gov.states.dc.dhs.tanf.income.deductions.earned
        enrolled = spm_unit("is_tanf_enrolled", period)
        annual_flat_exclusion = p.flat * MONTHS_IN_YEAR
        earnings_after_flat_exclusion = max_(
            gross_earnings - annual_flat_exclusion, 0
        )
        return where(
            enrolled,
            # For enrolled recipients, DC applies a flat and a percent deduction.
            earnings_after_flat_exclusion * (1 - p.percentage),
            # For new applicants, DC applies only a flat deduction.
            earnings_after_flat_exclusion,
        )
