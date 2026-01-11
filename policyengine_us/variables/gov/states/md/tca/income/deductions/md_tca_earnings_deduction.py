from policyengine_us.model_api import *


class md_tca_earnings_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TCA earnings deduction"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MD
    reference = "https://dsd.maryland.gov/regulations/Pages/07.03.03.13.aspx"

    def formula(spm_unit, period, parameters):
        # NOTE: Maryland applies different deduction rates for self-employment (50%)
        # vs regular employment. We apply the employment rate to all earned
        # income as a simplification.
        p = parameters(period).gov.states.md.tca.income.deductions.earned
        earned_income = add(spm_unit, period, ["tanf_gross_earned_income"])
        is_enrolled = spm_unit("is_tanf_enrolled", period)
        # 20% for new applicants, 40% for enrolled recipients
        rate = where(is_enrolled, p.not_self_employed, p.new)
        return earned_income * rate
