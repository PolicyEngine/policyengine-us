from policyengine_us.model_api import *


class sc_tanf_gross_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "South Carolina TANF gross income eligible"
    definition_period = MONTH
    defined_for = StateCode.SC
    reference = (
        "https://www.scstatehouse.gov/coderegs/Chapter%20114.pdf#page=217",
        "https://dss.sc.gov/media/bxwc1jdj/tanf-policy-manual-volume-67-final.pdf#page=133",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sc.tanf.income
        need_standard = spm_unit("sc_tanf_need_standard", period)
        # 114-1150(A): gross income "must not exceed 185 percent of the need
        # standard by family size". 114-1140(A)(4) rounds only the standard
        # of need and the payment amount, so the limit keeps its cents.
        gross_income_limit = need_standard * p.gross_income_limit
        gross_income = spm_unit("sc_tanf_gross_income", period)
        return gross_income <= gross_income_limit
