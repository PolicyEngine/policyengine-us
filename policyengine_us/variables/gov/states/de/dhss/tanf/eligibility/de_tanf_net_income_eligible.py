from policyengine_us.model_api import *


class de_tanf_net_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Delaware TANF net income eligible"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/delaware/16-Del-Admin-Code-SS-4000-4008"
    defined_for = StateCode.DE

    def formula(spm_unit, period, parameters):
        # Per State Plan Exhibits 1 & 2:
        # Applicants: $90 + childcare, compare to Payment Standard
        # Recipients: $90 + childcare + $30+1/3, compare to Standard of Need
        is_enrolled = spm_unit("is_tanf_enrolled", period)

        # Applicant net income: $90 + childcare only
        applicant_net_income = spm_unit("de_tanf_net_income", period)
        payment_standard = spm_unit("de_tanf_payment_standard", period)
        applicant_eligible = applicant_net_income <= payment_standard

        # Recipient countable income: $90 + $30 + 1/3 + childcare
        countable_income = spm_unit("de_tanf_countable_income", period)
        standard_of_need = spm_unit("de_tanf_standard_of_need", period)
        recipient_eligible = countable_income <= standard_of_need

        return where(is_enrolled, recipient_eligible, applicant_eligible)
