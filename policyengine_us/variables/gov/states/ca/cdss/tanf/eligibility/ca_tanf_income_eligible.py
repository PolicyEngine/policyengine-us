from policyengine_us.model_api import *


class ca_tanf_income_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "California CalWORKs Applicant Financial Eligibility"
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(spm_unit, period, parameters):
        countable_income_applicant = spm_unit(
            "ca_tanf_countable_income_applicant", period
        )
        countable_income_recipient = spm_unit(
            "ca_tanf_countable_income_recipient", period
        )
        income_limit = spm_unit("ca_tanf_income_limit", period)
        maximum_payment = spm_unit("ca_tanf_maximum_payment", period)

        return (countable_income_applicant <= income_limit) & (
            countable_income_recipient <= maximum_payment
        )
