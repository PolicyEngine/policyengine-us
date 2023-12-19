from policyengine_us.model_api import *


class ca_tanf_financial_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "California CalWORKs Financial Eligibility"
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(spm_unit, period, parameters):
        tanf_enrolled = spm_unit("is_tanf_enrolled", period)
        applicant_test = spm_unit("ca_tanf_applicant_financial_test", period)
        recipient_test = spm_unit("ca_tanf_recipient_financial_test", period)

        return where(
            tanf_enrolled, recipient_test, applicant_test & recipient_test
        )
