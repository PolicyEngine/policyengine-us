from policyengine_us.model_api import *


class ut_claims_retirement_credit(Variable):
    value_type = bool
    entity = TaxUnit
    label = "claims the Utah retirement credit"
    unit = USD
    documentation = "Utah residents can claim only one of the retirement credit or the social security benefits credit. We assume they claim the one with higher value."
    definition_period = YEAR
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        max_retirement_credit = tax_unit("ut_retirement_credit_max", period)
        max_ss_benefits_credit = tax_unit("ut_ss_benefits_credit_max", period)
        return max_retirement_credit >= max_ss_benefits_credit
