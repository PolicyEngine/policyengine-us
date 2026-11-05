from policyengine_us.model_api import *


class sc_tanf_gross_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "South Carolina TANF gross income eligible"
    definition_period = MONTH
    defined_for = StateCode.SC
    reference = (
        "https://dss.sc.gov/media/bxwc1jdj/tanf-policy-manual-volume-67-final.pdf#page=133",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sc.tanf.income
        need_standard = spm_unit("sc_tanf_need_standard", period)
        # The Section 8.15 table notes: "multiply the Need Standard by 1.85
        # and drop the cents".
        gross_income_limit = np.floor(need_standard * p.gross_income_limit)
        gross_income = spm_unit("sc_tanf_gross_income", period)
        return gross_income <= gross_income_limit
