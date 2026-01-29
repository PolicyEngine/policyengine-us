from policyengine_us.model_api import *


class sc_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "South Carolina TANF income eligible"
    definition_period = MONTH
    defined_for = StateCode.SC
    reference = "https://dss.sc.gov/media/ojqddxsk/tanf-policy-manual-volume-65.pdf#page=131"

    def formula(spm_unit, period, parameters):
        gross_income_eligible = spm_unit(
            "sc_tanf_gross_income_eligible", period
        )
        countable_income_eligible = spm_unit(
            "sc_tanf_countable_income_eligible", period
        )
        return gross_income_eligible & countable_income_eligible
