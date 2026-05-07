from policyengine_us.model_api import *


class md_tca_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TCA countable earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MD
    reference = "https://dsd.maryland.gov/regulations/Pages/07.03.03.13.aspx"

    def formula(spm_unit, period, parameters):
        # NOTE: Maryland applies different deduction rates for self-employment (50%)
        # vs regular employment. We apply the employment rate to all earned
        # income as a simplification.
        p = parameters(period).gov.states.md.tca.income.deductions.earned
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        is_enrolled = spm_unit("is_tanf_enrolled", period)
        # 20% disregard for applicants, 40% disregard for enrolled recipients
        rate = where(is_enrolled, p.recipient, p.applicant)
        after_disregard = gross_earned * (1 - rate)
        childcare_deduction = spm_unit("md_tca_childcare_deduction", period)
        return max_(after_disregard - childcare_deduction, 0)
