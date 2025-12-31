from policyengine_us.model_api import *


class de_tanf_net_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Delaware TANF net income eligible"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/delaware/"
        "16-Del-Admin-Code-SS-4000-4008"
    )
    defined_for = StateCode.DE

    def formula(spm_unit, period, parameters):
        # Per DSSM 4008: Applicants compare net income to Payment Standard
        # NOTE: PolicyEngine cannot track benefit history, so we use
        # applicant standard (more restrictive)
        payment_standard = spm_unit("de_tanf_payment_standard", period)
        net_income = spm_unit("de_tanf_countable_net_income", period)

        return net_income <= payment_standard
