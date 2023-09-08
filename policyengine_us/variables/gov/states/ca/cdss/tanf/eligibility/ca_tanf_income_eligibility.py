from policyengine_us.model_api import *


class ca_tanf_income_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "California CalWORKs Applicant Financial Eligibility"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(spm_unit, period, parameters):
        countable_income = spm_unit(
            "ca_tanf_countable_income_applicant", period
        )
        limit = spm_unit("ca_tanf_income_limit", period)
        return countable_income <= limit
