from policyengine_us.model_api import *


class sc_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "South Carolina TANF income eligible"
    definition_period = MONTH
    defined_for = StateCode.SC
    # PDF pages 133-134
    reference = "https://dss.sc.gov/media/bxwc1jdj/tanf-policy-manual-volume-67-final.pdf#page=133"

    def formula(spm_unit, period, parameters):
        gross_income_eligible = spm_unit("sc_tanf_gross_income_eligible", period)
        countable_income_eligible = spm_unit(
            "sc_tanf_countable_income_eligible", period
        )
        return gross_income_eligible & countable_income_eligible
